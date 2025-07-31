# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import abc
import re
import typing as t


SegmentTuple = t.Tuple[str, str]


class AbstractVersionPatternSegment(abc.ABC):

    @property
    def segment_names(self) -> list[str]:
        return []

    @abc.abstractmethod
    def regexp_string(self) -> str:
        pass

    @abc.abstractmethod
    def segments_tuples_to_text(self, segments_tuples: list[SegmentTuple]) -> str:
        pass

    def _name_anon(self, namep: str) -> None:  # TODO weird
        pass

    def _str_to_val(self, txt: str) -> object:  # TODO weird
        return txt


class NumericVersionPatternSegment(AbstractVersionPatternSegment):

    def __init__(self, *, partname: str|None = None):
        super().__init__()
        self.__partname = partname or ""

    @property
    def partname(self) -> str|None:
        return self.__partname

    @property
    def segment_names(self) -> list[str]:
        return [self.partname]

    def regexp_string(self) -> str:
        return rf"(?P<{self.partname}>\d+)"

    def segments_tuples_to_text(self, segments_tuples: list[SegmentTuple]) -> str:
        if (len(segments_tuples) == 0) or (self.partname != segments_tuples[0][0]):
            raise Exception("TODO")
        return str(segments_tuples.pop(0)[1])

    def _name_anon(self, namep):
        if not self.__partname:
            self.__partname = namep

    def _str_to_val(self, txt: str) -> object:  # TODO use !!!
        return int(txt)


class SeparatorVersionPatternSegment(AbstractVersionPatternSegment):

    def __init__(self, *, text: str):
        super().__init__()
        self.__text = text

    def regexp_string(self) -> str:
        return re.escape(self.__text)

    def segments_tuples_to_text(self, segments_tuples: list[SegmentTuple]) -> str:
        return self.__text


class OptionalVersionPatternSegment(AbstractVersionPatternSegment):  # TODO

    # TODO dedup (ConcatenatedVersionPatternSegment)

    def __init__(self, *, segments: t.Iterable[AbstractVersionPatternSegment]):
        super().__init__()
        self.__segment = ConcatenatedVersionPatternSegment(segments=segments)

    @property
    def segment_names(self):
        return self.__segment.segment_names

    def regexp_string(self) -> str:
        return f"({self.__segment.regexp_string()})?"

    def segments_tuples_to_text(self, segments_tuples: list[SegmentTuple]) -> str:
        return self.__segment.segments_tuples_to_text(segments_tuples) if segments_tuples else ""

    def _name_anon(self, namep):  # TODO  weird
        self.__segment._name_anon(namep)


class ConcatenatedVersionPatternSegment(AbstractVersionPatternSegment):

    def __init__(self, *, segments: t.Iterable[AbstractVersionPatternSegment]):
        super().__init__()
        self.__segments = segments

    @property
    def segment_names(self):
        result = []
        for segment in self.__segments:
            result += segment.segment_names
        return result

    def regexp_string(self) -> str:
        result = ""
        for segment in self.__segments:
            result += segment.regexp_string()
        return result

    def segments_tuples_to_text(self, segments_tuples: list[SegmentTuple]) -> str:
        result = ""
        for segment in self.__segments:
            result += segment.segments_tuples_to_text(segments_tuples)
        return result

    def _name_anon(self, namep):  # TODO weird
        for isegment, segment in enumerate(self.__segments):
            segment._name_anon(f"{namep}_{isegment}")


class VersionPattern:

    def __init__(self, *, segments: t.Iterable[AbstractVersionPatternSegment]):
        self.__segments = segments
        self.__segment = ConcatenatedVersionPatternSegment(segments=segments)
        self.__segment._name_anon("_")

    @property
    def segments(self) -> list[AbstractVersionPatternSegment]:
        return list(self.__segments)

    @property
    def segment_names(self):
        return self.__segment.segment_names

    def text_to_segments_tuples(self, text: str) -> list[SegmentTuple]:
        result = []
        match = re.fullmatch(self.__segment.regexp_string(), text)
        if not match:
            raise ValueError(f"version string {text!r} not according to pattern")
        matchgroupdict = match.groupdict()
        for segmentname in self.segment_names:
            segmentvalue = matchgroupdict.get(segmentname, self)
            if segmentvalue != self:
                result.append((segmentname, segmentvalue))
        return result

    def segments_tuples_to_text(self, segments_tuples: list[SegmentTuple]) -> str:  # TODO -> segments_tuples_to_text
        return self.__segment.segments_tuples_to_text(list(segments_tuples))


class Version:  # TODO abstract base class

    def __eq__(self, o):  # TODO __hash__
        if self is o:
            return True
        if not isinstance(o, Version):
            return False
        return self.segments_tuples == o.segments_tuples

    def __lt__(self, o):
        if self == o:
            return False
        if not isinstance(o, Version):
            return super().__lt__(o)
        ntups = self.segments_tuples
        ntupo = o.segments_tuples
        while True:
            tups = ntups.pop(0)
            tupo = ntupo.pop(0)
            if tups[0] != tupo[0]:
                raise ValueError(f"versions {self!r} and {o!r} are not comparable")
            if tups[1] == tupo[1]:
                continue
            return tups[1] < tupo[1]

    def __init__(self, *, text: str = None, pattern: VersionPattern = None, **segment_values):
        self.__text = text
        self.__pattern = pattern
        self.__segment_values = segment_values

    @property
    def segments_tuples(self):
        if self.__text is not None:
            return self.pattern.text_to_segments_tuples(self.__text)
        result = []
        for segment in self.pattern.segments:
            for segmentname in segment.segment_names:
                segmentvalue = self.__segment_values.get(segmentname, self)
                if segmentvalue != self:
                    result.append((segmentname, segmentvalue))
        return result

    @property
    def segments_values(self) -> dict[str, t.Any]:
        return {skey: sval for (skey, sval) in self.segments_tuples}

    @property
    def text(self) -> str:
        if self.__text is None:
            return self.pattern.segments_tuples_to_text(self.segments_tuples)
        else:
            return self.__text

    @property
    def pattern(self) -> VersionPattern:
        return self.__pattern

    def __str__(self):
        return self.text
