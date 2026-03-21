from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI(title="Bandido Mundialista API", version="1.0")

# --- 1. CONFIGURACIÓN DE CORS ---
# Esto permite que tu frontend de Next.js se comunique con este backend sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. MODELOS DE DATOS ---
class Producto(BaseModel):
    id: int
    sku_base: str 
    equipo: str
    precio_venta: float
    tallas: Dict[str, int] # Ejemplo: {"S": 5, "M": 10}
    imagen_url: str

class PedidoWhatsApp(BaseModel):
    nombre_cliente: str
    telefono: str
    producto_id: int
    talla_elegida: str # La talla que el usuario seleccionó en el frontend
    cantidad: int

# --- 3. BASE DE DATOS SIMULADA ---
# He colocado la imagen que proporcionaste en ambos productos
inventario_db = [
    {
        "id": 1, 
        "sku_base": "ARG-VIS-24", 
        "equipo": "Selección Argentina Visitante", 
        "precio_venta": 35.00, 
        "tallas": {"S": 5, "M": 10, "L": 0, "XL": 2}, 
        "imagen_url": "https://i.imgur.com/Wi5eFJ9.png"
    },
    {
        "id": 2, 
        "sku_base": "RMA-001", 
        "equipo": "Real Madrid 23/24", 
        "precio_venta": 35.00, 
        "tallas": {"S": 0, "M": 5, "L": 5, "XL": 0}, 
        "imagen_url": "https://i.imgur.com/Wi5eFJ9.png"
    }
]

# --- 4. ENDPOINTS ---

@app.get("/", tags=["Estado"])
def estado_servidor():
    return {"mensaje": "API de Bandido Mundialista operativa y lista para vender."}

@app.get("/api/productos", response_model=List[Producto], tags=["Catálogo"])
def obtener_catalogo():
    # Retorna el inventario completo para que el frontend dibuje las tarjetas
    return inventario_db

@app.post("/api/checkout-whatsapp", tags=["Ventas"])
def procesar_pedido(pedido: PedidoWhatsApp):
    # Buscamos el producto por ID
    producto = next((p for p in inventario_db if p["id"] == pedido.producto_id), None)
    
    if not producto:
        raise HTTPException(status_code=404, detail="Camiseta no encontrada")
    
    # Validamos si la talla elegida existe y tiene stock
    stock_actual = producto["tallas"].get(pedido.talla_elegida, 0)
    
    if stock_actual < pedido.cantidad:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente para la talla {pedido.talla_elegida}")

    total = producto["precio_venta"] * pedido.cantidad
    
    # Armamos el mensaje para WhatsApp
    mensaje_wa = (
        f"Hola Bandido Mundialista! Soy {pedido.nombre_cliente}. "
        f"Quiero confirmar mi pedido de {pedido.cantidad} camiseta(s) de "
        f"{producto['equipo']} (Talla {pedido.talla_elegida}). "
        f"Total a pagar: ${total}."
    )
    
    # Link directo (usando tu número registrado)
    link_whatsapp = f"https://wa.me/593992753201?text={mensaje_wa.replace(' ', '%20')}"

    return {
        "status": "éxito",
        "mensaje": "Pedido procesado. Redirigiendo a WhatsApp...",
        "link_cierre": link_whatsapp,
        "total_a_cobrar": total
    }