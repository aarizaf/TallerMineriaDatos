"""
Parcial 1 - Parte 1 - Mineria de Datos
Online Retail II - EDA, limpieza y construccion de baskets
"""
import re
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_PATH = "online_retail_II.xlsx"
OUT_DIR = "output"
results = {}

# ---------------------------------------------------------------------------
# 2. Cargar los datos
# ---------------------------------------------------------------------------
xls = pd.ExcelFile(DATA_PATH)
print("Hojas encontradas:", xls.sheet_names)
df = pd.concat([pd.read_excel(xls, sheet_name=s) for s in xls.sheet_names], ignore_index=True)

# Pregunta 2.1
results["2.1_a_columna_canastas"] = "Invoice"
results["2.1_b_columna_items"] = "StockCode"

# Pregunta 2.2
results["2.2_filas_originales"] = int(len(df))

# Pregunta 2.3
nulls_invoice_or_stock = df["Invoice"].isna() | df["StockCode"].isna()
results["2.3_a_nulos_invoice_o_stockcode"] = int(nulls_invoice_or_stock.sum())

invoice_str = df["Invoice"].astype(str)
cancel_mask = invoice_str.str.startswith("C")
results["2.3_b_invoices_empiezan_con_C"] = int(cancel_mask.sum())

pattern = re.compile(r"^\d{5}[A-Za-z]?$")
stockcode_str = df["StockCode"].astype(str)
non_matching_mask = ~stockcode_str.str.match(pattern)
non_matching_unique = sorted(stockcode_str[non_matching_mask].unique().tolist())
results["2.3_c_stockcodes_no_patron_count"] = len(non_matching_unique)
results["2.3_c_stockcodes_no_patron_valores"] = non_matching_unique

print(json.dumps(results, indent=2, ensure_ascii=False, default=str))

# ---------------------------------------------------------------------------
# 3. Limpieza de datos
# ---------------------------------------------------------------------------
df_clean = df.copy()
df_clean["Invoice"] = df_clean["Invoice"].astype(str)
df_clean["StockCode"] = df_clean["StockCode"].astype(str)

df_clean = df_clean[~df_clean["Invoice"].str.startswith("C")]
df_clean = df_clean[df_clean["Quantity"] > 0]

non_product_codes = {"POST", "D", "DOT", "M", "S", "AMAZONFEE",
                      "BANK CHARGES", "PADS", "CRUK", "C2", "m"}
df_clean = df_clean[~df_clean["StockCode"].isin(non_product_codes)]
df_clean = df_clean[df_clean["StockCode"].str.len() != 1]
df_clean = df_clean[df_clean["Customer ID"].notna()]

results["3_filas_tras_limpieza"] = int(len(df_clean))
results["3_stockcodes_unicos"] = int(df_clean["StockCode"].nunique())
results["3_invoices_unicos"] = int(df_clean["Invoice"].nunique())

print("Verificacion limpieza:",
      results["3_filas_tras_limpieza"],
      results["3_stockcodes_unicos"],
      results["3_invoices_unicos"])

assert results["3_filas_tras_limpieza"] == 802742, "No coincide el numero de filas esperado"
assert results["3_stockcodes_unicos"] == 4624, "No coincide el numero de StockCodes esperado"
assert results["3_invoices_unicos"] == 36644, "No coincide el numero de Invoices esperado"

df_clean.to_csv(f"{OUT_DIR}/clean_data.csv", index=False)

# ---------------------------------------------------------------------------
# 4. Construir los baskets
# ---------------------------------------------------------------------------
baskets_series = df_clean.groupby("Invoice")["StockCode"].apply(lambda s: frozenset(s))
results["4_total_canastas"] = int(len(baskets_series))
assert results["4_total_canastas"] == 36644, "No coincide el numero de canastas esperado"

basket_sizes = baskets_series.apply(len)

plt.figure(figsize=(10, 6))
plt.hist(basket_sizes, bins=50, color="#4C72B0", edgecolor="black")
plt.title("Distribucion del tamano de las canastas (Online Retail II)")
plt.xlabel("Cantidad de items por canasta")
plt.ylabel("Frecuencia (numero de canastas)")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/basket_size_histogram.png", dpi=150)
plt.close()

results["4_basket_size_min"] = int(basket_sizes.min())
results["4_basket_size_max"] = int(basket_sizes.max())
results["4_basket_size_mean"] = float(basket_sizes.mean())
results["4_basket_size_median"] = float(basket_sizes.median())

baskets_df = pd.DataFrame({
    "Invoice": baskets_series.index,
    "Items": baskets_series.apply(lambda fs: ",".join(sorted(fs)))
})
baskets_df.to_csv(f"{OUT_DIR}/baskets.csv", index=False)

with open(f"{OUT_DIR}/results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False, default=str)

print("\nOK - resultados guardados en output/results.json")
