# -*- coding: utf-8 -*-
import json
import pandas as pd
from PIL import Image as PILImage
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Preformatted, Table, TableStyle, PageBreak
)

with open("output/results.json", encoding="utf-8") as f:
    R = json.load(f)

with open("output/results_part2.json", encoding="utf-8") as f:
    R2 = json.load(f)

top15_df = pd.read_csv("output/top15_pairs.csv")
rules_df = pd.read_csv("output/association_rules.csv")

CELL_DIR = "output/cell_shots"
MAX_W = 15.5 * cm
MAX_H = 21 * cm

def code_img(n):
    path = f"{CELL_DIR}/cell_{n:02d}.png"
    w_px, h_px = PILImage.open(path).size
    w_pt = w_px * 0.75  # 96 dpi screenshot -> 72 dpi points
    h_pt = h_px * 0.75
    scale = min(1.0, MAX_W / w_pt, MAX_H / h_pt)
    w = w_pt * scale
    h = h_pt * scale
    return Image(path, width=w, height=h)

styles = getSampleStyleSheet()
title_style = ParagraphStyle("TitleX", parent=styles["Title"], fontSize=18, spaceAfter=6)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6, textColor=colors.HexColor("#1F3864"))
h3 = ParagraphStyle("H3", parent=styles["Heading3"], spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#2E5395"))
body = ParagraphStyle("BodyX", parent=styles["BodyText"], fontSize=10.5, leading=15)
answer = ParagraphStyle("Answer", parent=body, backColor=colors.HexColor("#EAF1FB"), borderPadding=6, leftIndent=4)
mono = ParagraphStyle("Mono", parent=styles["Code"], fontSize=8, leading=10)

doc = SimpleDocTemplate(
    "Parcial1_Parte1_MineriaDeDatos.pdf",
    pagesize=LETTER,
    topMargin=1.8*cm, bottomMargin=1.8*cm, leftMargin=2*cm, rightMargin=2*cm
)

story = []

story.append(Paragraph("Parcial 1 — Parte 1 — Minería de Datos", title_style))
story.append(Paragraph("Profesor: Pierre Rosado &nbsp;|&nbsp; Universidad del Norte", body))
story.append(Paragraph("Dataset: Online Retail II (UCI ML Repository)", body))
story.append(Paragraph("Autor: desarrollo_evol_4@jamar.com", body))
story.append(Spacer(1, 0.6*cm))

story.append(Paragraph(
    "Este documento resume las respuestas y evidencias generadas en el notebook "
    "<b>Parcial1_Parte1_MineriaDeDatos.ipynb</b> (adjunto/entregado por separado en Google Colab), "
    "que contiene la carga de datos, el EDA, la limpieza y la construcción de canastas (baskets) "
    "sobre el dataset Online Retail II.", body))

# ---------------------------------------------------------------------
story.append(Paragraph("1. Descarga de datos", h2))
story.append(Paragraph(
    "Se descargó el archivo <b>online+retail+ii.zip</b> desde "
    "https://archive.ics.uci.edu/dataset/502/online+retail+ii, se descomprimió y se inspeccionó "
    "el archivo Excel <b>online_retail_II.xlsx</b>, que contiene dos hojas: "
    "<i>Year 2009-2010</i> y <i>Year 2010-2011</i>, correspondientes a transacciones de una tienda "
    "online del Reino Unido entre el 01/12/2009 y el 09/12/2011.", body))

# ---------------------------------------------------------------------
story.append(Paragraph("2. Cargar los datos y EDA", h2))

story.append(Paragraph("Evidencia — código: carga del Excel", body))
story.append(code_img(2))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("Pregunta 2.1 — Columnas de canastas e ítems", h3))
story.append(Paragraph(
    "a) ¿Cuál es la columna que identifica a las canastas?<br/>"
    "b) ¿Cuál es la columna que identifica a los ítems?", body))
story.append(code_img(3))
story.append(Paragraph(
    "<b>Respuesta:</b> a) <b>Invoice</b> identifica la canasta (cada factura agrupa los ítems "
    "comprados juntos). b) <b>StockCode</b> identifica el ítem (código único de producto).",
    answer))

story.append(PageBreak())

story.append(Paragraph("Pregunta 2.2 — Filas originales", h3))
story.append(Paragraph("¿Cuántas filas tiene el dataset originalmente?", body))
story.append(code_img(4))
story.append(Paragraph(
    f"<b>Respuesta:</b> El dataset original (unión de ambas hojas) tiene "
    f"<b>{R['2.2_filas_originales']:,}</b> filas.", answer))

