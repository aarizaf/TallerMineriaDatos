# -*- coding: utf-8 -*-
"""
Parcial 1 - Parte 2 - Mineria de Datos
Algoritmo A-Priori y generacion de reglas de asociacion
"""
import json
import math
from collections import defaultdict
from itertools import combinations

import pandas as pd

OUT_DIR = "output"
results2 = {}

# ---------------------------------------------------------------------------
# Cargar baskets de la Parte 1
# ---------------------------------------------------------------------------
baskets_df = pd.read_csv(f"{OUT_DIR}/baskets.csv")
baskets = [frozenset(items.split(",")) for items in baskets_df["Items"]]
n_baskets = len(baskets)
print("Numero de canastas:", n_baskets)

# Mapeo StockCode -> Descripcion (la mas frecuente para ese StockCode)
clean_df = pd.read_csv(f"{OUT_DIR}/clean_data.csv", usecols=["StockCode", "Description"], dtype={"StockCode": str})
desc_map = (
    clean_df.groupby("StockCode")["Description"]
    .agg(lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0])
    .to_dict()
)

def describe(item):
    return desc_map.get(item, item)

def describe_itemset(iset):
    return " + ".join(sorted(describe(i) for i in iset))


# ---------------------------------------------------------------------------
# 1. Algoritmo A-Priori
# ---------------------------------------------------------------------------
def generate_candidates(prev_itemsets, k):
    """Genera candidatos Ck a partir de Lk-1 (join + poda por subconjuntos)."""
    prev_set = set(prev_itemsets)
    sorted_prev = [tuple(sorted(iset)) for iset in prev_itemsets]
    candidates = set()
    n = len(sorted_prev)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = sorted_prev[i], sorted_prev[j]
            if a[: k - 2] == b[: k - 2]:
                candidate = frozenset(a) | frozenset(b)
                if len(candidate) == k:
                    if all(frozenset(c) in prev_set for c in combinations(candidate, k - 1)):
                        candidates.add(candidate)
    return candidates


def apriori(baskets, min_support, max_k=4):
    """
    Algoritmo A-Priori.

    baskets: lista de frozensets
    min_support: soporte minimo absoluto (numero de baskets)
    max_k: tamano maximo de itemsets a buscar

    Retorna: dict {k: {frozenset: count}}
    """
    freq = {}
    candidates_count = {}

    # Pasada 1: contar items individuales
    item_counts = defaultdict(int)
    for b in baskets:
        for item in b:
            item_counts[item] += 1
    C1 = {frozenset([item]): cnt for item, cnt in item_counts.items()}
    candidates_count[1] = len(C1)

    L1 = {iset: cnt for iset, cnt in C1.items() if cnt >= min_support}
    freq[1] = L1

    k = 2
    Lk_minus_1 = L1
    while Lk_minus_1 and k <= max_k:
        prev_itemsets = list(Lk_minus_1.keys())
        items_in_prev = set()
        for iset in prev_itemsets:
            items_in_prev |= iset

        Ck = generate_candidates(prev_itemsets, k)
        candidates_count[k] = len(Ck)
        if not Ck:
            break

        counts = defaultdict(int)
        for b in baskets:
            reduced = b & items_in_prev
            if len(reduced) < k:
                continue
            for combo in combinations(sorted(reduced), k):
                fs = frozenset(combo)
                if fs in Ck:
                    counts[fs] += 1

        Lk = {iset: cnt for iset, cnt in counts.items() if cnt >= min_support}
        freq[k] = Lk

        Lk_minus_1 = Lk
        k += 1

    return freq, candidates_count


# Ejecucion
min_support = math.floor(0.02 * n_baskets)
print("Soporte minimo absoluto (2% de", n_baskets, "):", min_support)
results2["min_support"] = min_support

freq, candidates_count = apriori(baskets, min_support, max_k=4)

print("\nReporte por pasada:")
report_rows = []
total_frequent = 0
for k in sorted(set(list(candidates_count.keys()) + list(freq.keys()))):
    n_candidates = candidates_count.get(k, 0)
    n_frequent = len(freq.get(k, {}))
    total_frequent += n_frequent
    print(f"  k={k}: candidatos C{k}={n_candidates}, frecuentes L{k}={n_frequent}")
    report_rows.append({"k": k, "candidatos": n_candidates, "frecuentes": n_frequent})

print("\nTotal de itemsets frecuentes:", total_frequent)
results2["report_rows"] = report_rows
results2["total_frequent"] = total_frequent
results2["L1_count"] = len(freq.get(1, {}))
results2["L2_count"] = len(freq.get(2, {}))

