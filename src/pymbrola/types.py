"""Custom types."""

from typing import TypeAlias

Number: TypeAlias = float | int
PitchElement: TypeAlias = Number | list[tuple[Number, Number]]
PitchInput: TypeAlias = Number | list[PitchElement] | list[tuple[Number, Number]]
PitchOutput: TypeAlias = list[list[tuple[float, float]]]
