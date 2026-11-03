from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

from app.core.base_schema import ORMModel, UTCDateTime
from app.core.database.base_model import new_uuid

# Las piezas con las que se arma el formulario de cualquier actividad
FieldType = Literal["numero", "texto", "si_no", "opcion", "escala", "ejercicios"]
CHARTABLE: tuple[FieldType, ...] = ("numero", "escala")  # se pueden graficar en el tiempo


class ActivityField(BaseModel):
    # El id no cambia nunca: los valores de las sesiones se guardan por id, no por nombre
    id: str = Field(default_factory=new_uuid, min_length=1, max_length=36)
    name: str = Field(min_length=1, max_length=60)
    type: FieldType
    unit: str | None = Field(default=None, max_length=20)  # "km", "min"…
    options: list[str] | None = None  # solo para "opcion"
    archived: bool = False  # archivado: no se carga más, pero el historial se sigue viendo

    @model_validator(mode="after")
    def check_options(self) -> Self:
        if self.type == "opcion":
            self.options = list(dict.fromkeys(o.strip() for o in self.options or [] if o.strip()))
            if not self.options:
                raise ValueError(f"El campo '{self.name}' necesita al menos una opción")
        else:
            self.options = None
        return self


def _check_fields(fields: list[ActivityField] | None) -> None:
    if fields is None:
        return
    if len({f.id for f in fields}) != len(fields):
        raise ValueError("Hay campos con el mismo id")
    if sum(f.type == "ejercicios" and not f.archived for f in fields) > 1:
        raise ValueError("Una actividad tiene como mucho una lista de ejercicios")


class ActivityIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    emoji: str | None = Field(default=None, max_length=32)
    color: str | None = "#0A84FF"
    active: bool = True
    sort_order: int = 0
    fields: list[ActivityField] = []
    habit_id: str | None = None

    @model_validator(mode="after")
    def check_fields(self) -> Self:
        _check_fields(self.fields)
        return self


class ActivityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    emoji: str | None = Field(default=None, max_length=32)
    color: str | None = None
    active: bool | None = None
    sort_order: int | None = None
    # Lista completa. Un campo que ya no viene queda archivado, no se borra.
    fields: list[ActivityField] | None = None
    habit_id: str | None = None

    @model_validator(mode="after")
    def check_fields(self) -> Self:
        _check_fields(self.fields)
        return self


class ActivityOut(ORMModel):
    id: str
    name: str
    emoji: str | None
    color: str | None
    active: bool
    sort_order: int
    fields: list[ActivityField]
    habit_id: str | None
    created_at: UTCDateTime
