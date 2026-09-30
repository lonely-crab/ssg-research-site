# ssg-research-site

Сайт с результатами небольшого прогона: задержка API vs RPS.
Сборка — MkDocs Material, та же страница ещё раз на Sphinx (`generators/sphinx`).

Текст — [CC BY 4.0](LICENSE-CONTENT), код — [MIT](LICENSE).

[![ci](https://github.com/lonely-crab/ssg-research-site/actions/workflows/ci.yml/badge.svg)](https://github.com/lonely-crab/ssg-research-site/actions)

https://lonely-crab.github.io/ssg-research-site/

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make experiment
make serve
```

`make sphinx` — вторая вёрстка. После пуша в `main` GitHub Actions выкладывает Pages.
Если поменять `data/experiment.csv`, графики пересчитаются при сборке.
