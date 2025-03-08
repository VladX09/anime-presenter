import pathlib

from anime_presenter.markup import Markup


def test_markup_success(resources: pathlib.Path):
    markup_file = resources / "positive_case.yaml"
    print(markup_file.read_text())
    markup = Markup.from_yaml(markup_file)
    expected = {
        "title": "My Awesome Presentation",
        "markup_file": markup_file.absolute(),
        "src": (resources / "video.mp4").absolute(),
        "settings": {"mute_audio": True},
        "sections": [
            {
                "label": "Introduction",
                "slides": [
                    {"label": "Title", "offset": 0},
                    {"label": None, "offset": 100},
                ],
            },
            {
                "label": None,
                "slides": [
                    {"label": None, "offset": 200},
                    {"label": None, "offset": 300},
                    {"label": "End", "offset": 450},
                ],
            },
        ],
    }

    assert markup.model_dump() == expected