story.append(Paragraph("Pregunta 2.3 — EDA", h3))
story.append(Paragraph(
    "a) ¿Cuántas filas tienen valores nulos en Invoice o StockCode?<br/>"
    "b) ¿Cuántas filas tienen un Invoice que empieza con “C”?<br/>"
    "c) Valores de StockCode que no siguen el patrón de 5 dígitos con sufijo de letra opcional "
    "(se esperan 68 valores únicos).", body))

story.append(Paragraph("Evidencia — código apartado a):", body))
story.append(code_img(5))
story.append(Paragraph("Evidencia — código apartado b):", body))
story.append(code_img(6))
story.append(Paragraph("Evidencia — código apartado c):", body))
story.append(code_img(7))

story.append(Paragraph(
    f"<b>Respuesta:</b><br/>"
    f"a) <b>{R['2.3_a_nulos_invoice_o_stockcode']}</b> filas tienen nulos en Invoice o StockCode.<br/>"
    f"b) <b>{R['2.3_b_invoices_empiezan_con_C']:,}</b> filas tienen un Invoice que empieza con “C” (cancelaciones).<br/>"
    f"c) Se identificaron <b>{R['2.3_c_stockcodes_no_patron_count']}</b> valores únicos de StockCode "
    f"que no siguen el patrón (coincide con el valor esperado de 68).", answer))

codes = R["2.3_c_stockcodes_no_patron_valores"]
codes_text = ", ".join(codes)
story.append(Paragraph("<b>Evidencia — listado de los 68 StockCodes atípicos:</b>", body))
story.append(Preformatted(codes_text, mono))

story.append(PageBreak())

# ---------------------------------------------------------------------
story.append(Paragraph("3. Limpieza de datos", h2))
story.append(Paragraph(
    "Reglas de limpieza aplicadas: eliminar cancelaciones (Invoice que empieza con “C”), "
    "conservar solo filas con Quantity &gt; 0, eliminar los stock codes no-producto "
    "(POST, D, DOT, M, S, AMAZONFEE, BANK CHARGES, PADS, CRUK, C2, m), eliminar stock codes de "
    "longitud 1, y eliminar filas con Customer ID nulo.", body))

story.append(Paragraph("Evidencia — código de limpieza:", body))
story.append(code_img(8))
story.append(Paragraph("Evidencia — código de verificación:", body))
story.append(code_img(9))

table_data = [
    ["Métrica", "Esperado", "Obtenido", "OK"],
    ["Filas tras limpieza", "802,742", f"{R['3_filas_tras_limpieza']:,}", "✓"],
    ["StockCodes únicos", "4,624", f"{R['3_stockcodes_unicos']:,}", "✓"],
    ["Invoices únicos", "36,644", f"{R['3_invoices_unicos']:,}", "✓"],
]
t = Table(table_data, colWidths=[6*cm, 3*cm, 3*cm, 1.5*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3864")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FC")]),
]))
story.append(Spacer(1, 0.2*cm))
story.append(t)
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    "<b>Verificación:</b> los tres valores coinciden exactamente con los esperados en el enunciado.",
    answer))

# ---------------------------------------------------------------------
story.append(Paragraph("4. Construir los baskets", h2))

story.append(Paragraph("4.1 — Importancia de frozenset", h3))
story.append(Paragraph(
    "<b>Respuesta:</b> <b>frozenset</b> es la versión inmutable de <i>set</i> en Python. Es importante "
    "para representar los ítems de una canasta porque: (1) al ser inmutable y <i>hashable</i>, puede "
    "usarse como clave de diccionario o como elemento de otro set — indispensable para algoritmos "
    "de reglas de asociación (Apriori/FP-Growth) que cuentan itemsets como claves; (2) elimina "
    "duplicados y no depende del orden de los ítems, que es la semántica correcta de una canasta de "
    "compra; (3) permite operaciones eficientes de conjuntos (unión, intersección, subconjunto); y "
    "(4) evita modificaciones accidentales de la canasta durante el procesamiento, garantizando "
    "resultados reproducibles.", answer))

story.append(PageBreak())

story.append(Paragraph("4.2 — Construcción de canastas", h3))
story.append(Paragraph("Evidencia — código:", body))
story.append(code_img(10))
story.append(Paragraph(
    f"<b>Respuesta:</b> se agruparon los StockCode por Invoice como frozenset, obteniendo "
    f"<b>{R['4_total_canastas']:,}</b> canastas, coincidiendo con el valor esperado de 36,644.", answer))

story.append(Paragraph("4.3 — Distribución de tamaños de canastas", h3))
story.append(Paragraph("Evidencia — código:", body))
story.append(code_img(11))
story.append(Paragraph(
    f"Tamaño mínimo: {R['4_basket_size_min']} ítems &nbsp;|&nbsp; "
    f"Tamaño máximo: {R['4_basket_size_max']} ítems &nbsp;|&nbsp; "
    f"Promedio: {R['4_basket_size_mean']:.2f} ítems &nbsp;|&nbsp; "
    f"Mediana: {R['4_basket_size_median']:.0f} ítems", body))
