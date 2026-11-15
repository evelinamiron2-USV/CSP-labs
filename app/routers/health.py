from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Observation, Country, Indicator

router = APIRouter(prefix="/api/health", tags=["Global Health Data"])

@router.get("/observations")
def get_observations(
    country_code: Optional[str] = Query(None, description="Cod ISO3 țară (ex: ROU, USA)"),
    indicator_code: Optional[str] = Query(None, description="Cod indicator (ex: WHOSIS_000001)"),
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Observation).join(Country).join(Indicator)
    
    if country_code:
        query = query.filter(Observation.country_code == country_code.upper())
    if indicator_code:
        query = query.filter(Indicator.code == indicator_code)
    if year_min:
        query = query.filter(Observation.year >= year_min)
    if year_max:
        query = query.filter(Observation.year <= year_max)
        
    results = query.limit(500).all()
    return [
        {
            "country_code": obs.country_code,
            "indicator": obs.indicator.name if obs.indicator else None,
            "year": obs.year,
            "sex": obs.sex,
            "value": obs.value,
            "is_outlier": obs.is_outlier
        }
        for obs in results
    ]