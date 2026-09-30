# Результаты

Как снимались точки — в {ref}`data-collection`.

```{include} ../../docs/generated/build_info.md
```

## Модель

Задержку $L$ при нагрузке $r$ оценивал прямой

```{math}
:label: eq-latency

L(r) = a r + b + \varepsilon
```

Коэффициенты в {eq}`eq-latency` — МНК. В экспериментальных прогонах
сравнивал со скользящим средним. Сглаживанием температурных рядов это
не заменить, для регрессионного анализа задержки хватило. Латентности
в хвосте не смотрел.

Модель грубая, для публикации сойдёт {cite}`hastie2009,kleinrock1975`.
Закон Литтла не проверял {cite}`little1961`.

## Как это считается

::::{grid} 2
:gutter: 2

:::{grid-item}
Скрипт читает csv, считает $a$, $b$ и RMSE. Если вход тот же — кэш.
См. {ref}`processing`.
:::

:::{grid-item}
```{image} img/pipeline.svg
:alt: схема
```

Рис. 1. csv → расчёт → страница.
:::
::::

## Сводка

<table>
  <caption>Таблица 1. Диапазоны по сериям замеров.</caption>
  <thead>
    <tr>
      <th rowspan="2">Серия</th>
      <th colspan="2">Нагрузка, RPS</th>
      <th colspan="2">Задержка, мс</th>
    </tr>
    <tr>
      <th>min</th>
      <th>max</th>
      <th>min</th>
      <th>max</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2">текущий прогон</td>
      <td>10</td>
      <td>85</td>
      <td>48.2</td>
      <td>141.8</td>
    </tr>
    <tr>
      <td>100</td>
      <td>150</td>
      <td>168.7</td>
      <td>271.5</td>
    </tr>
  </tbody>
</table>

## Графики

```{image} img/latency.png
:alt: matplotlib
```

Рис. 2. Точки и прямая МНК.

```{raw} html
<iframe src="_static/latency_plotly.html" width="100%" height="420" title="plotly"></iframe>
```

## Код

```{code-block} python
:linenos:

def fit(x, y):
    a, b = np.polyfit(x, y, 1)
    rmse = np.sqrt(np.mean((y - a * x - b) ** 2))
    return float(a), float(b), float(rmse)
```

## Шум

$\varepsilon$ считал гауссовским.[^noise]

[^noise]: На живом сервисе смотрел бы 95/99 квантили.

```{bibliography}
```