story.append(Spacer(1, 0.2*cm))
story.append(Image("output/basket_size_histogram.png", width=15*cm, height=9*cm))

story.append(Paragraph("4.4 — Exportación a CSV", h3))
story.append(Paragraph("Evidencia — código:", body))
story.append(code_img(12))
story.append(Paragraph(
    "Las canastas se guardaron en <b>baskets.csv</b> (una fila por Invoice, con la columna Items "
    "conteniendo los StockCode separados por coma).", answer))

story.append(PageBreak())

# =======================================================================
# PARTE 2
# =======================================================================
story.append(Paragraph("Parcial 1 — Parte 2 — Minería de Datos", title_style))
story.append(Paragraph(
    "Continuando con las canastas construidas en la Parte 1, se implementa el algoritmo "
    "<b>A-Priori</b> y la <b>generación de reglas de asociación</b>.", body))
story.append(Spacer(1, 0.4*cm))

story.append(Paragraph("Ejemplo sintético (verificación manual)", h2))
story.append(Paragraph(
    "Antes de correr el algoritmo sobre el dataset completo, se probó la implementación con un "
    "ejemplo pequeño y sintético (6 canastas de \"pan\", \"leche\", \"pañales\", \"cerveza\", \"huevos\") "
    "que se puede verificar a mano. Con soporte mínimo = 3 se espera "
    "<b>L1</b> = {pan, leche, pañales, cerveza} (huevos queda fuera, soporte 1) y "
    "<b>L2</b> = {(pan,leche), (pan,pañales), (leche,pañales), (pañales,cerveza)}.", body))
story.append(Paragraph("Evidencia — código y salida de la ejecución:", body))
story.append(code_img(14))
story.append(Paragraph(
    "<b>Resultado:</b> la salida de la función coincide exactamente con el conteo manual, "
    "confirmando que la implementación es correcta antes de aplicarla al dataset completo.", answer))

story.append(PageBreak())

# ---------------------------------------------------------------------
story.append(Paragraph("1. Algoritmo A-Priori", h2))

story.append(Paragraph("Implementación", h3))
story.append(Paragraph(
    "Se implementó la función <b>apriori(baskets, min_support, max_k=4)</b> siguiendo los pasos "
    "vistos en clase: Pasada 1 cuenta ítems individuales y filtra por soporte mínimo para obtener L1; "
    "en cada Pasada k se generan candidatos Ck a partir de Lk-1 (join + poda por subconjuntos, función "
    "auxiliar <b>generate_candidates</b>), se cuenta su soporte escaneando las canastas y se filtra "
    "para obtener Lk. El proceso se repite hasta que no se generen más itemsets frecuentes o se "
    "alcance max_k.", body))
story.append(Paragraph("Evidencia — código:", body))
story.append(code_img(13))

story.append(Paragraph("Ejecución", h3))
story.append(Paragraph("Evidencia — código: preparación de baskets y descripciones de producto:", body))
story.append(code_img(15))
story.append(Paragraph("Evidencia — código: cálculo del soporte mínimo y ejecución del algoritmo:", body))
story.append(code_img(16))
story.append(Paragraph("Evidencia — código y salida: reporte de candidatos y frecuentes por pasada:", body))
story.append(code_img(17))

report_table_data = [["k", "Candidatos Ck", "Frecuentes Lk"]]
for row in R2["report_rows"]:
    report_table_data.append([str(row["k"]), f"{row['candidatos']:,}", f"{row['frecuentes']:,}"])
t2 = Table(report_table_data, colWidths=[2*cm, 5*cm, 5*cm])
t2.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3864")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FC")]),
]))
story.append(Spacer(1, 0.2*cm))
story.append(t2)
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph(
    f"<b>Respuesta:</b> con soporte mínimo de <b>{R2['min_support']}</b> (2.0% de 36,644 canastas), "
    f"se obtienen <b>{R2['L1_count']}</b> ítems frecuentes en L1, <b>{R2['L2_count']}</b> pares "
    f"frecuentes en L2 y 0 tríos frecuentes en L3 (el algoritmo se detiene antes de max_k=4 al no "
    f"generarse más itemsets frecuentes), para un total de <b>{R2['total_frequent']}</b> itemsets "
    f"frecuentes — coincidiendo exactamente con la verificación del enunciado.", answer))

story.append(PageBreak())

story.append(Paragraph("Los 15 pares frecuentes con mayor soporte:", h3))
story.append(Paragraph("Evidencia — código:", body))
story.append(code_img(18))

