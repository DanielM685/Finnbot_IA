import copy
import json
import sys
from datetime import date
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

_CTX_PATH = Path(__file__).parent / "user_context.json"

_EMPTY: dict = {
    "usuario": {
        "nombre": "",
        "cedula": "",
        "edad": 0,
        "ciudad": "",
        "ocupacion": "",
        "ingresos_mensuales": 0,
        "antiguedad_cliente_años": 0,
        "perfil_riesgo": ""
    },
    "productos_activos": [],
    "resumen_financiero": {
        "total_deudas": 0,
        "total_ahorros_e_inversiones": 0,
        "cuota_mensual_total": 0,
        "capacidad_endeudamiento_restante": 0,
        "indicador_salud_financiera": "saludable"
    },
    "alertas": [],
    "ultima_actualizacion": ""
}

_TIPOS_DEUDA  = {"credito", "tarjeta"}
_TIPOS_AHORRO = {"cdt", "ahorro", "cuenta"}

_LIMITE_ENDEUDAMIENTO = 0.30  # 30% of monthly income


def _empty_context() -> dict:
    return copy.deepcopy(_EMPTY)


def _fmt(amount: float) -> str:
    return "$" + f"{amount:,.0f}".replace(",", ".")


# ─── 1. load_context ─────────────────────────────────────────────

def load_context() -> dict:
    if not _CTX_PATH.exists():
        ctx = _empty_context()
        save_context(ctx)
        return ctx
    with open(_CTX_PATH, encoding="utf-8") as f:
        return json.load(f)


# ─── 2. save_context ─────────────────────────────────────────────

