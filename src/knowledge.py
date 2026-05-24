import json
from pathlib import Path

_PRODUCTS_PATH = Path(__file__).parent.parent / "data" / "products.json"

_TIPOS_GASTO = {"compra", "pago"}



def _cargar_productos() -> list:
    with open(_PRODUCTS_PATH, encoding="utf-8") as f:
        return json.load(f)["productos"]


def get_product_context(query: str = "") -> str:
    """Devuelve solo los productos relevantes según la query del usuario."""

    productos = _cargar_productos()
    query_lower = query.lower()

    if query_lower:
        relevantes = [
            p for p in productos
            if any(kw in query_lower for kw in p.get("palabras_clave", []))
            or any(
                palabra in query_lower
                for palabra in p.get("nombre", "").lower().split()
            )
        ]
        if not relevantes:
            relevantes = productos[:4]
    else:
        relevantes = productos[:4]

    context = "=== PRODUCTOS SERFINANZA RELEVANTES ===\n\n"
    for p in relevantes:
        context += f"Producto: {p.get('nombre', '')}\n"
        context += f"Categoría: {p.get('categoria', '')}\n"
        context += f"Detalle: {p.get('contenido', '')}\n"
        context += "-" * 40 + "\n"

    return context


def get_product_info(nombre: str) -> dict:
    """Busca un producto por nombre (búsqueda parcial, ignora mayúsculas)."""
    nombre_lower = nombre.lower()
    for p in _cargar_productos():
        if nombre_lower in p.get("nombre", "").lower():
            return p
    return {}
