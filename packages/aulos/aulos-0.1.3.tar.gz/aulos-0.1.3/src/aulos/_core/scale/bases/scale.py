import typing as t
from itertools import starmap
from typing import cast

from aulos._core.context import inject
from aulos._core.object import AulosSchemaObject
from aulos._core.pitchclass import BaseKey, BasePitchClass, PitchClassCollection
from aulos._core.utils import Intervals, Positions, classproperty

from ..schemas import ScaleSchema


class BaseScale[KEY: BaseKey, PITCHCLASS: BasePitchClass](AulosSchemaObject[ScaleSchema]):
    """
    Represents a musical scale with a specific key and pitch class.

    This class provides the foundational structure for defining musical scales, including properties and methods
    to handle intervals, positions, and key signatures. It allows for the creation and manipulation of scales
    in a theoretical context, supporting various musical keys and pitch classes.
    """

    _Key: t.ClassVar[type[BaseKey]]
    _PitchClass: t.ClassVar[type[BasePitchClass]]
    _intervals: t.ClassVar[Intervals]
    _positions: t.ClassVar[Positions]

    _key: KEY
    _signatures: tuple[int, ...]

    @inject
    def __init__(self, key: str | KEY, **kwargs: t.Any) -> None:
        super().__init__(**kwargs)

        if isinstance(key, str):
            self._key = self.Key(key, setting=self._setting)
            self._signatures = tuple(
                starmap(
                    lambda x, y: x + y,
                    zip(
                        self._key.signature,
                        self.schema.generate_scale_signatures(self._intervals),
                        strict=False,
                    ),
                ),
            )

        elif isinstance(key, BaseKey):
            self._key = key
            self._signatures = tuple(
                starmap(
                    lambda x, y: x + y,
                    zip(
                        self._key.signature,
                        self.schema.generate_scale_signatures(self._intervals),
                        strict=False,
                    ),
                ),
            )

        else:
            raise TypeError

    def __init_subclass__(
        cls,
        *,
        intervals: t.Sequence[int] | None = None,
        key: type[KEY] | None = None,
    ) -> None:
        if intervals is None or key is None:
            return
        schema = ScaleSchema(key.schema.pitchclass)
        super().__init_subclass__(schema=schema)
        cls._Key = key
        cls._PitchClass = key.PitchClass
        cls._intervals = Intervals(intervals)
        cls._positions = cls._intervals.to_positions()

    @classproperty
    def Key(self) -> type[KEY]:  # noqa: N802
        return cast("type[KEY]", self._Key)

    @classproperty
    def PitchClass(self) -> type[PITCHCLASS]:  # noqa: N802
        return cast("type[PITCHCLASS]", self._PitchClass)

    @classproperty
    def intervals(self) -> Intervals:
        return self._intervals

    @classproperty
    def positions(self) -> Positions:
        return self._positions

    @property
    def key(self) -> KEY:
        return self._key

    @property
    def signatures(self) -> tuple[int, ...]:
        return self._signatures

    @property
    def components(self) -> PitchClassCollection[PITCHCLASS]:
        components = []
        root = self.PitchClass(self._key.keyname, scale=self, setting=self.setting)
        for pos in self.positions:
            pitchclass = (root + pos).pitchclass
            note = self.PitchClass(pitchclass, scale=self, setting=self.setting)
            components.append(note)
        return PitchClassCollection(components)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseScale):
            return NotImplemented
        return self._intervals == other._intervals and self._key == other._key

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self._key}>"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self._key}>"
