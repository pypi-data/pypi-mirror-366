from pydantic import BaseModel, ConfigDict


class Routine(BaseModel):
    model_config = ConfigDict(extra="forbid")
    _routine_name: str

    @property
    def routine_name(self) -> str:
        return self._routine_name