def save_context(data: dict) -> bool:
    try:
        with open(_CTX_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


# ─── 3. update_usuario ───────────────────────────────────────────

def update_usuario(
    nombre: str = None,
    cedula: str = None,
    edad: int = None,
    ciudad: str = None,
    ocupacion: str = None,
    ingresos_mensuales: float = None,
    antiguedad_cliente_años: int = None,
    perfil_riesgo: str = None,
) -> bool:
    ctx = load_context()
    u = ctx["usuario"]
    if nombre               is not None: u["nombre"]                  = nombre
    if cedula               is not None: u["cedula"]                  = cedula
    if edad                 is not None: u["edad"]                    = edad
    if ciudad               is not None: u["ciudad"]                  = ciudad
    if ocupacion            is not None: u["ocupacion"]               = ocupacion
    if ingresos_mensuales   is not None: u["ingresos_mensuales"]      = ingresos_mensuales
    if antiguedad_cliente_años is not None: u["antiguedad_cliente_años"] = antiguedad_cliente_años
    if perfil_riesgo        is not None: u["perfil_riesgo"]           = perfil_riesgo
    return save_context(ctx)


# ─── 4. add_producto ─────────────────────────────────────────────

def add_producto(
    tipo: str,
    nombre: str,
    saldo_actual: float = 0,
    cupo_total: float = 0,
    cuota_mensual: float = 0,
    tasa_ea: float = 0,
    fecha_apertura: str = "",
    fecha_vencimiento: str = "",
    cuotas_pagadas: int = 0,
    cuotas_totales: int = 0,
    estado: str = "activo",
) -> bool:
    ctx = load_context()
    key = nombre.strip().lower()

    for producto in ctx["productos_activos"]:
        if producto["nombre"].strip().lower() == key:
            producto.update({
                "tipo": tipo,
                "saldo_actual": saldo_actual,
                "cupo_total": cupo_total,
                "cuota_mensual": cuota_mensual,
                "tasa_ea": tasa_ea,
                "fecha_apertura": fecha_apertura,
                "fecha_vencimiento": fecha_vencimiento,
                "cuotas_pagadas": cuotas_pagadas,
                "cuotas_totales": cuotas_totales,
                "estado": estado,
            })
            return save_context(ctx)

    ctx["productos_activos"].append({
        "tipo": tipo,
        "nombre": nombre,
        "saldo_actual": saldo_actual,
        "cupo_total": cupo_total,
        "cuota_mensual": cuota_mensual,
        "tasa_ea": tasa_ea,
        "fecha_apertura": fecha_apertura,
        "fecha_vencimiento": fecha_vencimiento,
        "cuotas_pagadas": cuotas_pagadas,
        "cuotas_totales": cuotas_totales,
        "estado": estado,
    })
    return save_context(ctx)


# ─── 5. update_resumen_financiero ────────────────────────────────

def update_resumen_financiero() -> bool:
    ctx = load_context()

    total_deudas = 0.0
    total_ahorros = 0.0
    cuota_mensual_total = 0.0

    for p in ctx["productos_activos"]:
        tipo  = p.get("tipo", "").lower()
        saldo = float(p.get("saldo_actual", 0))
        cuota = float(p.get("cuota_mensual", 0))

        if tipo in _TIPOS_DEUDA:
            total_deudas        += saldo
            cuota_mensual_total += cuota
        elif tipo in _TIPOS_AHORRO:
            total_ahorros += saldo

    ingresos = float(ctx["usuario"].get("ingresos_mensuales", 0))
    limite_cuota = ingresos * _LIMITE_ENDEUDAMIENTO
    capacidad = max(0.0, limite_cuota - cuota_mensual_total)

    if ingresos > 0:
        ratio = cuota_mensual_total / ingresos
        if ratio < 0.30:
            indicador = "saludable"
        elif ratio <= 0.40:
            indicador = "moderado"
        else:
            indicador = "en riesgo"
    else:
        indicador = "saludable"

    ctx["resumen_financiero"] = {
        "total_deudas": total_deudas,
        "total_ahorros_e_inversiones": total_ahorros,
        "cuota_mensual_total": cuota_mensual_total,
        "capacidad_endeudamiento_restante": capacidad,
        "indicador_salud_financiera": indicador,
    }
    return save_context(ctx)


# ─── 6. get_context_for_prompt ───────────────────────────────────

def get_context_for_prompt() -> str:
    ctx = load_context()
    nombre = ctx["usuario"].get("nombre", "").strip()
    if not nombre:
        return ""

    u         = ctx["usuario"]
    resumen   = ctx["resumen_financiero"]
    productos = ctx["productos_activos"]

    ingreso_txt = _fmt(u.get("ingresos_mensuales", 0))
    indicador   = resumen.get("indicador_salud_financiera", "")

    productos_detalle = []
    for p in productos:
        tipo  = p["tipo"]
        linea = f"- {p['nombre']} (tipo: {tipo})"
        linea += f" | saldo actual (deuda/saldo usado): {_fmt(p['saldo_actual'])}"

        if tipo == "tarjeta":
            cupo      = float(p.get("cupo_total", 0))
            saldo     = float(p.get("saldo_actual", 0))
            disponible = cupo - saldo
            linea += f" | cupo total: {_fmt(cupo)} | cupo disponible: {_fmt(disponible)}"
        elif tipo == "credito":
            linea += f" | cuotas pagadas: {p.get('cuotas_pagadas',0)} de {p.get('cuotas_totales',0)}"
        elif tipo in ("cdt", "ahorro"):
            linea += f" | tasa E.A.: {p.get('tasa_ea',0)}%"
            if p.get("fecha_vencimiento"):
                linea += f" | vence: {p['fecha_vencimiento']}"

        if p.get("cuota_mensual", 0) > 0:
            linea += f" | cuota mensual: {_fmt(p['cuota_mensual'])}"

        productos_detalle.append(linea)

    productos_txt = "\n".join(productos_detalle) if productos_detalle else "ninguno"

    return (
        "PERFIL DEL USUARIO:\n"
        f"Nombre: {nombre} | Ciudad: {u.get('ciudad','')} | "
        f"Ocupacion: {u.get('ocupacion','')} | Ingresos: {ingreso_txt}\n"
        f"Deudas totales: {_fmt(resumen['total_deudas'])} | "
        f"Ahorros e inversiones: {_fmt(resumen['total_ahorros_e_inversiones'])} | "
        f"Cuota mensual: {_fmt(resumen['cuota_mensual_total'])} | "
        f"Salud financiera: {indicador}\n\n"
        f"PRODUCTOS ACTIVOS ({len(productos)}):\n{productos_txt}"
    )

# ─── 7. clear_context ────────────────────────────────────────────

def clear_context() -> bool:
    return save_context(_empty_context())


# ─── Prueba de integración ────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  PRUEBA DE INTEGRACION — user_context.py")
    print("=" * 60)

    # Reload actual demo user from disk (do not overwrite)
    ctx = load_context()
    u   = ctx["usuario"]
    r   = ctx["resumen_financiero"]

    print(f"\nUsuario cargado : {u['nombre']}")
    print(f"Ciudad          : {u.get('ciudad','')}")
    print(f"Ingresos        : {_fmt(u.get('ingresos_mensuales', 0))}")
    print(f"Perfil riesgo   : {u.get('perfil_riesgo','')}")

    print("\n" + "─" * 60)
    print("  RESUMEN FINANCIERO")
    print("─" * 60)
    print(f"  Total deudas                 : {_fmt(r['total_deudas'])}")
    print(f"  Total ahorros e inversiones  : {_fmt(r['total_ahorros_e_inversiones'])}")
    print(f"  Cuota mensual total          : {_fmt(r['cuota_mensual_total'])}")
    print(f"  Capacidad endeudamiento      : {_fmt(r['capacidad_endeudamiento_restante'])}")
    print(f"  Indicador salud financiera   : {r['indicador_salud_financiera']}")

    print("\n" + "─" * 60)
    print("  PRODUCTOS ACTIVOS")
    print("─" * 60)
    for p in ctx["productos_activos"]:
        print(f"  [{p['tipo'].upper()}] {p['nombre']}")
        print(f"    Saldo actual : {_fmt(p['saldo_actual'])}  |  Tasa EA: {p.get('tasa_ea',0)}%")

    print("\n" + "─" * 60)
    print("  ALERTAS")
    print("─" * 60)
    for a in ctx.get("alertas", []):
        tag = "(!)" if a["tipo"] == "advertencia" else "(i)"
        print(f"  {tag} {a['mensaje'][:80]}...")

    print("\n" + "─" * 60)
    print("  CONTEXTO PARA EL AGENTE")
    print("─" * 60)
    print(get_context_for_prompt())
    print()

