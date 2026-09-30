#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[1]
DATA_CSV = ROOT / "data" / "experiment.csv"
DATA_VERSION = ROOT / "data" / "VERSION"
CACHE_DIR = ROOT / ".experiment-cache"
OUT_DIR = ROOT / "docs" / "generated"
ASSETS_DIR = ROOT / "docs" / "assets"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def git_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip()
    except Exception:
        return "unknown"


def cache_key() -> str:
    raw = (
        sha256_file(DATA_CSV)
        + sha256_file(Path(__file__))
        + DATA_VERSION.read_text(encoding="utf-8").strip()
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def write_scheme(path: Path, slope: float, rmse: float) -> None:
    path.write_text(
        f"""<svg xmlns="http://www.w3.org/2000/svg" width="480" height="180" viewBox="0 0 480 180">
  <rect width="480" height="180" fill="#f7f7f7" stroke="#ccc"/>
  <rect x="20" y="55" width="100" height="60" rx="6" fill="#e8f0fe"/>
  <text x="70" y="90" text-anchor="middle" font-size="14">CSV</text>
  <rect x="190" y="55" width="110" height="60" rx="6" fill="#fff3cd"/>
  <text x="245" y="82" text-anchor="middle" font-size="13">МНК</text>
  <text x="245" y="100" text-anchor="middle" font-size="11">a={slope:.3f}</text>
  <rect x="360" y="55" width="100" height="60" rx="6" fill="#e6f4ea"/>
  <text x="410" y="82" text-anchor="middle" font-size="13">сайт</text>
  <text x="410" y="100" text-anchor="middle" font-size="11">RMSE={rmse:.1f}</text>
  <path d="M120 85 H190" stroke="#333" stroke-width="2"/>
  <path d="M300 85 H360" stroke="#333" stroke-width="2"/>
</svg>
""",
        encoding="utf-8",
    )


def write_build_info(meta: dict, from_cache: bool, elapsed: float) -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    src = "кэш" if from_cache else "пересчёт"
    text = (
        f"Коммит `{git_commit()}`, сборка {stamp}, "
        f"датасет `{meta['version']}` "
        f"(`{meta['dataset_sha256'][:12]}…`), "
        f"{src} {elapsed:.3f} с.\n"
    )
    (OUT_DIR / "build_info.md").write_text(text, encoding="utf-8")
    (OUT_DIR / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def run() -> None:
    t0 = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    key = cache_key()
    cached = CACHE_DIR / key
    meta_path = cached / "meta.json"

    if meta_path.exists() and os.environ.get("FORCE_EXPERIMENT") != "1":
        for name in os.listdir(cached):
            src = cached / name
            if src.is_file():
                dest_dir = ASSETS_DIR if name == "pipeline.svg" else OUT_DIR
                shutil.copy2(src, dest_dir / name)
        elapsed = time.perf_counter() - t0
        print(f"cache hit {key} {elapsed:.3f}s")
        write_build_info(json.loads(meta_path.read_text(encoding="utf-8")), True, elapsed)
        return

    with DATA_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    x = np.array([float(r["rps"]) for r in rows])
    y = np.array([float(r["latency_ms"]) for r in rows])
    a, b = [float(v) for v in np.polyfit(x, y, 1)]
    rmse = float(np.sqrt(np.mean((y - a * x - b) ** 2)))
    corr = float(np.corrcoef(x, y)[0, 1])
    version = DATA_VERSION.read_text(encoding="utf-8").strip()

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(x, y, label="замеры")
    xs = np.linspace(x.min(), x.max(), 40)
    ax.plot(xs, a * xs + b, color="red", label=f"y = {a:.3f}x + {b:.1f}")
    ax.set_xlabel("RPS")
    ax.set_ylabel("латентность, мс")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    png_path = OUT_DIR / "latency.png"
    fig.savefig(png_path, dpi=130)
    plt.close(fig)

    pfig = go.Figure()
    pfig.add_trace(go.Scatter(x=x, y=y, mode="markers", name="замеры"))
    pfig.add_trace(go.Scatter(x=xs, y=a * xs + b, mode="lines", name="модель"))
    pfig.update_layout(
        title="Задержка vs нагрузка",
        xaxis_title="RPS",
        yaxis_title="мс",
        height=400,
        margin=dict(l=40, r=20, t=40, b=40),
        template="simple_white",
    )
    html_path = OUT_DIR / "latency_plotly.html"
    pfig.write_html(str(html_path), include_plotlyjs=True, full_html=True)

    table_path = OUT_DIR / "summary.csv"
    with table_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["метрика", "значение"])
        w.writerow(["n", len(rows)])
        w.writerow(["a", round(a, 4)])
        w.writerow(["b", round(b, 3)])
        w.writerow(["RMSE", round(rmse, 3)])
        w.writerow(["r", round(corr, 4)])

    write_scheme(ASSETS_DIR / "pipeline.svg", a, rmse)

    meta = {
        "version": version,
        "dataset_sha256": sha256_file(DATA_CSV),
        "n": len(rows),
        "a": a,
        "b": b,
        "rmse": rmse,
        "r": corr,
        "cache_key": key,
    }

    cached.mkdir(parents=True, exist_ok=True)
    for p in (png_path, html_path, table_path):
        shutil.copy2(p, cached / p.name)
    shutil.copy2(ASSETS_DIR / "pipeline.svg", cached / "pipeline.svg")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    elapsed = time.perf_counter() - t0
    print(f"cache miss {key} {elapsed:.3f}s a={a:.4f}")
    write_build_info(meta, False, elapsed)


if __name__ == "__main__":
    run()
