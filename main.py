from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Agregamos esta línea
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Bandido Mundialista API", version="1.0")

# --- CONFIGURACIÓN DE CORS (La llave de acceso) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Con esto aceptamos peticiones de cualquier página
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DATOS (Pydantic valida que la data entre limpia) ---
class Producto(BaseModel):
    id: int
    sku: str
    equipo: str
    talla: str
    precio_venta: float
    stock: int

class PedidoWhatsApp(BaseModel):
    nombre_cliente: str
    telefono: str
    producto_id: int
    cantidad: int

# --- BASE DE DATOS SIMULADA (Para pruebas rápidas) ---
inventario_db = [
    {"id": 1, "sku": "ECU-593-M", "equipo": "Selección Ecuador", "talla": "M", "precio_venta": 45.00, "stock": 10},
    {"id": 2, "sku": "RMA-001-L", "equipo": "Real Madrid 23/24", "talla": "L", "precio_venta": 50.00, "stock": 5}
]

# --- ENDPOINTS (Las puertas de acceso a tu sistema) ---

@app.get("/", tags=["Estado"])
def estado_servidor():
    return {"mensaje": "API de Bandido Mundialista operativa y lista para vender."}

@app.get("/api/productos", response_model=List[Producto], tags=["Catálogo"])
def obtener_catalogo():
    # Aquí es donde conectaremos tu frontend para mostrar las camisetas
    productos_disponibles = [p for p in inventario_db if p["stock"] > 0]
    return productos_disponibles

@app.post("/api/checkout-whatsapp", tags=["Ventas"])
def procesar_pedido(pedido: PedidoWhatsApp):
    # Buscamos el producto
    producto = next((p for p in inventario_db if p["id"] == pedido.producto_id), None)
    
    if not producto:
        raise HTTPException(status_code=404, detail="Camiseta no encontrada")
    
    if producto["stock"] < pedido.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente para esta talla")

    total = producto["precio_venta"] * pedido.cantidad
    
    # Aquí armamos el link dinámico de WhatsApp que se abrirá en el celular del cliente
    mensaje_wa = f"Hola Bandido Mundialista! Soy {pedido.nombre_cliente}. Quiero confirmar mi pedido de {pedido.cantidad} camiseta(s) del {producto['equipo']} (Talla {producto['talla']}). El total es ${total}."
    link_whatsapp = f"https://wa.me/593900000000?text={mensaje_wa.replace(' ', '%20')}" # Reemplazaremos con tu número

    return {
        "status": "éxito",
        "mensaje": "Pedido procesado. Redirigiendo a WhatsApp...",
        "link_cierre": link_whatsapp,
        "total_a_cobrar": total
    }