from sqlalchemy import select, func, cast, String
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement
from app.models import Observation, Country, Indicator, Sex
from app.domain import ObservationCriteria, ObservationListItem, Option, FilterOptions

_STABLE_ORDER = (
    Country.name,
    Observation.year.desc(),
    Indicator.code,
    Observation.sex,
    Observation.observation_id,
)

def _conditions(criteria: ObservationCriteria) -> list[ColumnElement[bool]]:
    conditions: list[ColumnElement[bool]] = []
    if criteria.country_iso3 is not None:
        conditions.append(Country.country_code == criteria.country_iso3)
    if criteria.indicator_code is not None:
        conditions.append(Indicator.code == criteria.indicator_code)
    if criteria.region is not None:
        conditions.append(Country.region == criteria.region)
    if criteria.year_from is not None:
        conditions.append(Observation.year >= criteria.year_from)
    if criteria.year_to is not None:
        conditions.append(Observation.year <= criteria.year_to)
    if criteria.sex is not None:
        conditions.append(Observation.sex == criteria.sex)
    return conditions

def _matching_observations(criteria: ObservationCriteria):
    return (
        select(
            Country.country_code.label("country_iso3"),  # <-- ADAUGĂ ACEASTĂ LINIE
            Country.name.label("country_name"),
            Country.region.label("region"),
            Indicator.code.label("indicator_code"),
            Indicator.name.label("indicator_name"),
            Indicator.unit.label("unit"),
            Observation.year.label("year"),
            Observation.sex.label("sex"),
            Observation.value.label("value"),
        )
        .join(Country, Observation.country_code == Country.country_code)
        .join(Indicator, Observation.indicator_id == Indicator.indicator_id)
        .where(*_conditions(criteria))
    )
class ObservationRepository:
    """Reads observations and the lookup values used to filter them."""
    def __init__(self, session: Session) -> None:
        self._session = session

    def find(
        self, criteria: ObservationCriteria, *, limit: int, offset: int
    ) -> list[ObservationListItem]:
        query = (
            _matching_observations(criteria)
            .order_by(*_STABLE_ORDER)
            .limit(limit)
            .offset(offset)
        )
        return [
            ObservationListItem(**row)
            for row in self._session.execute(query).mappings()
        ]

    def count(self, criteria: ObservationCriteria) -> int:
        query = select(func.count()).select_from(
            _matching_observations(criteria).subquery()
        )
        return self._session.scalar(query) or 0

    def list_countries(self) -> list[Option]:
        query = select(Country.country_code, Country.name).distinct().order_by(Country.name)
        return [Option(value=row.country_code, label=f"{row.name} ({row.country_code})") for row in self._session.execute(query)]

    def list_indicators(self) -> list[Option]:
        query = select(Indicator.code, Indicator.name).distinct().order_by(Indicator.name)
        return [Option(value=row.code, label=row.name) for row in self._session.execute(query)]

    def list_regions(self) -> list[Option]:
        query = select(Country.region).where(Country.region.is_not(None)).distinct().order_by(Country.region)
        return [Option(value=row.region, label=row.region) for row in self._session.execute(query) if row.region]

    def get_filter_options(self) -> FilterOptions:
        return FilterOptions(
            countries=self.list_countries(),
            indicators=self.list_indicators(),
            regions=self.list_regions(),
        )