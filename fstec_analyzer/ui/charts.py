
import matplotlib
matplotlib.use("QtAgg")

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np

from ui.theme import COLORS, SEVERITY_COLORS


def apply_dark_theme():
    plt.rcParams.update({
        "figure.facecolor":  COLORS["bg_card"],
        "axes.facecolor":    COLORS["bg_panel"],
        "axes.edgecolor":    COLORS["border"],
        "axes.labelcolor":   COLORS["text_secondary"],
        "axes.titlecolor":   COLORS["text_primary"],
        "axes.titlesize":    12,
        "axes.titleweight":  "bold",
        "axes.titlepad":     14,
        "axes.labelsize":    11,
        "xtick.color":       COLORS["text_secondary"],
        "ytick.color":       COLORS["text_secondary"],
        "xtick.labelsize":   10,
        "ytick.labelsize":   10,
        "grid.color":        COLORS["border"],
        "grid.linestyle":    "--",
        "grid.alpha":        0.5,
        "text.color":        COLORS["text_primary"],
        "font.family":       "monospace",
        "figure.dpi":        100,
        "legend.facecolor":  COLORS["bg_card"],
        "legend.edgecolor":  COLORS["border"],
        "legend.labelcolor": COLORS["text_primary"],
        "legend.fontsize":   10,

        "figure.subplot.top": 0.88,
        "figure.subplot.bottom": 0.18,
        "figure.subplot.left": 0.05,
        "figure.subplot.right": 0.97,
    })


apply_dark_theme()

PALETTE = [
    COLORS["accent_blue"],
    COLORS["accent_green"],
    COLORS["accent_orange"],
    COLORS["accent_red"],
    COLORS["accent_purple"],
    COLORS["accent_cyan"],
    "#E8A838", "#FF6B9D", "#56CFE1", "#7209B7",
]

SEV_PALETTE = {
    "Критический": COLORS["sev_critical"],
    "Высокий":     COLORS["sev_high"],
    "Средний":     COLORS["sev_medium"],
    "Низкий":      COLORS["sev_low"],
    "Неизвестно":  COLORS["sev_unknown"],
}


class ChartCanvas(FigureCanvas):
    def __init__(self, fig: Figure):
        super().__init__(fig)
        self.setStyleSheet(f"background-color: {COLORS['bg_card']};")


def bar_chart(df: pd.DataFrame, x_col: str, y_col: str,
              title: str = "", color_col: str = None,
              figsize=(8, 4), horizontal: bool = False) -> ChartCanvas:
    fig, ax = plt.subplots(figsize=figsize, facecolor=COLORS["bg_card"])
    ax.set_facecolor(COLORS["bg_panel"])

    labels = df[x_col].astype(str)
    values = df[y_col]

    if color_col and color_col in df.columns:
        colors = [SEV_PALETTE.get(str(v), PALETTE[0]) for v in df[color_col]]
    else:
        colors = (PALETTE * (len(df) // len(PALETTE) + 1))[:len(df)]

    if horizontal:
        bars = ax.barh(labels, values, color=colors, edgecolor="none", height=0.6)
        ax.set_xlabel(y_col)
        ax.invert_yaxis()
        max_val = max(values) if len(values) else 1
        for bar, val in zip(bars, values):
            ax.text(val + max_val * 0.01, bar.get_y() + bar.get_height() / 2,
                    f"{val:,}", va="center", ha="left",
                    color=COLORS["text_secondary"], fontsize=9)

        fig.subplots_adjust(left=0.28, right=0.95, top=0.90, bottom=0.08)
    else:
        bars = ax.bar(labels, values, color=colors, edgecolor="none", width=0.7)
        ax.set_ylabel(y_col)
        plt.xticks(rotation=35, ha="right")
        max_val = max(values) if len(values) else 1
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max_val * 0.01,
                    f"{val:,}", ha="center", va="bottom",
                    color=COLORS["text_secondary"], fontsize=9)
        fig.subplots_adjust(left=0.10, right=0.97, top=0.88, bottom=0.22)

    if title:
        ax.set_title(title, pad=10, fontsize=12)
    ax.grid(axis="x" if horizontal else "y", alpha=0.3)
    ax.spines[["top", "right", "left" if horizontal else "bottom"]].set_visible(False)
    return ChartCanvas(fig)


def pie_chart(df: pd.DataFrame, label_col: str, value_col: str,
              title: str = "", figsize=(6, 5)) -> ChartCanvas:
    fig, ax = plt.subplots(figsize=figsize, facecolor=COLORS["bg_card"])
    ax.set_facecolor(COLORS["bg_card"])

    labels = df[label_col].astype(str)
    values = df[value_col]

    colors = [SEV_PALETTE.get(str(l), PALETTE[i % len(PALETTE)])
              for i, l in enumerate(labels)]

    wedges, texts, autotexts = ax.pie(
        values, labels=None, colors=colors, autopct="%1.1f%%",
        startangle=140, pctdistance=0.8,
        wedgeprops={"edgecolor": COLORS["bg_card"], "linewidth": 2},
    )
    for at in autotexts:
        at.set_color(COLORS["text_primary"])
        at.set_fontsize(10)

    ax.legend(
        wedges, [f"{l} ({v:,})" for l, v in zip(labels, values)],
        loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), framealpha=0,
    )
    if title:
        ax.set_title(title, pad=12, fontsize=12)
    fig.subplots_adjust(left=0.05, right=0.72, top=0.90, bottom=0.05)
    return ChartCanvas(fig)


