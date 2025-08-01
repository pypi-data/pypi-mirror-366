from typing import  Optional

import numpy
import skimage.transform as sktr
from rich.segment import Segment
from rich.style import Style

from climax.climax_rs import _colour_strings_with_newlines_rust


class Renderer:
    """
    Base class for renderers.
    """

    def __init__(
        self,
        image: numpy.ndarray,
        rgb_lookup: Optional[list[str]] = None,
        interpolation_order: Optional[int] = None
    ) -> None:
        self.image = image.astype(int)
        self.rgb_lookup = rgb_lookup if rgb_lookup else [f"rgb({i},{i},{i})" for i in range(256)]
        self.interpolation_order = interpolation_order if interpolation_order is not None else 0

    def render(self, resize: tuple[int, int] | None) -> list[Segment]:
        """
        Render an image to Segments using half cells - replace _colour_strings_with_newlines_rust(self.image, self.rgb_lookup)
        with self._colour_strings_with_newlines_python() for a pure Python implementation (about 25% slower)
        """
        target_height = resize[0] if resize else self.image.shape[0]
        if target_height % 2 != 0:
            target_height += 1

        if self.image.shape[0] != target_height:
            resize = (
                (target_height, resize[1]) if resize else (target_height, self.image.shape[1])
            )

        if resize:
            self.image = sktr.resize(self.image, resize, self.interpolation_order, preserve_range=True).astype(int)

        style_cache = {}
        segments = []
        for s in _colour_strings_with_newlines_rust(self.image, self.rgb_lookup):
            if s == "\n":
                segments.append(Segment("\n", None))
            else:
                if s not in style_cache:
                    style_cache[s] = Style.parse(s)
                segments.append(Segment("▄", style_cache[s]))
        return segments
            
    def _colour_strings_with_newlines_python(self) -> list[str]:
        upper = self.image[0::2, :]
        lower = self.image[1::2, :]
        rows, cols = upper.shape[0:2]
        out = []
        for r in range(rows):
            for c in range(cols):
                low = lower[r, c]
                upp = upper[r, c]
                out.append(f"{self.rgb_lookup[low]} on {self.rgb_lookup[upp]}")
            out.append("\n")
        return out
    
    def set_image(self, image: numpy.ndarray) -> bool:
        """
        Set the image to be rendered.
        """
        self.image = image.astype(int)
        return True

    def set_rgb_lookup(self, rgb_lookup: list[str]) -> bool:
        """
        Set the RGB lookup table.
        """
        self.rgb_lookup = rgb_lookup
        return True
