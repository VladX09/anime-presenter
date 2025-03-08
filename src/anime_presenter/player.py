import pathlib
import typing as t

import pygame
from pyvidplayer2 import Video, VideoPlayer

from anime_presenter.markup import Markup, Settings
from anime_presenter.navigation import Commands, Navigator
from anime_presenter.presentation import PresentationStructure


class Player:

    @classmethod
    def from_markup(cls: t.Type["Player"], markup: Markup) -> "Player":
        return cls(
            src_path=markup.src,
            title=markup.title,
            navigator=Navigator(PresentationStructure.from_markup(markup)),
            settings=markup.settings,
        )

    def __init__(
        self,
        src_path: pathlib.Path,
        title: str,
        navigator: Navigator,
        settings: Settings,
    ) -> None:
        self._running = False
        self.src_path = src_path
        self.title = title
        self._navigator = navigator
        self._settings = settings

    def open(self) -> "Player":
        video = Video(
            path=str(self.src_path),
            use_pygame_audio=True,
            no_audio=self._settings.mute_audio,
        )
        self._win = pygame.display.set_mode(video.original_size, pygame.RESIZABLE)
        pygame.display.set_caption(self.title)
        self._player = VideoPlayer(
            video=video,
            rect=(0, 0, *video.original_size),
            interactable=False,
        )
        self._navigator.reset()
        return self

    @property
    def _video(self) -> Video:
        return self._player.get_video()

    def close(self) -> None:
        self._player.close()
        pygame.quit()

    def __enter__(self) -> "Player":
        return self

    def __exit__(self, *_: t.Any) -> t.Any:
        self.close()

    def _render(self, events) -> None:
        self._player.update(events)
        self._player.draw(self._win)
        pygame.time.wait(16)
        pygame.display.update()

    def _stop_on_slide(self) -> None:
        if not self._video.paused and self._video.frame >= self._navigator.state.next_offset:
            self._video.pause()
            self._navigator.apply(Commands.to_next_slide)

    def stop(self) -> None:
        self._running = False

    def loop(self) -> None:
        self._running = True
        while self._running:
            events = pygame.event.get()
            for event in events:
                self._handle_event(event, events)

            self._stop_on_slide()
            self._render(events)

    def _move_to_frame(self, frame: int | None, events) -> None:
        if frame is None:
            return None

        self._video.seek_frame(frame)

        # There are some issues with update + pause combination
        # So we need to render frame several times to update it
        self._video.resume()
        for _ in range(6):
            self._render(events)

        self._video.pause()

    def _handle_event(self, event, events):
        event_descr = (
            event.type,
            getattr(event, "mod", None),
            getattr(event, "key", None),
        )

        match event_descr:
            case (pygame.QUIT, mod, _):
                self.stop()
            case (pygame.VIDEORESIZE, mod, _):
                self._player.resize(self._win.get_size())
            case (pygame.KEYDOWN, pygame.KMOD_NONE, pygame.K_z):
                self._player.toggle_zoom()
            case (pygame.KEYDOWN, pygame.KMOD_NONE, pygame.K_q):
                self.stop()
            case (pygame.KEYDOWN, pygame.KMOD_NONE, pygame.K_SPACE):
                if self._navigator.state.next:  # Stop on the last slide
                    self._video.resume()
            case (pygame.KEYDOWN, pygame.KMOD_NONE, pygame.K_RIGHT):
                frame = self._navigator.apply(Commands.to_next_slide)
                self._move_to_frame(frame, events)
            case (pygame.KEYDOWN, pygame.KMOD_NONE, pygame.K_LEFT):
                frame = self._navigator.apply(Commands.to_prev_slide) or 0
                self._move_to_frame(frame, events)
            case (pygame.KEYDOWN, mod, pygame.K_RIGHT) if mod & pygame.KMOD_SHIFT:
                frame = self._navigator.apply(Commands.to_next_section)
                self._move_to_frame(frame, events)
            case (pygame.KEYDOWN, mod, pygame.K_LEFT) if mod & pygame.KMOD_SHIFT:
                frame = self._navigator.apply(Commands.to_prev_section) or 0
                self._move_to_frame(frame, events)
            case (pygame.KEYDOWN, pygame.KMOD_NONE, pygame.K_b):
                frame = self._navigator.apply(Commands.to_first_slide)
                self._move_to_frame(frame, events)
            case (pygame.KEYDOWN, pygame.KMOD_NONE, pygame.K_e):
                frame = self._navigator.apply(Commands.to_last_slide)
                self._move_to_frame(frame, events)
