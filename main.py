from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Bandido Mundialista API")

# --- 1. CONFIGURACIÓN DE SEGURIDAD (CORS) ---
# He añadido tu nuevo dominio oficial para que Render lo acepte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Esto permite que CUALQUIER dominio lea los datos
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

# --- 3. BASE DE DATOS (CATÁLOGO REPARADO) ---
# REVISIÓN: Todas las líneas terminan en coma para evitar el SyntaxError
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

# --- 4. RUTAS (ENDPOINTS) ---
@app.get("/api/productos", response_model=List[Producto])
def obtener_catalogo():
    return inventario_db

@app.get("/")
def home():
    return {"mensaje": "API Bandido Mundialista Online"}

# Endpoint simplificado para que no falle el checkout
@app.post("/api/checkout-whatsapp")
def procesar_pedido(pedido: dict):
    return {"status": "success"}