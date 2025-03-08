import pathlib

from anime_presenter.markup import Markup
from anime_presenter.presentation import PresentationStructure


def test_markup_builder(resources: pathlib.Path):
    markup_file = resources / "positive_case.yaml"
    markup = Markup.from_yaml(markup_file)
    presentation = PresentationStructure.from_markup(markup)

    assert list(presentation._index.keys()) == [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3)]
    assert [(s.section_title, s.slide_title) for s in presentation._index.values()] == [
        ("Section 1. Introduction", "Slide 1. Title"),
        ("Section 1. Introduction", "Slide 2."),
        ("Section 2.", "Slide 1."),
        ("Section 2.", "Slide 2."),
        ("Section 2.", "Slide 3. End"),
    ]


def test_navigation(resources: pathlib.Path):
    markup_file = resources / "positive_case.yaml"
    markup = Markup.from_yaml(markup_file)
    presentation = PresentationStructure.from_markup(markup)

    assert presentation.get_slide_by_id((2, 1)).full_id == (2, 1)
    assert presentation.get_slide_by_id((100, 1000)) is None
    assert presentation.get_slide_by_id((100, -1000)) is None

    assert presentation.get_slide_by_number(2).full_id == (1, 2)
    assert presentation.get_slide_by_number(1000) is None
    assert presentation.get_slide_by_number(-1000) is None

    assert presentation.get_next_slide((1, 2)).full_id == (2, 1)
    assert presentation.get_next_slide((2, 3)) is None

    assert presentation.get_prev_slide((2, 3)).full_id == (2, 2)
    assert presentation.get_prev_slide((1, 1)) is None

    assert presentation.get_next_section_start(1).full_id == (2, 1)
    assert presentation.get_next_section_start(2).full_id == (2, 1)
    assert presentation.get_prev_section_start(2).full_id == (1, 1)
    assert presentation.get_prev_section_start(1).full_id == (1, 1)
