"""Visualisation: the transcript renderer, the trajectory plot and the animated viewer.

``trajectory_plot`` needs matplotlib and is imported only when it is used. ``viewer``
writes a self-contained HTML page and needs nothing beyond the standard library.
"""

from .transcript import render_transcript

__all__ = ["render_transcript"]
