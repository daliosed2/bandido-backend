from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI(title="Bandido Mundialista API", version="1.0")

# --- 1. CONFIGURACIÓN DE CORS (Permisos para que Next.js pueda leer los datos) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. MODELOS DE DATOS (Las reglas estrictas de tu negocio) ---
class Producto(BaseModel):
    id: int
    sku_base: str 
    equipo: str
    precio_venta: float
    tallas: Dict[str, int] # <-- El formato clave para el frontend: {"Talla": Stock}
    imagen_url: str

class PedidoWhatsApp(BaseModel):
    nombre_cliente: str
    telefono: str
    producto_id: int
    talla_elegida: str # <-- Ahora el pedido exige saber qué talla eligió
    cantidad: int

# --- 3. BASE DE DATOS (Tu catálogo actual) ---
inventario_db = [
    {
        "id": 1, 
        "sku_base": "ARG-VIS-24", 
        "equipo": "Selección Argentina Visitante", 
        "precio_venta": 35.00, 
        # Control de stock por talla. 0 = Botón bloqueado en la web.
        "tallas": {"S": 2, "M": 10, "L": 0, "XL": 5}, 
        "imagen_url": "https://i.imgur.com/kS9Qn1U.jpg"
    },
    {
        "id": 2, 
        "sku_base": "RMA-001", 
        "equipo": "Real Madrid 23/24", 
        "precio_venta": 35.00, 
        "tallas": {"S": 0, "M": 5, "L": 5, "XL": 2}, 
        "imagen_url": "https://i.imgur.com/vH9v5qL.jpg"
    }
]

# --- 4. ENDPOINTS (Las puertas de acceso a tu sistema) ---

@app.get("/", tags=["Estado"])
def estado_servidor():
    return {"mensaje": "API de Bandido Mundialista operativa y lista para vender."}

@app.get("/api/productos", response_model=List[Producto], tags=["Catálogo"])
def obtener_catalogo():
    # Devuelve todo el catálogo al frontend de Next.js
    return inventario_db

@app.post("/api/checkout-whatsapp", tags=["Ventas"])
def procesar_pedido(pedido: PedidoWhatsApp):
    # 1. Buscamos la camiseta en la base de datos
    producto = next((p for p in inventario_db if p["id"] == pedido.producto_id), None)
    
    if not producto:
        raise HTTPException(status_code=404, detail="Camiseta no encontrada")
    
    # 2. Validamos que la talla exista y tenga stock
    stock_disponible = producto["tallas"].get(pedido.talla_elegida, 0)
    
    if stock_disponible < pedido.cantidad:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente para la talla {pedido.talla_elegida}")

    # 3. Calculamos totales
    total = producto["precio_venta"] * pedido.cantidad
    
    # 4. Generamos el enlace de WhatsApp (usando el número que pusiste en tu frontend)
    mensaje_wa = f"Hola Bandido Mundialista Shop ⚽! Soy {pedido.nombre_cliente}. Quiero confirmar mi pedido: {pedido.cantidad} camiseta(s) del {producto['equipo']} (Talla {pedido.talla_elegida}). Total: ${total}."
    link_whatsapp = f"https://wa.me/593992753201?text={mensaje_wa.replace(' ', '%20')}"

    return {
        "status": "éxito",
        "mensaje": "Pedido procesado correctamente.",
        "link_cierre": link_whatsapp,
        "total_a_cobrar": total
    }