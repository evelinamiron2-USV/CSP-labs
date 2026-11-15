from app.database import SessionLocal
from app.models import Country
from etl.extract_who import download_who_indicator
from etl.transform_who import transform_who_file
from etl.clean import clean_observations
from etl.load import get_or_create_source, get_or_create_indicator, upsert_observations, log_import

def run():
    session = SessionLocal()
    try:
        print("--- Importing WHO Data ---")
        valid_iso3 = set(r[0] for r in session.query(Country.country_code).all())
        source_id = get_or_create_source(session, "WHO", "World Health Organization GHO", "https://www.who.int/data/gho")
        
        code, name, unit = "WHOSIS_000001", "Life expectancy at birth (years)", "years"
        path, _ = download_who_indicator(code)
        raw = transform_who_file(path, code)
        cleaned = clean_observations(raw, valid_iso3)
        ind_id = get_or_create_indicator(session, code, name, unit, source_id)
        loaded = upsert_observations(session, cleaned, ind_id)
        log_import(session, "WHO", "SUCCESS", loaded)
        print(f"WHO [{code}] -> Încărcate: {loaded} rânduri în PostgreSQL")
    except Exception as e:
        session.rollback()
        print(f"Eroare la import WHO: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    run()