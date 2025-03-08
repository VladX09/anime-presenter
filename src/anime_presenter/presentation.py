import dataclasses
import itertools
import typing as t

from anime_presenter.markup import Markup

T = t.TypeVar("T")
IndexT = dict[tuple[int, int], "Slide"]
SlideIdT = tuple[int, int]
FlatIndexT = dict[int, SlideIdT]


@dataclasses.dataclass
class Slide:
    section_id: int
    slide_id: int
    section_title: str
    slide_title: str
    offset: str

    @property
    def full_id(self) -> SlideIdT:
        return (self.section_id, self.slide_id)


def get_next(seq: t.Iterable[T], selector: t.Callable[[t.Any], bool]) -> T | None:
    seq_iter = iter(seq)
    for element in seq_iter:
        if selector(element):
            break

    return next(seq_iter, None)


def get_previous(seq: t.Iterable[T], selector: t.Callable[[t.Any], bool]) -> T | None:
    previous = None
    for element in seq:
        if selector(element):
            break
        previous = element

    return previous


class IDCounter:

    def __init__(self) -> None:
        self.section_counter = itertools.count(start=1)
        self.slide_counter = itertools.count(start=1)

    def next_slide(self) -> int:
        return next(self.slide_counter)

    def next_section(self) -> int:
        self.slide_counter = itertools.count(start=1)
        return next(self.section_counter)


class PresentationStructure:

    @classmethod
    def from_markup(cls: t.Type["PresentationStructure"], markup: Markup) -> "PresentationStructure":
        index: IndexT = dict()

        id_counter = IDCounter()

        for section in markup.sections:
            section_id = id_counter.next_section()
            section_title = f"Section {section_id}.{' ' + section.label if section.label else ''}"

            for slide in section.slides:
                slide_id = id_counter.next_slide()
                index[(section_id, slide_id)] = Slide(
                    section_id=section_id,
                    section_title=section_title,
                    slide_id=slide_id,
                    slide_title=f"Slide {slide_id}.{' ' + slide.label if slide.label else ''}",
                    offset=slide.offset,
                )

        return cls(index=index)

    def __init__(self, index: IndexT) -> None:
        self._index = index
        self._flat_index: FlatIndexT = {i + 1: k for i, k in enumerate(index.keys())}

        if not self._flat_index:
            raise ValueError("At least one slide is required")

    def get_all_slides(self) -> list[Slide]:
        return list(self._index.values())

    def get_slide_by_number(self, slide_number: int) -> Slide | None:
        full_id = self._flat_index.get(slide_number)
        if not full_id:
            return None

        return self._index.get(full_id)

    def get_first_slide(self) -> Slide:
        return list(self._index.values())[0]

    def get_last_slide(self) -> Slide:
        return list(self._index.values())[-1]

    def get_slide_by_id(self, full_id: SlideIdT) -> Slide | None:
        return self._index.get(full_id)

    def get_next_slide(self, full_id: SlideIdT) -> Slide | None:
        next_slide_id = get_next(seq=iter(self._index.keys()), selector=lambda x: x == full_id)
        if not next_slide_id:
            return None

        return self.get_slide_by_id(next_slide_id)

    def get_prev_slide(self, full_id: SlideIdT) -> Slide | None:
        prev_slide_id = get_previous(seq=iter(self._index.keys()), selector=lambda x: x == full_id)
        if not prev_slide_id:
            return None

        return self.get_slide_by_id(prev_slide_id)

    def _get_next_section(self, section_id: int) -> Slide | None:
        seq = itertools.groupby(self._index.keys(), key=lambda x: x[0])
        next_section = get_next(seq=seq, selector=lambda x: x[0] == section_id)
        return next_section

    def get_next_section_start(self, section_id: int) -> Slide | None:
        next_section = self._get_next_section(section_id)
        if not next_section:
            return self.get_slide_by_id((section_id, 1))

        slide_id = next(next_section[1])
        return self.get_slide_by_id(slide_id)

    def _get_prev_section(self, section_id: int) -> Slide | None:
        seq = itertools.groupby(self._index.keys(), key=lambda x: x[0])
        # Have to wrap into list, the groupby nuance
        seq = ((k, list(v)) for k, v in seq)
        prev_section = get_previous(seq=seq, selector=lambda x: x[0] == section_id)
        return prev_section

    def get_prev_section_start(self, section_id: int) -> Slide | None:
        prev_section = self._get_prev_section(section_id)
        if not prev_section:
            return self.get_slide_by_id((section_id, 1))

        slide_id = prev_section[1][0]
        return self.get_slide_by_id(slide_id)
