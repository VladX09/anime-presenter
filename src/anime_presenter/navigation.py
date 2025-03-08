import typing as t

import pydantic
import typing_extensions as te
from loguru import logger

from anime_presenter.presentation import PresentationStructure, Slide


def offset(slide: Slide | None) -> None:
    if not slide:
        return None

    return slide.offset


class State(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(validate_assignment=True)

    cur: Slide | None
    next: Slide | None

    @property
    def cur_offset(self) -> int | float:
        return self.cur.offset if self.cur else float("-inf")

    @property
    def next_offset(self) -> int | float:
        return self.next.offset if self.next else float("inf")

    def __str__(self) -> str:
        cur_id = self.cur.full_id if self.cur else None
        next_id = self.next.full_id if self.next else None

        return f"State({cur_id}:{self.cur_offset}, {next_id}:{self.next_offset})"

    @pydantic.model_validator(mode="after")
    def illegal_states(self) -> te.Self:
        match (self.cur, self.next):
            case (None, None):
                raise ValueError(f"Illegal state: {self}")
            case _:
                return self


def initial_state(struc: PresentationStructure) -> State:
    return State(cur=None, next=struc.get_first_slide())


class Commands:

    def to_next_slide(state: State, struc: PresentationStructure) -> tuple[State, int | None]:
        match state:
            case State(cur=cur, next=None):
                return State(cur=cur, next=None), None

            case State(cur=_, next=next) if next is not None:
                new_next = struc.get_next_slide(next.full_id)
                new_cur = next
                return State(cur=new_cur, next=new_next), offset(new_cur)

    def to_prev_slide(state: State, struc: PresentationStructure) -> tuple[State, int | None]:
        match state:
            case State(cur=None, next=next):
                return State(cur=None, next=next), None

            case State(cur=cur, next=_) if cur is not None:
                new_cur = struc.get_prev_slide(cur.full_id)
                return State(cur=new_cur, next=cur), offset(new_cur)

    def to_next_section(state: State, struc: PresentationStructure) -> tuple[State, int | None]:
        match state:
            case State(cur=cur, next=None):
                return State(cur=cur, next=None), None

            case State(cur=_, next=next) if next is not None:
                new_cur = struc.get_next_section_start(next.section_id)
                new_next = struc.get_next_slide(new_cur.full_id)
                return State(cur=new_cur, next=new_next), offset(new_cur)

    def to_prev_section(state: State, struc: PresentationStructure) -> tuple[State, int | None]:
        match state:
            case State(cur=None, next=next):
                return State(cur=None, next=next), None

            case State(cur=cur, next=_) if cur is not None:
                new_cur = struc.get_prev_section_start(cur.section_id)
                new_next = struc.get_next_slide(new_cur.full_id)
                return State(cur=new_cur, next=new_next), offset(new_cur)

    def to_first_slide(state: State, struc: PresentationStructure) -> tuple[State, int | None]:
        new_cur = struc.get_first_slide()
        return State(cur=new_cur, next=struc.get_next_slide(new_cur.full_id)), offset(new_cur)

    def to_last_slide(state: State, struc: PresentationStructure) -> tuple[State, int | None]:
        new_cur = struc.get_last_slide()
        return State(cur=new_cur, next=None), offset(new_cur)


class Navigator:

    def __init__(self, struc: PresentationStructure) -> None:
        self._struc = struc
        self.state = initial_state(struc)

    def reset(self) -> None:
        self.state = initial_state(self._struc)

    def apply(
        self,
        cmd: t.Callable[[State, PresentationStructure], tuple[State, int | None]],
    ) -> int | None:
        old_state = self.state
        self.state, new_frame = cmd(self.state, self._struc)

        logger.debug("{} -> [{}] -> {}".format(old_state, cmd.__name__, self.state))

        return new_frame