def line_chart(df: pd.DataFrame, x_col: str, y_cols: list[str],
               title: str = "", figsize=(9, 4)) -> ChartCanvas:
    fig, ax = plt.subplots(figsize=figsize, facecolor=COLORS["bg_card"])
    ax.set_facecolor(COLORS["bg_panel"])

    for i, col in enumerate(y_cols):
        if col in df.columns:
            color = SEV_PALETTE.get(col, PALETTE[i % len(PALETTE)])
            ax.plot(df[x_col], df[col], color=color, linewidth=2.5,
                    marker="o", markersize=4, label=col)
            ax.fill_between(df[x_col], df[col], alpha=0.08, color=color)

    ax.set_xlabel(x_col)
    ax.grid(alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    if len(y_cols) > 1:
        ax.legend()
    if title:
        ax.set_title(title, pad=10, fontsize=12)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    fig.subplots_adjust(left=0.10, right=0.97, top=0.88, bottom=0.14)
    return ChartCanvas(fig)


def stacked_bar(df_pivot: pd.DataFrame, title: str = "",
                figsize=(10, 5)) -> ChartCanvas:
    fig, ax = plt.subplots(figsize=figsize, facecolor=COLORS["bg_card"])
    ax.set_facecolor(COLORS["bg_panel"])

    bottom = np.zeros(len(df_pivot))
    for i, col in enumerate(df_pivot.columns):
        color = SEV_PALETTE.get(col, PALETTE[i % len(PALETTE)])
        ax.bar(df_pivot.index, df_pivot[col], bottom=bottom,
               color=color, label=col, edgecolor="none", width=0.8)
        bottom += df_pivot[col].values

    ax.set_ylabel("Количество")
    ax.legend(loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=35, ha="right")
    if title:
        ax.set_title(title, pad=10, fontsize=12)
    fig.subplots_adjust(left=0.10, right=0.97, top=0.88, bottom=0.22)
    return ChartCanvas(fig)


def heatmap_chart(df: pd.DataFrame, title: str = "",
                  figsize=(10, 6)) -> ChartCanvas:
    fig, ax = plt.subplots(figsize=figsize, facecolor=COLORS["bg_card"])
    ax.set_facecolor(COLORS["bg_panel"])

    data = df.values.astype(float)
    im = ax.imshow(data, cmap="Blues", aspect="auto")

    ax.set_xticks(range(len(df.columns)))
    ax.set_xticklabels(df.columns, rotation=30, ha="right", fontsize=10)
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels(df.index, fontsize=9)

    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            val = int(data[i, j])
            if val > 0:
                text_color = "white" if data[i, j] > data.max() * 0.5 else COLORS["text_secondary"]
                ax.text(j, i, f"{val:,}", ha="center", va="center",
                        color=text_color, fontsize=8)

    plt.colorbar(im, ax=ax, fraction=0.03)
    if title:
        ax.set_title(title, pad=10, fontsize=12)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.90, bottom=0.12)
    return ChartCanvas(fig)
