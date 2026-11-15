import logging
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from app.models import Country, Indicator, Observation, ImportLog, Source

logger = logging.getLogger(__name__)

def upsert_countries(session: Session, df_countries) -> int:
    if df_countries.empty:
        return 0
    records = df_countries.to_dict(orient="records")
    for r in records:
        stmt = insert(Country).values(**r)
        stmt = stmt.on_conflict_do_update(
            index_elements=["country_code"],
            set_={
                "name": stmt.excluded.name,
                "region": stmt.excluded.region,
                "income_group": stmt.excluded.income_group,
            },
        )
        session.execute(stmt)
    session.commit()
    return len(records)

def get_or_create_source(session: Session, name: str, description: str = None, base_url: str = None) -> int:
    src = session.query(Source).filter_by(name=name).first()
    if not src:
        src = Source(name=name, description=description, base_url=base_url)
        session.add(src)
        session.commit()
        session.refresh(src)
    return src.source_id

def get_or_create_indicator(session: Session, code: str, name: str, unit: str, source_id: int) -> int:
    ind = session.query(Indicator).filter_by(code=code).first()
    if not ind:
        ind = Indicator(code=code, name=name, unit=unit, source_id=source_id)
        session.add(ind)
        session.commit()
        session.refresh(ind)
    return ind.indicator_id

def upsert_observations(session: Session, df_obs, indicator_id: int, chunk_size: int = 500) -> int:
    if df_obs.empty:
        return 0
    
    total_loaded = 0
    
    for _, row in df_obs.iterrows():
        c_code = row.get("country_iso3") if "country_iso3" in row else row.get("country_code")
        if not c_code:
            continue
            
        values = {
            "country_code": c_code,
            "indicator_id": indicator_id,
            "year": int(row["year"]),
            "sex": row.get("sex", "BTSX"),
            "value": row["value"],
            "is_outlier": bool(row.get("is_outlier", False))
        }

        stmt = insert(Observation).values(**values)
        # Folosim exact numele constrângerii din baza de date
        stmt = stmt.on_conflict_do_update(
            constraint="unique_country_indicator_year",
            set_={
                "value": stmt.excluded.value,
                "is_outlier": stmt.excluded.is_outlier,
                "created_at": func.now()
            }
        )
        session.execute(stmt)
        total_loaded += 1

    session.commit()
    return total_loaded

def log_import(session: Session, source_name: str, status: str, records_imported: int, error_message: str = None):
    log_entry = ImportLog(
        source_name=source_name,
        status=status,
        records_imported=records_imported,
        error_message=error_message
    )
    session.add(log_entry)
    session.commit()