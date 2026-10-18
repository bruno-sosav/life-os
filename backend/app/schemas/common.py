import datetime as dt
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def _as_utc(value: dt.datetime) -> dt.datetime:
    return value.replace(tzinfo=dt.UTC) if value.tzinfo is None else value


# MySQL guarda DATETIME sin zona (en UTC). Al marcarlo como UTC, el JSON sale con "Z"
# y el navegador lo convierte bien a la hora local.
UTCDateTime = Annotated[dt.datetime, AfterValidator(_as_utc)]
