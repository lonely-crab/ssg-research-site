# Сравнение сборок

| генератор | время, с | HTML, байт | внешние URL | файл |
|---|---:|---:|---:|---|
| MkDocs Material | 1.12 | 24460 | 0 | `site/experiment/index.html` |
| Sphinx + MyST | 0.73 | 23218 | 1 | `generators/sphinx/_build/html/experiment.html` |

Lighthouse гонял отдельно в Chrome.

| генератор | не вышло из коробки | что сделал |
|---|---|---|
| MkDocs | объединение ячеек в md-таблицах | html `<table>` |
| MkDocs | номера формул | MathJax `tags: ams` |
| Sphinx | plotly не попадал в `_build` | копия в `_static` из Makefile |

