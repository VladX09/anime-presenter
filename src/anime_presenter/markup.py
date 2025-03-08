import pathlib
import typing as t

import yaml
from pydantic import BaseModel, FilePath, NonNegativeInt, model_validator


class Settings(BaseModel):
    mute_audio: bool = True


class Slide(BaseModel):
    label: str | None = None
    offset: NonNegativeInt


class Section(BaseModel):
    label: str | None = None
    slides: list[Slide]


class Markup(BaseModel):
    markup_file: FilePath
    title: str
    src: FilePath
    sections: list[Section]
    settings: Settings = Settings()

    @model_validator(mode="after")
    def post_init(self):
        self.markup_file = self.markup_file.absolute()
        self.src = (self.markup_file.parent / self.src).absolute()

        cur_offset = -1
        for section in self.sections:
            for slide in section.slides:
                if slide.offset <= cur_offset:
                    raise ValueError("Slide offsets should increase")
                cur_offset = slide.offset
        return self

    @classmethod
    def from_yaml(cls: t.Type["Markup"], path: pathlib.Path) -> "Markup":
        with open(path) as fp:
            data = yaml.load(fp, Loader=yaml.Loader)
            return cls.model_validate({"markup_file": path, **data})
