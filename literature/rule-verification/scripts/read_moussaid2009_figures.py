"""Read the side shares of Moussaid et al. 2009, Figures 4 and 5, from the figures' pixels (issue #122, RF-37).

Figure 4 (c) and (d): the paper gives the shares only as bars with no axis labels, a dashed line in
each panel and the frame. **Assumption:** the dashed line is 0.5 and the bottom axis 0 (panel (c)'s
two blue bars then sum to 1.01, which fits). Panel (d)'s two blue bars sum to 1.12 on that scale, so
its reading is also given normalised to sum to 1.

Figure 5 (b): the observed share of pedestrians in each of six zones across the street, "left" and
"right" in each walker's own direction (1 left sidewalk, 2-3 left of the walkway, 4-5 right of the
walkway, 6 right sidewalk). The six blue bars are normalised to sum to 1.

    uv run --no-project --python 3.13 --with pymupdf --with numpy python -I \
        literature/rule-verification/scripts/read_moussaid2009_fig4.py refs/rf14_moussaid2009_side_preference.pdf
"""

import sys

import numpy as np
import pymupdf

FIGURE_XREF = 104  # page 16's first image: Figure 4, 986 x 522 px
BARS = {"left": (829, 854), "right": (909, 934)}  # the blue (experiment) bars' columns
GAP = (887, 908)  # columns between the bars, where only the dashed line is drawn
PANELS = {"c (condition 2: the other stands still)": (10, 211), "d (condition 3: both walk)": (249, 450)}


def main(path: str) -> None:
    pix = pymupdf.Pixmap(pymupdf.open(path), FIGURE_XREF)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    blue = (b > 150) & (r < 90) & (g < 90)
    grey = (np.abs(r - g) < 30) & (np.abs(g - b) < 30) & (a.sum(axis=2) < 450)
    for panel, (top, axis) in PANELS.items():
        dashed = [y for y in range(top, axis) if grey[y, GAP[0]:GAP[1]].sum() >= 2]
        half = axis - dashed[0]
        shares = {}
        for side, (x0, x1) in BARS.items():
            tops = [np.where(blue[top:axis, x])[0].min() + top for x in range(x0, x1 + 1) if blue[top:axis, x].any()]
            shares[side] = (axis - float(np.median(tops))) / (2 * half)
        total = sum(shares.values())
        print(panel, {side: round(v, 2) for side, v in shares.items()}, "sum", round(total, 2),
              "normalised", {side: round(v / total, 2) for side, v in shares.items()})
    figure5(path)


FIGURE5_XREF = 105  # page 16's second image: Figure 5, 561 x 1022 px
FIGURE5_BARS = ((168, 180), (232, 245), (297, 309), (361, 374), (426, 438), (490, 503))  # zones 1 to 6, blue
FIGURE5_PANEL_B_FROM = 600  # rows below this are panel (b)


def figure5(path: str) -> None:
    pix = pymupdf.Pixmap(pymupdf.open(path), FIGURE5_XREF)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].astype(int)
    blue = (a[..., 2] > 150) & (a[..., 0] < 90) & (a[..., 1] < 90)
    blue[:FIGURE5_PANEL_B_FROM] = False
    heights = []
    for x0, x1 in FIGURE5_BARS:
        ys = [np.where(blue[:, x])[0] for x in range(x0, x1 + 1)]
        heights.append(float(np.median([y.max() - y.min() + 1 for y in ys if len(y)])))
    shares = [h / sum(heights) for h in heights]
    print("figure 5b zones 1-6", [round(s, 3) for s in shares],
          "own left (1-3)", round(sum(shares[:3]), 2), "own right (4-6)", round(sum(shares[3:]), 2))


if __name__ == "__main__":
    main(sys.argv[1])
