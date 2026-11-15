import logging
from app.database import SessionLocal
from etl.extract_worldbank import download_worldbank_countries, download_worldbank_indicator
from etl.transform_worldbank import transform_worldbank_countries, transform_worldbank_file
from etl.clean import clean_observations
from etl.load import get_or_create_source, get_or_create_indicator, upsert_countries, upsert_observations, log_import

INDICATORS = [
    ("SH.XPD.CHEX.GD.ZS", "Current health expenditure (% of GDP)", "%"),
    ("SH.IMM.MEAS", "Immunization, measles (% of children)", "%"),
    ("SP.DYN.IMRT.IN", "Mortality rate, infant (per 1,000)", "per 1,000"),
    ("NY.GDP.PCAP.CD", "GDP per capita (current US$)", "USD")
]

def run():
    session = SessionLocal()
    try:
        print("--- Importing World Bank Data ---")
        c_path, _ = download_worldbank_countries()
        df_c = transform_worldbank_countries(c_path)
        upsert_countries(session, df_c)
        valid_iso3 = set(df_c["country_code"].dropna())

        source_id = get_or_create_source(session, "World Bank", "World Bank Open Data", "https://data.worldbank.org")

        for code, name, unit in INDICATORS:
            path, _ = download_worldbank_indicator(code)
            raw = transform_worldbank_file(path, code)
            cleaned = clean_observations(raw, valid_iso3)
            ind_id = get_or_create_indicator(session, code, name, unit, source_id)
            loaded = upsert_observations(session, cleaned, ind_id)
            log_import(session, "World Bank", "SUCCESS", loaded)
            print(f"World Bank [{code}] -> Încurcate: {loaded} rânduri în PostgreSQL")
    except Exception as e:
        session.rollback()
        print(f"Eroare la import World Bank: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    run()