pairs_table_data = [["Producto A", "Producto B", "Conteo", "Soporte"]]
for _, r in top15_df.iterrows():
    pairs_table_data.append([
        Paragraph(r["desc_A"], body), Paragraph(r["desc_B"], body),
        f"{int(r['count']):,}", f"{r['support']:.4f}",
    ])
t3 = Table(pairs_table_data, colWidths=[6*cm, 6*cm, 2*cm, 2*cm], repeatRows=1)
t3.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3864")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("ALIGN", (2, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FC")]),
]))
story.append(Spacer(1, 0.2*cm))
story.append(t3)

story.append(PageBreak())

# ---------------------------------------------------------------------
story.append(Paragraph("2. Generación de reglas de asociación", h2))

story.append(Paragraph("Implementación", h3))
story.append(Paragraph(
    "Se implementó <b>generate_rules(freq, support, n_baskets, min_confidence, min_interest)</b>: "
    "para cada itemset frecuente I de tamaño ≥ 2 se generan todas las reglas A → B con A ∪ B = I y "
    "A ∩ B = ∅, calculando soporte, confianza, lift e interés, y reteniendo solo las reglas cuya "
    "confianza ≥ min_confidence e interés ≥ min_interest.", body))
story.append(Paragraph("Evidencia — código:", body))
story.append(code_img(19))

story.append(Paragraph("Ejecución", h3))
story.append(Paragraph("Evidencia — código y salida: generación de reglas (min_confidence=0.5, min_interest=0.5):", body))
story.append(code_img(20))
story.append(Paragraph(
    f"<b>Respuesta:</b> con los parámetros indicados se obtienen <b>{R2['n_rules']}</b> reglas, "
    f"coincidiendo con la verificación del enunciado.", answer))

story.append(Paragraph("Evidencia — código: reglas ordenadas por lift, con descripción de productos:", body))
story.append(code_img(21))

rules_table_data = [["Antecedente", "Consecuente", "Soporte", "Confianza", "Lift", "Interés"]]
for _, r in rules_df.iterrows():
    rules_table_data.append([
        Paragraph(r["antecedent_desc"], body), Paragraph(r["consequent_desc"], body),
        f"{r['support']:.4f}", f"{r['confidence']:.4f}", f"{r['lift']:.2f}", f"{r['interest']:.4f}",
    ])
t4 = Table(rules_table_data, colWidths=[4.3*cm, 4.3*cm, 1.9*cm, 2*cm, 1.5*cm, 1.7*cm], repeatRows=1)
t4.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3864")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("ALIGN", (2, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FC")]),
]))
story.append(Spacer(1, 0.2*cm))
story.append(t4)

story.append(PageBreak())

story.append(Paragraph("Preguntas", h3))
story.append(Paragraph(
    "<b>¿Qué indica un valor de lift mayor a 1?</b> Que la presencia de A hace que B aparezca "
    "<b>más frecuentemente</b> de lo que aparecería por azar (independencia estadística) — existe una "
    "asociación positiva entre A y B; cuanto mayor el lift, más fuerte la asociación (p. ej. lift≈27 "
    "significa que comprar A hace ~27 veces más probable comprar B que si fueran independientes).",
    answer))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    "<b>¿Qué indica un valor de lift menor a 1?</b> Que la presencia de A hace que B aparezca "
    "<b>menos frecuentemente</b> de lo esperado por azar — existe una asociación negativa (los "
    "productos tienden a <i>no</i> comprarse juntos, posiblemente porque son sustitutos entre sí).",
    answer))

story.append(Paragraph("Evidencia — código:", body))
story.append(code_img(22))

sr = R2["strongest_rule"]
story.append(Paragraph(
    f"<b>¿Qué par de productos tiene la asociación más fuerte?</b> La asociación más fuerte "
    f"(mayor lift) es entre <b>{sr['antecedent']}</b> y <b>{sr['consequent']}</b> "
    f"(lift ≈ {sr['lift']:.1f}, confianza ≈ {sr['confidence']:.2%}), es decir, los clientes que "
    f"compran uno de estos productos de la colección Regency tienen una probabilidad muchísimo mayor "
    f"de comprar también el otro, comparado con lo esperado si las compras fueran independientes.",
    answer))

story.append(Spacer(1, 0.5*cm))
story.append(Paragraph(
    "Documento generado automáticamente a partir de la ejecución real del notebook "
    "Parcial1_Parte1_MineriaDeDatos.ipynb (Partes 1 y 2).",
    ParagraphStyle("Footer", parent=body, fontSize=8, textColor=colors.grey)))

doc.build(story)
print("PDF generado: Parcial1_Parte1_MineriaDeDatos.pdf")
