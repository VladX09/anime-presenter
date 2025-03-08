"""For now only Full HD is supported."""

import pathlib
from contextlib import contextmanager

import cv2
import numpy.typing as nt
from loguru import logger
from PIL import Image
from rich import print

from anime_presenter.markup import Markup
from anime_presenter.presentation import PresentationStructure


@contextmanager
def video_capture_wrapper(*args, **kwargs):
    try:
        vid_stream = cv2.VideoCapture(*args, **kwargs)
        yield vid_stream
    finally:
        vid_stream.release()


def add_slide_info(image: nt.NDArray, slide_number: str, section_title, slide_title) -> nt.NDArray:
    overlay = image.copy()
    output = image.copy()

    # Define box properties
    box_height = 80  # Height of the overlay box
    alpha = 0.6  # Transparency level (0 = fully transparent, 1 = fully opaque)

    # Box coordinates (bottom of the image)
    box_start = (0, 1080 - box_height)
    box_end = (1920, 1080)

    # Draw the semi-transparent rectangle
    cv2.rectangle(overlay, box_start, box_end, (0, 0, 0), -1)
    cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

    # Text properties
    # font = cv2.FONT_HERSHEY_SIMPLEX
    font = cv2.FONT_HERSHEY_TRIPLEX
    font_scale = 1
    font_thickness = 1
    text_color = (255, 255, 255)  # White text

    # Format slide info text
    section_text = f"{slide_number} | {section_title}"
    slide_text = f"{slide_title}"

    # Calculate text positions
    text_x = 30
    text_y1 = 1080 - box_height + 30  # First line
    text_y2 = 1080 - box_height + 65  # Second line

    # Draw text on the image
    cv2.putText(
        output,
        section_text,
        (text_x, text_y1),
        font,
        font_scale,
        text_color,
        font_thickness,
        cv2.LINE_AA,
    )
    cv2.putText(
        output,
        slide_text,
        (text_x, text_y2),
        font,
        font_scale,
        text_color,
        font_thickness,
        cv2.LINE_AA,
    )

    return output


def save_to_pdf(markup: Markup, output_file: pathlib.Path) -> None:

    pres = PresentationStructure.from_markup(markup)
    with video_capture_wrapper(markup.src) as video:
        pages = []
        for slide in sorted(pres.get_all_slides(), key=lambda s: s.offset):
            if slide.offset >= int(video.get(cv2.CAP_PROP_FRAME_COUNT)):
                logger.warning(f"Offset out of boundaries: {slide}")
                continue

            video.set(cv2.CAP_PROP_POS_FRAMES, slide.offset)
            ret, frame = video.read()
            if not ret:
                logger.warning(f"Error during reading: {slide}")
                continue

            frame = cv2.resize(frame, (1920, 1080))
            frame = add_slide_info(
                frame,
                slide_number=f"{slide.section_id}/{slide.slide_id}",
                section_title=slide.section_title,
                slide_title=slide.slide_title,
            )
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            image = Image.fromarray(frame)
            pages.append(image)

        if not pages:
            print("[bold red]Alert![/bold red] No frames to save")
            exit(1)

    pages[0].save(output_file, save_all=True, append_images=pages[1:])
