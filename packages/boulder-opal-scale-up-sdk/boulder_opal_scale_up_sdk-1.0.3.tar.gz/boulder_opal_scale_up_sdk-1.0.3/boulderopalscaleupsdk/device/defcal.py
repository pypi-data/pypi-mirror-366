# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

import re
from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, PlainSerializer, TypeAdapter
from pydantic.dataclasses import dataclass

QubitAddr = tuple[int, ...]
GateName = str

_KEY_PATTERN = r"^.+#\d+(?:-\d+)*$"


@dataclass(frozen=True)
class DataKey:
    gate: GateName
    addr: QubitAddr

    def as_tuple(self) -> tuple[GateName, QubitAddr]:
        return (self.gate, self.addr)

    @staticmethod
    def from_string(value: Any) -> "DataKey | None":
        match value:
            case str():
                if not re.match(_KEY_PATTERN, value):
                    raise KeyError(f"invalid string for DataKey {value}")
                gate, qubit_str = value.split("#", 1)
                qubit_addr = tuple(int(q) for q in qubit_str.split("-"))
                return DataKey(gate=gate, addr=qubit_addr)
            case _:
                return None

    def serialize_as_string(self) -> str:
        return f"{self.gate}#{'-'.join(str(i) for i in self.addr)}"


DataKeyTypeAdapter = TypeAdapter(DataKey)
DataKeyLike = Annotated[
    DataKey,
    BeforeValidator(lambda x: DataKey.from_string(x) or x),
    PlainSerializer(lambda x: x.serialize_as_string(), return_type=str),
]


@dataclass
class DefCalData:
    body: str
    status: Literal["calibrated", "uncalibrated"]
    scope: Literal["public", "internal"]
