# -*- coding: utf-8 -*-
import os
import subprocess
import nbformat
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT_DIR = "output/cell_shots"
os.makedirs(OUT_DIR, exist_ok=True)

nb = nbformat.read("Parcial1_Parte1_MineriaDeDatos.ipynb", as_version=4)
lexer = PythonLexer()
formatter = HtmlFormatter(style="default", noclasses=True, nowrap=False)

HTML_TEMPLATE = """<!doctype html>
<html><head><meta charset="utf-8">
<style>
  body {{ margin:0; padding:0; background:white; font-family: Consolas, Menlo, monospace; }}
  .cellbox {{
    border: 1px solid #cfd8dc;
    border-left: 4px solid #4C72B0;
    border-radius: 4px;
    width: fit-content;
    max-width: 1400px;
  }}
  .prompt {{
    background:#f5f7fa;
    color:#4C72B0;
    font-size:13px;
    padding:4px 10px;
    border-bottom:1px solid #e0e6ec;
    font-family: Consolas, Menlo, monospace;
  }}
  pre {{
    margin:0;
    padding:10px 14px;
    font-size:14px;
    line-height:1.4;
    white-space: pre;
  }}
</style></head>
<body>
<div class="cellbox">
  <div class="prompt">In [{n}]:</div>
  {code_html}
</div>
</body></html>
"""

code_cells = [c for c in nb.cells if c.cell_type == "code" and c.source.strip()]
print(f"Total code cells: {len(code_cells)}")

paths = []
for i, cell in enumerate(code_cells, start=1):
    code_html = highlight(cell.source, lexer, formatter)
    html = HTML_TEMPLATE.format(n=i, code_html=code_html)
    html_path = os.path.join(OUT_DIR, f"cell_{i:02d}.html")
    png_path = os.path.join(OUT_DIR, f"cell_{i:02d}.png")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    n_lines = cell.source.count("\n") + 2
    width = 1300
    height = max(90, 60 + n_lines * 22)

    subprocess.run([
        EDGE, "--headless", "--disable-gpu",
        f"--screenshot={os.path.abspath(png_path)}",
        f"--window-size={width},{height}",
        os.path.abspath(html_path)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    paths.append(png_path)
    print("captured", png_path)

print("Listo:", len(paths), "capturas generadas")
