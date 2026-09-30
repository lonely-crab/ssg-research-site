#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "measurements" / "build.md"
EXTERNAL = re.compile(r"https?://[^\s\"'<>]+")


def page_stats(html: Path) -> tuple[int, int]:
    text = html.read_text(encoding="utf-8", errors="replace")
    cdn = {
        u
        for u in EXTERNAL.findall(text)
        if any(s in u for s in ("cdn.", "unpkg", "jsdelivr", "cdnjs", "googleapis"))
    }
    return html.stat().st_size, len(cdn)


def timed(cmd: list[str], cwd: Path) -> float:
    t0 = time.perf_counter()
    subprocess.check_call(cmd, cwd=cwd)
    return time.perf_counter() - t0


def main() -> None:
    rows = []
    t = timed(["make", "build"], ROOT)
    page = ROOT / "site" / "experiment" / "index.html"
    sz, n = page_stats(page)
    rows.append(("MkDocs Material", t, sz, n, "site/experiment/index.html"))

    sphinx = ROOT / "generators" / "sphinx"
    t = timed(["make", "html"], sphinx)
    page = sphinx / "_build" / "html" / "experiment.html"
    sz, n = page_stats(page)
    rows.append(("Sphinx + MyST", t, sz, n, "generators/sphinx/_build/html/experiment.html"))

    lines = [
        "# Сравнение сборок",
        "",
        "| генератор | время, с | HTML, байт | внешние URL | файл |",
        "|---|---:|---:|---:|---|",
    ]
    for name, t, sz, n, path in rows:
        lines.append(f"| {name} | {t:.2f} | {sz} | {n} | `{path}` |")
    lines += [
        "",
        "Lighthouse гонял отдельно в Chrome.",
        "",
        "| генератор | не вышло из коробки | что сделал |",
        "|---|---|---|",
        "| MkDocs | объединение ячеек в md-таблицах | html `<table>` |",
        "| MkDocs | номера формул | MathJax `tags: ams` |",
        "| Sphinx | plotly не попадал в `_build` | копия в `_static` из Makefile |",
        "",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
