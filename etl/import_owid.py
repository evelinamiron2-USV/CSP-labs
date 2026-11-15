import logging
from app.database import SessionLocal
from app.models import Country
from etl.extract_owid import download_owid_chart
from etl.transform_owid import transform_owid_file
from etl.clean import clean_observations
from etl.load import get_or_create_source, get_or_create_indicator, upsert_observations, log_import

def run():
    session = SessionLocal()
    try:
        print("--- Importing Our World in Data ---")
        valid_iso3 = set(r[0] for r in session.query(Country.country_code).all())
        if not valid_iso3:
            print("Rulează mai întâi importul World Bank pentru a popula țările!")
            return

        source_id = get_or_create_source(session, "OWID", "Our World in Data", "https://ourworldindata.org")
        
        slug, code, name, unit = "life-expectancy", "OWID_LE", "Life Expectancy (OWID)", "years"
        path, _ = download_owid_chart(slug)
        raw = transform_owid_file(path, code)
        cleaned = clean_observations(raw, valid_iso3)
        ind_id = get_or_create_indicator(session, code, name, unit, source_id)
        loaded = upsert_observations(session, cleaned, ind_id)
        log_import(session, "OWID", "SUCCESS", loaded)
        print(f"OWID [{code}] -> Încărcate: {loaded} rânduri în PostgreSQL")
    except Exception as e:
        session.rollback()
        print(f"Eroare la import OWID: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    run()