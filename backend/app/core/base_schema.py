import datetime as dt
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def _as_utc(value: dt.datetime) -> dt.datetime:
    return value.replace(tzinfo=dt.UTC) if value.tzinfo is None else value


# MySQL guarda DATETIME sin zona (en UTC). Al marcarlo como UTC, el JSON sale con "Z"
# y el navegador lo convierte bien a la hora local.
UTCDateTime = Annotated[dt.datetime, AfterValidator(_as_utc)]

# Etiqueta libre que elige el usuario (categoría, etiqueta…): se muestra tal cual, emoji incluido
Label = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]

# Puntaje opcional de 1 a 5 (rating de un libro, mood, energía)
Score = Field(default=None, ge=1, le=5)

# Un monto de plata: mayor que cero y con tope para que entre en la columna
Amount = Field(gt=0, lt=10**10)
