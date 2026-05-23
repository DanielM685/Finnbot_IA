import json
import os

def _cargar_productos():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    products_path = os.path.join(base_dir, "..", "data", "products.json")
    with open(products_path, "r", encoding="utf-8") as f:
        return json.load(f)["productos"]

def get_product_context(query: str = "") -> str:
    """Devuelve solo los productos relevantes según la query del usuario."""
    
    productos = _cargar_productos()
    query_lower = query.lower()

    # Filtrar productos relevantes por palabras clave o nombre
    if query_lower:
        relevantes = [
            p for p in productos
            if any(kw in query_lower for kw in p.get("palabras_clave", []))
            or any(palabra in query_lower for palabra in p.get("nombre", "").lower().split())
        ]
        # Si no encontró nada, tomar los primeros 5 como fallback
        if not relevantes:
            relevantes = productos[:5]
    else:
        relevantes = productos[:5]

    context = "=== PRODUCTOS SERFINANZA RELEVANTES ===\n\n"
    for p in relevantes:
        context += f"Producto: {p.get('nombre', '')}\n"
        context += f"Categoría: {p.get('categoria', '')}\n"
        context += f"Detalle: {p.get('contenido', '')}\n"
        context += "-" * 40 + "\n"

    return context