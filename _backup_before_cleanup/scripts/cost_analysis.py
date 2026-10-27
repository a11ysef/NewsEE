"""Cost and efficiency analysis (no API calls, reads saved results only).

  python scripts/cost_analysis.py            # test split

Outputs
  results/cost_<split>.md                    tables for Chapter 5
  results/fig_cost_vs_f1_<split>.png / .pdf  F1 against tokens per document, baseline -> framework

Token counts: results/main_<model>_<split>.json store the usage of the calls that were NOT
served from the local cache. Totals are estimated as tokens per fresh call x all calls.
Prices: DeepSeek list prices (RMB per million tokens, cache-miss input). Zhipu runs used
resource packs, so only their tokens are reported. Real DeepSeek bills are lower because of
its prefix cache (repeated guidelines and demonstrations hit the cache).
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402

ORDER = ["glm-4.7", "ds-pro", "glm-air", "ds-flash", "ds-flash-think"]
# (input, output) RMB per million tokens; peak and off-peak (weekday 9-12, 14-18 = peak)
PRICES = {"ds-flash": ((2, 8), (1, 4)), "ds-flash-think": ((2, 8), (1, 4)), "ds-pro": ((9, 27), (4.5, 13.5))}
# thinking mode ran out of output budget on most calls, so it is discussed separately, not plotted
FIG_EXCLUDE = {"ds-flash-think"}
BASE, FW, GOLD = "Baseline (zero-shot, all-in-one)", "NewsEE framework", "Framework, gold triggers"
# categorical slots 1-5 of the validated reference palette, fixed per model
COLORS = {"glm-4.7": "#2a78d6", "ds-pro": "#eb6834", "glm-air": "#1baf7a", "ds-flash": "#eda100",
          "ds-flash-think": "#e87ba4"}
MARKERS = {"glm-4.7": "o", "ds-pro": "s", "glm-air": "D", "ds-flash": "^", "ds-flash-think": "v"}


def estimate(info):
    u = info.get("usage", {})
    fresh = u.get("calls", 0)
    total_calls = info.get("llm_calls") or (fresh + u.get("cached", 0))
    if not fresh:
        return None
    k = total_calls / fresh
    return {"calls": total_calls, "prompt": u.get("prompt_tokens", 0) * k,
            "completion": u.get("completion_tokens", 0) * k,
            "reasoning": u.get("reasoning_tokens", 0) * k}


def cost(model, t):
    if model not in PRICES or t is None:
        return None, None
    (pi, po), (oi, oo) = PRICES[model]
    peak = t["prompt"] / 1e6 * pi + t["completion"] / 1e6 * po
    off = t["prompt"] / 1e6 * oi + t["completion"] / 1e6 * oo
    return round(peak, 2), round(off, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    a = ap.parse_args()
    res_dir = config.ROOT / "results"
    data = [json.loads(f.read_text()) for f in sorted(res_dir.glob(f"main_*_{a.split}.json"))]
    data.sort(key=lambda d: ORDER.index(d["model"]) if d["model"] in ORDER else 99)

    lines = [f"# Cost and efficiency on {a.split}", "",
             "| model | method | docs | LLM calls | calls / doc | input tokens / doc (k) | output tokens / doc (k) | "
             "Trig-C | Arg-C (EM) | cost RMB (peak) | cost RMB (off-peak) |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    points = []
    for d in data:
        n = d["n_docs"]
        for label, row in d["rows"].items():
            t = estimate(row["info"])
            if t is None:
                continue
            peak, off = cost(d["model"], t)
            m = row["metrics"]
            lines.append(f"| {d['model']} | {label} | {n} | {t['calls']} | {t['calls'] / n:.1f} | "
                         f"{t['prompt'] / n / 1000:.1f} | {t['completion'] / n / 1000:.2f} | "
                         f"{m['Trig-C']['F1']:.1f} | {m['Arg-C (EM)']['F1']:.1f} | "
                         f"{'—' if peak is None else peak} | {'—' if off is None else off} |")
            if label in (BASE, FW) and d["model"] not in FIG_EXCLUDE:
                points.append({"model": d["model"], "method": label,
                               "tok": (t["prompt"] + t["completion"]) / n / 1000,
                               "trig": m["Trig-C"]["F1"], "arg": m["Arg-C (EM)"]["F1"]})
    lines += ["", "Tokens are estimated from fresh (non-cached) calls. Zhipu runs: resource packs, no cash cost.",
              "DeepSeek costs use cache-miss list prices, so they are upper bounds."]

    # cost of each ablation setting (dev, first full run of each configuration)
    abl = res_dir / "ablation_ds-flash_dev_guidelineV1.csv"
    if abl.exists():
        rows = list(csv.DictReader(open(abl)))
        lines += ["", "## Cost of each framework variant (ds-flash, dev, 30 documents)", "",
                  "| setting | Trig-C | Arg-C (EM) | tokens (k) | relative to full |", "|---|---|---|---|---|"]
        full = next((float(r["tokens (k)"]) for r in rows if r["setting"] == "Full framework"), None)
        for r in rows:
            tk = float(r["tokens (k)"])
            if tk == 0:
                continue
            rel = f"{tk / full:.2f}x" if full else ""
            lines.append(f"| {r['setting']} | {r['Trig-C']} | {r['Arg-C (EM)']} | {tk} | {rel} |")
        lines.append("")
        lines.append("Entity guideline V1 run (all calls fresh); token counts of later re-runs are partly cached.")

    out = res_dir / f"cost_{a.split}.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nsaved {out}")
    plot(points, res_dir / f"fig_cost_vs_f1_{a.split}")


def plot(points, stem):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.ticker  # noqa: F401
    except ImportError:
        print("matplotlib not installed: pip install matplotlib  (figure skipped)")
        return
    ink, quiet, grid = "#0b0b0b", "#52514e", "#e4e3df"
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": quiet, "axes.labelcolor": ink,
                         "xtick.color": quiet, "ytick.color": quiet, "font.family": "DejaVu Sans"})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharex=True)
    models = [m for m in ORDER if any(p["model"] == m for p in points)]
    labels = []
    for ax, key, title in ((axes[0], "trig", "Trigger detection (Trig-C F1)"),
                           (axes[1], "arg", "Argument labelling (Arg-C F1, exact match)")):
        for m in models:
            b = next((p for p in points if p["model"] == m and p["method"] == BASE), None)
            f = next((p for p in points if p["model"] == m and p["method"] == FW), None)
            c, mk = COLORS.get(m, "#6250d6"), MARKERS.get(m, "o")
            if b and f:
                ax.annotate("", xy=(f["tok"], f[key]), xytext=(b["tok"], b[key]),
                            arrowprops=dict(arrowstyle="-|>", color=c, lw=1.5, shrinkA=6, shrinkB=6))
            if b:
                ax.scatter(b["tok"], b[key], s=55, marker=mk, facecolors="white", edgecolors=c, linewidths=2, zorder=3)
            if f:
                ax.scatter(f["tok"], f[key], s=90, marker=mk, color=c, edgecolors="white", linewidths=1.5, zorder=4)
                labels.append((ax, f["tok"], f[key], m))
        ax.set_title(title, loc="left", fontsize=11, color=ink)
        ax.set_xlabel("Tokens per document (thousand, input + output)")
        ax.grid(True, color=grid, lw=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.set_ylim(bottom=0)
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    axes[0].set_ylabel("F1 (%)")
    # direct labels in a column right of all points, nudged apart (>= 20 px), joined by thin leaders
    xmax = max(p["tok"] for p in points)
    for ax in axes:
        ax.set_xlim(0, xmax * 1.32)
    fig.canvas.draw()
    for ax in axes:
        items = sorted([(ax.transData.transform((x, y))[1], x, y, m) for a_, x, y, m in labels if a_ is ax],
                       reverse=True)
        last, lx = None, xmax * 1.09
        inv = ax.transData.inverted()
        for py, x, y, m in items:
            ty = py if last is None else min(py, last - 20)
            last = ty
            ly = inv.transform((0, ty))[1]
            ax.annotate(m, (x, y), xytext=(lx, ly), textcoords="data", color=ink, fontsize=9, va="center",
                        arrowprops=dict(arrowstyle="-", color=quiet, lw=0.6, shrinkA=2, shrinkB=6))
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker=MARKERS.get(m, "o"), color=COLORS.get(m), ls="", markersize=7, label=m) for m in models]
    handles += [Line2D([], [], marker="o", ls="", markerfacecolor="white", markeredgecolor=quiet, markersize=7,
                       label="zero-shot baseline (hollow)"),
                Line2D([], [], marker="o", ls="", color=quiet, markersize=7, label="NewsEE framework (filled)")]
    fig.legend(handles=handles, loc="lower center", ncol=len(handles), frameon=False, fontsize=9,
               bbox_to_anchor=(0.5, -0.02))
    tok_r, f1_r = [], []
    for m in models:
        b = next((p for p in points if p["model"] == m and p["method"] == BASE), None)
        f = next((p for p in points if p["model"] == m and p["method"] == FW), None)
        if b and f and b["tok"] and b["trig"]:
            tok_r.append(f["tok"] / b["tok"]); f1_r.append(f["trig"] / b["trig"])
    title = "NewsEE framework vs zero-shot baseline: F1 against token cost"
    if tok_r:
        title = (f"The framework uses {min(tok_r):.0f} to {max(tok_r):.0f}x the tokens of the baseline "
                 f"and raises trigger F1 {min(f1_r):.1f} to {max(f1_r):.1f}x")
    fig.suptitle(title, x=0.01, ha="left", fontsize=12, color=ink)
    fig.tight_layout(rect=(0, 0.07, 1, 0.95))
    for ext in ("png", "pdf"):
        fig.savefig(f"{stem}.{ext}", dpi=200, bbox_inches="tight", facecolor="white")
    print(f"saved {stem}.png / .pdf")


if __name__ == "__main__":
    main()
