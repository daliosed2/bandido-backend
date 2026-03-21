from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI(title="Bandido Mundialista API", version="1.1")

# --- 1. CONFIGURACIÓN DE SEGURIDAD (CORS) ---
# Permite que tu frontend de Next.js lea los datos de este servidor
app.add_middleware(
    CORSMiddleware,
    # IMPORTANTE: Aquí van las URLs que pueden leer tu base de datos
    allow_origins=[
        "http://localhost:3000",
        "https://bandido-frontend.vercel.app",
        "https://shop.davidfernandomartinez.com"  # <--- TU NUEVO DOMINIO OFICIAL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. MODELO DE DATOS ACTUALIZADO ---
class Producto(BaseModel):
    id: int
    sku_base: str 
    equipo: str
    precio_venta: float
    tallas: Dict[str, int] # Formato: {"S": 5, "M": 0}
    imagenes: List[str]    # <-- Ahora acepta múltiples fotos por producto
    descripcion: str # <-- NUEVO CAMPO

class PedidoWhatsApp(BaseModel):
    nombre_cliente: str
    telefono: str
    producto_id: int
    talla_elegida: str
    cantidad: int

# --- 3. BASE DE DATOS (CATÁLOGO) ---
# RECOMENDACIÓN DE DAVID: Sube tus fotos a Imgur y usa el "Direct Link" (que termine en .png o .jpg)
inventario_db = [
    {
        "id": 1, 
        "sku_base": "ARG-VIS-24", 
        "equipo": "Selección Argentina Visitante", 
        "precio_venta": 35.00, 
        "tallas": {"S": 5, "M": 10, "L": 0, "XL": 2}, 
        # --- CARGA TUS FOTOS AQUÍ ---
        # La primera imagen de la lista será la portada principal.
        "imagenes": [
            "https://i.imgur.com/Wi5eFJ9.png", # Foto de frente
            "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh_fqRFDMdmamTLL2dedMcJjH7EzJMGZN9zi-Nv4Nf4N7gzeM9badQu7xT6FXE_dtlZKS57vplnQllOz_p3LkgGNlZVAuWjylJu84SWH7TTB01OXywjmiNQirJp4085rsdLDJsKV09nUlWu0lCkGxg8OF4cLfgmRPm50CmLn2v6HDOlKiAs8inZo-k-IevY/s1600/se-produce-la-filtracion-de-la-camiseta-visitante-de-argentina-para-el-mundial-de-2026-vista-a-la-venta.jpg", # Foto de espalda o detalle
            "https://i.imgur.com/Wi5eFJ9.png"  # Foto del escudo/tela
        ]
        "descripcion": "Camiseta versión fan de la Selección Argentina. Tela transpirable con tecnología de secado rápido. Escudo bordado y detalles oficiales." # <-- AGREGA ESTO
    },
    {
        "id": 2, 
        "sku_base": "RMA-001", 
        "equipo": "Real Madrid 23/24", 
        "precio_venta": 35.00, 
        "tallas": {"S": 0, "M": 5, "L": 5, "XL": 0}, 
        "imagenes": [
            "https://i.imgur.com/Wi5eFJ9.png", # Foto de frente
            "https://i.imgur.com/Wi5eFJ9.png"  # Foto detalle
        ]
        "descripcion": "Camiseta versión fan de la Selección Argentina. Tela transpirable con tecnología de secado rápido. Escudo bordado y detalles oficiales." # <-- AGREGA ESTO
    }
]

# --- 4. ENDPOINTS (RUTAS) ---

@app.get("/", tags=["Estado"])
def estado_servidor():
    return {"mensaje": "API de Bandido Mundialista operativa. ¡A vender!"}

@app.get("/api/productos", response_model=List[Producto], tags=["Catálogo"])
def obtener_catalogo():
    # Devuelve la lista completa de productos al frontend
    return inventario_db

@app.post("/api/checkout-whatsapp", tags=["Ventas"])
def procesar_pedido(pedido: PedidoWhatsApp):
    # Buscamos el producto por ID
    producto = next((p for p in inventario_db if p["id"] == pedido.producto_id), None)
    
    if not producto:
        raise HTTPException(status_code=404, detail="Camiseta no encontrada")
    
    # Validamos stock de la talla seleccionada
    stock_actual = producto["tallas"].get(pedido.talla_elegida, 0)
    
    if stock_actual < pedido.cantidad:
        raise HTTPException(status_code=400, detail=f"Stock agotado en talla {pedido.talla_elegida}")

    total = producto["precio_venta"] * pedido.cantidad
    
    # Generamos el mensaje para WhatsApp
    mensaje_wa = (
        f"Hola Bandido Mundialista Shop! Soy {pedido.nombre_cliente}. "
        f"Confirmo pedido de {pedido.cantidad} {producto['equipo']} "
        f"(Talla {pedido.talla_elegida}). Total: ${total}."
    )
    
    # Link directo al número registrado
    link_whatsapp = f"https://wa.me/593992753201?text={mensaje_wa.replace(' ', '%20')}"

    return {
        "status": "éxito",
        "link_cierre": link_whatsapp,
        "total": total
    }