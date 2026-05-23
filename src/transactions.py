import json
import sys
from datetime import date, timedelta
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

_TXN_PATH = Path(__file__).parent / "transactions.json"

_TIPOS_GASTO = {"compra", "pago"}


def _fmt(amount: float) -> str:
    return "$" + f"{amount:,.0f}".replace(",", ".")


# ─── 1. load_transactions ────────────────────────────────────────

def load_transactions() -> list:
    with open(_TXN_PATH, encoding="utf-8") as f:
        return json.load(f)


# ─── 2. get_transactions_summary ─────────────────────────────────

def get_transactions_summary() -> dict:
    """Return financial summary for the current and previous calendar months.

    Only counts expense transactions (tipo compra/pago, estado aprobada).
    """
    today = date.today()
    mes_actual   = (today.year, today.month)
    primer_dia   = today.replace(day=1)
    mes_anterior = (
        (primer_dia - timedelta(days=1)).replace(day=1).year,
        (primer_dia - timedelta(days=1)).replace(day=1).month,
    )

    txns = load_transactions()

    gastos_actual    = []
    gastos_anterior  = []
    categorias_actual: dict[str, float] = {}

    for t in txns:
        if t.get("estado") != "aprobada":
            continue
        if t.get("tipo") not in _TIPOS_GASTO:
            continue
        fecha = date.fromisoformat(t["fecha"])
        mes   = (fecha.year, fecha.month)
        monto = float(t["monto"])

        if mes == mes_actual:
            gastos_actual.append(monto)
            cat = t.get("categoria", "Otro")
            categorias_actual[cat] = categorias_actual.get(cat, 0) + monto
        elif mes == mes_anterior:
            gastos_anterior.append(monto)

    total_actual   = sum(gastos_actual)
    total_anterior = sum(gastos_anterior)
    n_actual       = len(gastos_actual)
    promedio       = total_actual / n_actual if n_actual else 0.0
    cat_mayor      = max(categorias_actual, key=categorias_actual.get) if categorias_actual else ""

    return {
        "total_gastado_mes_actual":    total_actual,
        "total_gastado_mes_anterior":  total_anterior,
        "categoria_mayor_gasto":       cat_mayor,
        "numero_transacciones_mes":    n_actual,
        "promedio_transaccion":        promedio,
    }


# ─── 3. get_by_categoria ─────────────────────────────────────────

def get_by_categoria(categoria: str) -> list:
    """Return all transactions matching *categoria* (case-insensitive)."""
    needle = categoria.strip().lower()
    return [
        t for t in load_transactions()
        if t.get("categoria", "").lower() == needle
    ]


# ─── 4. get_by_periodo ───────────────────────────────────────────

def get_by_periodo(fecha_inicio: str, fecha_fin: str) -> list:
    """Return transactions with fecha between *fecha_inicio* and *fecha_fin* inclusive (YYYY-MM-DD)."""
    inicio = date.fromisoformat(fecha_inicio)
    fin    = date.fromisoformat(fecha_fin)
    return [
        t for t in load_transactions()
        if inicio <= date.fromisoformat(t["fecha"]) <= fin
    ]


# ─── 5. get_context_for_prompt ───────────────────────────────────

def get_context_for_prompt() -> str:
    """Return a compact spending summary (max ~150 words) for the last 30 days."""
    hoy    = date.today()
    inicio = hoy - timedelta(days=30)

    recientes = [
        t for t in load_transactions()
        if t.get("tipo") in _TIPOS_GASTO
        and t.get("estado") == "aprobada"
        and date.fromisoformat(t["fecha"]) >= inicio
    ]

    if not recientes:
        return "RESUMEN DE GASTOS RECIENTES: Sin transacciones en los ultimos 30 dias."

    total = sum(float(t["monto"]) for t in recientes)

    cats: dict[str, float] = {}
    for t in recientes:
        cat = t.get("categoria", "Otro")
        cats[cat] = cats.get(cat, 0) + float(t["monto"])

    top3 = sorted(cats.items(), key=lambda x: x[1], reverse=True)[:3]
    top3_txt = " | ".join(f"{c}: {_fmt(v)}" for c, v in top3)

    ultimas = sorted(recientes, key=lambda t: t["fecha"], reverse=True)[:3]
    ult_txt = " | ".join(
        f"{t['comercio']} {_fmt(t['monto'])}" for t in ultimas
    )

    return (
        f"RESUMEN DE GASTOS RECIENTES (ultimos 30 dias):\n"
        f"Total gastado: {_fmt(total)} en {len(recientes)} transacciones.\n"
        f"Top categorias: {top3_txt}.\n"
        f"Ultimas compras: {ult_txt}."
    )


# ─── Test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  TEST — transactions.py")
    print("=" * 60)

    # 1. Total de transacciones cargadas
    txns = load_transactions()
    print(f"\n[1] Total de transacciones cargadas : {len(txns)}")

    # 2. Resumen financiero del mes actual
    resumen = get_transactions_summary()
    print("\n[2] Resumen mes actual (mayo 2026):")
    print(f"    Total gastado mes actual    : {_fmt(resumen['total_gastado_mes_actual'])}")
    print(f"    Total gastado mes anterior  : {_fmt(resumen['total_gastado_mes_anterior'])}")
    print(f"    Categoria mayor gasto       : {resumen['categoria_mayor_gasto']}")
    print(f"    No. transacciones mes       : {resumen['numero_transacciones_mes']}")
    print(f"    Promedio por transaccion    : {_fmt(resumen['promedio_transaccion'])}")

    # 3. Las 5 transacciones mas recientes (aprobadas, tipo gasto)
    gastos = [
        t for t in txns
        if t.get("tipo") in _TIPOS_GASTO and t.get("estado") == "aprobada"
    ]
    gastos_ord = sorted(gastos, key=lambda t: (t["fecha"], t["hora"]), reverse=True)[:5]
    print("\n[3] Las 5 transacciones mas recientes:")
    for t in gastos_ord:
        print(f"    {t['id']}  {t['fecha']}  {t['comercio']:<30}  {_fmt(t['monto'])}")

    # 4. Confirmacion word count < 150
    ctx_txt   = get_context_for_prompt()
    num_words = len(ctx_txt.split())
    ok        = "OK" if num_words < 150 else "EXCEDE LIMITE"
    print(f"\n[4] get_context_for_prompt() -> {num_words} palabras [{ok}]")
    print("\n" + "─" * 60)
    print(ctx_txt)
    print("─" * 60)
