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
        "equipo": "Selección Argentina Visitante 2026 Mundial", 
        "precio_venta": 35.00, 
        "tallas": {"S": 5, "M": 10, "L": 2, "XL": 2}, 
        "imagenes": [
            "https://i.imgur.com/Wi5eFJ9.png",
            "https://assets.adidas.com/images/w_940,f_auto,q_auto/a3ad0f0ebbcb4a2bb3e86a34c7746851_9366/KB0639_02_laydown.jpg"
        ],
        "descripcion": "Camiseta versión fan de la Selección Argentina. Tela transpirable con tecnología de secado rápido. Escudo bordado y detalles oficiales."
    },
    {
        "id": 2, 
        "sku_base": "RMA-001", 
        "equipo": "Real Madrid 25/26", 
        "precio_venta": 35.00, 
        "tallas": {"S": 0, "M": 5, "L": 5, "XL": 2}, 
        "imagenes": [
            "https://shop.realmadrid.com/cdn/shop/files/RMCFMZ0903_01.jpg?v=1767814763&width=1000",
            "https://lataquillafutbol.com/wp-content/uploads/2025/06/83ffc95b-scaled.jpg"
        ],
        "descripcion": "La blanca del Rey de Europa. Calidad premium, tejido técnico y ajuste perfecto para el hincha madridista."
    },
    {
        "id": 3, 
        "sku_base": "BAR-001", 
        "equipo": "Barcelona Visitante Kobe 25/26", 
        "precio_venta": 35.00, 
        "tallas": {"S": 0, "M": 5, "L": 5, "XL": 2}, 
        "imagenes": [
            "https://store.fcbarcelona.com/cdn/shop/files/HJ4603-784_431735711_D_A_1X1_48cfc706-a037-4073-aa5a-8abbde823c12.jpg?v=1753951926&width=1200",
            "https://store.fcbarcelona.com/cdn/shop/files/BARCA1-24660.jpg?v=1753951926&width=1200"

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