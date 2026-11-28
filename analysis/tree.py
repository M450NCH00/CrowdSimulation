"""A decision tree of depth 3 or less (issue #63, RF-8, task 5).

A small tree on the per-agent predictors (and condition and geometry as dummies) can be read and
checked by hand, and is the compressed form of the mapping (``literature/trained-deciders/
verdict.md``, point 2). It is reported with what it is worth: its accuracy on the rows it was
grown on, the accuracy of always guessing the commoner outcome, and its accuracy on held-out
sessions (grouped cross-validation, so that one session's two rows are never split).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import GroupKFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier, export_text

from .effects import design_matrix, full_rank

MAX_DEPTH = 3


@dataclass
class Tree:
    outcome: str
    n: int
    note: str = ""
    text: str = ""
    accuracy: Optional[float] = None
    majority: Optional[float] = None
    cv_accuracy: Optional[float] = None
    cv_folds: int = 0
    used: list[str] = field(default_factory=list)
    model: Optional[DecisionTreeClassifier] = None
    columns: list[str] = field(default_factory=list)


def grow(agents: pd.DataFrame, predictors: Sequence[str], outcome: str = "passed_first", max_depth: int = MAX_DEPTH, seed: int = 63) -> Tree:
    if not 1 <= max_depth <= MAX_DEPTH:
        raise ValueError(f"max_depth: 1 to {MAX_DEPTH}, got {max_depth}")
    rows = agents.loc[agents[outcome].notna()]
    tree = Tree(outcome, len(rows))
    if rows.empty or rows[outcome].nunique() < 2:
        tree.note = "the outcome takes one value (or none): no tree"
        return tree
    categorical = [name for name in ("condition", "geometry") if name in rows.columns]
    matrix, _ = full_rank(design_matrix(rows, predictors, categorical))
    if matrix.shape[1] == 0:
        tree.note = "no predictor varies: no tree"
        return tree
    y = rows[outcome].astype(int)
    leaf = max(5, round(0.02 * len(rows)))
    model = DecisionTreeClassifier(max_depth=max_depth, min_samples_leaf=leaf, random_state=seed).fit(matrix, y)
    tree.model, tree.columns = model, list(matrix.columns)
    tree.text = export_text(model, feature_names=tree.columns, show_weights=True)
    tree.accuracy = float(model.score(matrix, y))
    tree.majority = float(max(y.mean(), 1.0 - y.mean()))
    tree.used = sorted({tree.columns[i] for i in model.tree_.feature if i >= 0})
    sessions = rows["session_key"].nunique()
    tree.cv_folds = min(5, sessions)
    if tree.cv_folds >= 2:
        scores = cross_val_score(clone(model), matrix, y, groups=rows["session_key"], cv=GroupKFold(n_splits=tree.cv_folds))
        tree.cv_accuracy = float(scores.mean())
    return tree


def save_figure(tree: Tree, path: Path) -> bool:
    """The tree as a figure (PNG); False when there is no tree."""
    if tree.model is None:
        return False
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.tree import plot_tree

    figure, axes = plt.subplots(figsize=(14, 7))
    plot_tree(tree.model, feature_names=tree.columns, class_names=["no", "yes"], impurity=False, proportion=True, rounded=True, ax=axes, fontsize=8)
    axes.set_title(f"{tree.outcome}: decision tree (depth <= {tree.model.get_depth()}, {tree.n} rows)")
    figure.tight_layout()
    figure.savefig(path, dpi=120)
    plt.close(figure)
    return True
