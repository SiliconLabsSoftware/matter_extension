#!/usr/bin/env python3
"""
HTML Report - Generate a static, self-contained HTML comparison report.

The generated file embeds all data, styles and scripts so it can be shared
and opened in any web browser without additional files.
"""

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

CategoryData = Dict[str, List[Tuple[str, int]]]

_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Code Size Comparison - __TITLE__</title>
<style>
  body {
    background-color: #1e1e1e;
    color: #fff;
    font-family: "Segoe UI", Helvetica, Arial, sans-serif;
    margin: 0;
  }
  .toolbar {
    background-color: #2b2b2b;
    border-bottom: 1px solid #555;
    padding: 10px;
    font-size: 14pt;
    color: #d4d4d4;
  }
  .toolbar .meta { font-size: 11pt; color: #999; margin-top: 4px; }
  .content { padding: 10px; display: flex; flex-direction: column; gap: 5px; }
  .row { display: flex; gap: 10px; align-items: stretch; }
  .col-name { flex: 2; min-width: 200px; }
  .col { flex: 1; text-align: center; display: flex; align-items: center; justify-content: center; white-space: pre-line; }
  .total {
    background-color: #2b2b2b;
    border: 2px solid #1768EB;
    border-radius: 5px;
    padding: 10px;
    color: #1768EB;
    font-weight: bold;
  }
  .total .col-name { font-size: 16pt; padding: 10px; }
  .total .col { font-size: 15pt; padding: 5px; }
  .col-headers .col, .col-headers .col-name {
    color: #999; font-size: 12pt; padding: 0 10px; word-break: break-all;
  }
  .category { background-color: #3c3c3c; padding: 10px; }
  .category button {
    width: 100%;
    background-color: #3c3c3c;
    border: 1px solid #555;
    padding: 10px;
    text-align: left;
    font-size: 15pt;
    font-weight: bold;
    cursor: pointer;
    font-family: inherit;
  }
  .category button:hover { background-color: #4c4c4c; }
  .category button:active { background-color: #2c2c2c; }
  .category .col {
    color: #ccc; font-size: 14pt; padding: 5px;
    background-color: #2b2b2b; border: 1px solid #555;
  }
  .category .col.delta { font-weight: bold; }
  .details { padding: 5px 5px 5px 20px; display: flex; flex-direction: column; gap: 2px; }
  .obj {
    background-color: #2b2b2b;
    border-left: 2px solid #555;
    padding: 3px 5px;
    font-size: 13pt;
  }
  .obj:hover { background-color: #353535; }
  .obj .col-name { color: #d4d4d4; word-break: break-all; }
  .obj .col { color: #b4b4b4; }
  .obj .col.delta { font-weight: bold; }
  .pos { color: #F44336 !important; }
  .neg { color: #4CAF50 !important; }
  .zero { color: #999 !important; }
</style>
</head>
<body>
<div class="toolbar">
  <div>Code Size Comparison</div>
  <div class="meta">Generated __DATE__</div>
</div>
<div class="content" id="content"></div>
<script id="report-data" type="application/json">__DATA__</script>
<script>
(function () {
  "use strict";
  var data = JSON.parse(document.getElementById("report-data").textContent);
  var content = document.getElementById("content");
  var MAX_OBJECTS = 15;

  function fmt(n) { return n.toLocaleString("en-US"); }
  function sum(objs) { return objs.reduce(function (a, o) { return a + o[1]; }, 0); }
  function deltaClass(d) { return d > 0 ? "pos" : d < 0 ? "neg" : "zero"; }
  function deltaText(d) { return (d > 0 ? "+" : "") + fmt(d) + " bytes"; }
  function pct(v, t) { return t > 0 ? (v / t * 100).toFixed(1) : "0.0"; }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  var a = data.a.categories, b = data.b.categories;
  var names = Object.keys(a).concat(Object.keys(b).filter(function (k) { return !(k in a); }));
  names.sort();

  var totalA = 0, totalB = 0, countA = 0, countB = 0;
  Object.keys(a).forEach(function (k) { totalA += sum(a[k]); countA += a[k].length; });
  Object.keys(b).forEach(function (k) { totalB += sum(b[k]); countB += b[k].length; });
  var totalDelta = totalA - totalB;

  // Column headers identifying the two inputs
  var hdr = el("div", "row col-headers");
  hdr.appendChild(el("div", "col-name", ""));
  hdr.appendChild(el("div", "col", "Latest" + (data.a.name ? "\\n" + data.a.name : "")));
  hdr.appendChild(el("div", "col", "Reference" + (data.b.name ? "\\n" + data.b.name : "")));
  hdr.appendChild(el("div", "col", "Delta"));
  content.appendChild(hdr);

  var total = el("div", "row total");
  total.appendChild(el("div", "col-name", "TOTAL CODE SIZE (" + countA + "/" + countB + ")"));
  total.appendChild(el("div", "col", fmt(totalA) + " bytes\\n(100.0%)"));
  total.appendChild(el("div", "col", fmt(totalB) + " bytes\\n(100.0%)"));
  total.appendChild(el("div", "col " + deltaClass(totalDelta), deltaText(totalDelta)));
  content.appendChild(total);

  names.forEach(function (name, index) {
    var objsA = a[name] || [], objsB = b[name] || [];
    var sizeA = sum(objsA), sizeB = sum(objsB), delta = sizeA - sizeB;
    var color = index % 2 === 0 ? "#E57373" : "#CCCCCC";
    var label = name + " (" + objsA.length + "/" + objsB.length + ")";

    var wrapper = el("div");
    var header = el("div", "row category");
    var nameCol = el("div", "col-name");
    var btn = el("button", null, label);
    btn.style.color = color;
    btn.style.borderLeft = "3px solid " + color;
    nameCol.appendChild(btn);
    header.appendChild(nameCol);
    header.appendChild(el("div", "col", fmt(sizeA) + " bytes\\n(" + pct(sizeA, totalA) + "%)"));
    header.appendChild(el("div", "col", fmt(sizeB) + " bytes\\n(" + pct(sizeB, totalB) + "%)"));
    header.appendChild(el("div", "col delta " + deltaClass(delta), deltaText(delta)));
    wrapper.appendChild(header);

    var details = null;
    btn.addEventListener("click", function () {
      if (details) {
        wrapper.removeChild(details);
        details = null;
        btn.textContent = label;
        return;
      }
      var mapA = {}, mapB = {};
      objsA.forEach(function (o) { mapA[o[0]] = o[1]; });
      objsB.forEach(function (o) { mapB[o[0]] = o[1]; });
      var all = Object.keys(mapA);
      Object.keys(mapB).forEach(function (k) { if (!(k in mapA)) all.push(k); });
      var rows = all.map(function (k) {
        var sa = mapA[k] || 0, sb = mapB[k] || 0;
        return [k, sa, sb, sa - sb];
      });
      rows.sort(function (x, y) { return Math.abs(y[3]) - Math.abs(x[3]); });

      details = el("div", "details");
      rows.slice(0, MAX_OBJECTS).forEach(function (r) {
        var row = el("div", "row obj");
        row.appendChild(el("div", "col-name", r[0]));
        row.appendChild(el("div", "col", r[1] > 0 ? fmt(r[1]) + " bytes" : "-"));
        row.appendChild(el("div", "col", r[2] > 0 ? fmt(r[2]) + " bytes" : "-"));
        row.appendChild(el("div", "col delta " + deltaClass(r[3]), deltaText(r[3])));
        details.appendChild(row);
      });
      wrapper.appendChild(details);
      btn.textContent = "\\u25BC " + label;
    });

    content.appendChild(wrapper);
  });
})();
</script>
</body>
</html>
"""


def generate_diff_report(
    data_a: CategoryData,
    data_b: CategoryData,
    name_a: str,
    name_b: str,
    output_path: Path,
) -> Path:
    """
    Write a self-contained HTML comparison report.

    Args:
        data_a: Parsed category data for the first folder.
        data_b: Parsed category data for the second folder.
        name_a: Display name for the first folder.
        name_b: Display name for the second folder.
        output_path: Destination HTML file.

    Returns:
        Path of the written report.
    """
    payload = {
        "a": {"name": name_a, "categories": data_a},
        "b": {"name": name_b, "categories": data_b},
    }
    # Escape '<' so embedded strings can never terminate the <script> block.
    data_json = json.dumps(payload).replace("<", "\\u003c")

    report = (
        _TEMPLATE
        .replace("__TITLE__", html.escape(f"{name_a} vs {name_b}" if name_a or name_b else "Latest vs Reference"))
        .replace("__DATE__", html.escape(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        .replace("__DATA__", data_json)
    )

    output_path.write_text(report, encoding="utf-8")
    return output_path
