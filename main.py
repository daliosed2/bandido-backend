from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Bandido Mundialista API")

# --- 1. SEGURIDAD (CORS) ---
# He revisado cada coma aquí para que no falle el deploy
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://bandido-frontend.vercel.app",
        "https://shop.davidfernandomartinez.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. MODELO DE DATOS ---
class Producto(BaseModel):
    id: int
    sku_base: str 
    equipo: str
    precio_venta: float
    tallas: Dict[str, int]
    imagenes: List[str]
    descripcion: str

# --- 3. BASE DE DATOS (CATÁLOGO) ---
inventario_db = [
    {
        "id": 1, 
        "sku_base": "ARG-VIS-24", 
        "equipo": "Selección Argentina Visitante", 
        "precio_venta": 35.00, 
        "tallas": {"S": 5, "M": 10, "L": 0, "XL": 2}, 
        "imagenes": [
            "https://i.imgur.com/Wi5eFJ9.png",
            "https://i.imgur.com/Wi5eFJ9.png"
        ],
        "descripcion": "Camiseta versión fan de la Selección Argentina. Tela transpirable con tecnología de secado rápido. Escudo bordado y detalles oficiales."
    },
    {
        "id": 2, 
        "sku_base": "RMA-001", 
        "equipo": "Real Madrid 23/24", 
        "precio_venta": 35.00, 
        "tallas": {"S": 0, "M": 5, "L": 5, "XL": 2}, 
        "imagenes": [
            "https://i.imgur.com/Wi5eFJ9.png",
            "https://i.imgur.com/Wi5eFJ9.png"
        ],
        "descripcion": "La blanca del Rey de Europa. Calidad premium, tejido técnico y ajuste perfecto para el hincha madridista."
    }
]

# --- 4. RUTAS ---
@app.get("/api/productos", response_model=List[Producto])
def obtener_catalogo():
    return inventario_db

@app.post("/api/checkout-whatsapp")
def procesar_pedido(pedido: dict):
    # Simplificado para evitar errores de validación por ahora
    return {"status": "ok"}