assert min_support == 732
assert results2["L1_count"] == 196
assert results2["L2_count"] == 31
assert total_frequent == 227
print("\nVerificacion OK: soporte minimo 732 | L1=196 | L2=31 | total=227")

# support dict unificado (para generar reglas)
support = {}
for k, itemsets in freq.items():
    support.update(itemsets)

# Top 15 pares frecuentes con mayor soporte
pairs = freq.get(2, {})
top15 = sorted(pairs.items(), key=lambda x: x[1], reverse=True)[:15]
top15_rows = []
for iset, cnt in top15:
    items = sorted(iset)
    top15_rows.append({
        "item_A": items[0], "desc_A": describe(items[0]),
        "item_B": items[1], "desc_B": describe(items[1]),
        "count": cnt, "support": cnt / n_baskets,
    })
top15_df = pd.DataFrame(top15_rows)
print("\nTop 15 pares frecuentes:")
print(top15_df.to_string(index=False))
top15_df.to_csv(f"{OUT_DIR}/top15_pairs.csv", index=False)


# ---------------------------------------------------------------------------
# 2. Generacion de reglas de asociacion
# ---------------------------------------------------------------------------
def generate_rules(freq, support, n_baskets, min_confidence=0.5, min_interest=0.5):
    """Genera reglas de asociacion A -> B a partir de itemsets frecuentes.

    Parametros
    ----------
    freq : dict {k: {frozenset: int}}
        Itemsets frecuentes agrupados por tamano k.
    support : dict {frozenset: int}
        Conteo absoluto para todo itemset frecuente (incluyendo singletons).
    n_baskets : int
        Numero total de canastas.
    min_confidence : float, default 0.5
        Umbral minimo de confianza.
    min_interest : float, default 0.5
        Umbral minimo de interes.

    Solo se retornan reglas cuya confianza >= min_confidence e interes >= min_interest.

    Retorna: pd.DataFrame con columnas:
        antecedent, consequent, support, confidence, lift, interest.
    """
    rows = []
    for k, itemsets in freq.items():
        if k < 2:
            continue
        for I, count_I in itemsets.items():
            items = list(I)
            for r in range(1, len(items)):
                for a_tuple in combinations(items, r):
                    A = frozenset(a_tuple)
                    B = I - A
                    if not B:
                        continue
                    count_A = support[A]
                    count_B = support[B]
                    confidence = count_I / count_A
                    supp = count_I / n_baskets
                    p_b = count_B / n_baskets
                    lift = confidence / p_b
                    interest = abs(confidence - p_b)
                    if confidence >= min_confidence and interest >= min_interest:
                        rows.append({
                            "antecedent": A,
                            "consequent": B,
                            "support": supp,
                            "confidence": confidence,
                            "lift": lift,
                            "interest": interest,
                        })
    return pd.DataFrame(rows)


rules = generate_rules(freq, support, n_baskets, min_confidence=0.5, min_interest=0.5)
print("\nNumero de reglas generadas:", len(rules))
results2["n_rules"] = len(rules)
assert len(rules) == 8
print("Verificacion OK: 8 reglas generadas")

rules_sorted = rules.sort_values("lift", ascending=False).reset_index(drop=True)
rules_sorted["antecedent_desc"] = rules_sorted["antecedent"].apply(describe_itemset)
rules_sorted["consequent_desc"] = rules_sorted["consequent"].apply(describe_itemset)

display_cols = ["antecedent_desc", "consequent_desc", "support", "confidence", "lift", "interest"]
print("\nReglas de asociacion (ordenadas por lift desc):")
print(rules_sorted[display_cols].to_string(index=False))

rules_sorted.to_csv(f"{OUT_DIR}/association_rules.csv", index=False)

strongest = rules_sorted.iloc[0]
results2["strongest_rule"] = {
    "antecedent": strongest["antecedent_desc"],
    "consequent": strongest["consequent_desc"],
    "lift": float(strongest["lift"]),
    "confidence": float(strongest["confidence"]),
    "support": float(strongest["support"]),
}

results2["rules_table"] = rules_sorted[display_cols].to_dict(orient="records")

with open(f"{OUT_DIR}/results_part2.json", "w", encoding="utf-8") as f:
    json.dump(results2, f, indent=2, ensure_ascii=False, default=str)

print("\nOK - resultados de la Parte 2 guardados en output/results_part2.json")
