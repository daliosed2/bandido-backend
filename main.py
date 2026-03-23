import os
import gspread
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = FastAPI()

# Configuración de CORS para tu dominio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shop.davidfernandomartinez.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    private_key = os.getenv("G_SHEET_PRIVATE_KEY")
    if private_key:
        private_key = private_key.replace('\\n', '\n').strip('"').strip("'")

    creds_dict = {
        "type": "service_account",
        "project_id": os.getenv("G_SHEET_PROJECT_ID"),
        "private_key_id": "99999999999999999999999999999999",
        "private_key": private_key,
        "client_email": os.getenv("G_SHEET_CLIENT_EMAIL"),
        "client_id": "111111111111111111111",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('G_SHEET_CLIENT_EMAIL')}"
    }
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

@app.get("/api/productos")
async def get_productos():
    try:
        client = get_gsheet_client()
        sheet = client.open_by_key(os.getenv("G_SHEET_ID")).sheet1
        data = sheet.get_all_records()
        
        productos = []
        for row in data:
            imgs = [row.get("Imagen_1"), row.get("Imagen_2"), row.get("Imagen_3"), row.get("Imagen_4")]
            productos.append({
                "id": row.get("ID"),
                "equipo": row.get("Equipo"),
                "sku": row.get("SKU"),
                "categoria": row.get("categoria") or row.get("Categoria") or "General",
                "precio_venta": float(row.get("Precio", 0)),
                "imagenes": [img for img in imgs if img and str(img).startswith('http')],
                "tallas": {
                    "S": int(row.get("Talla_S", 0)),
                    "M": int(row.get("Talla_M", 0)),
                    "L": int(row.get("Talla_L", 0)),
                    "XL": int(row.get("Talla_XL", 0))
                },
                "descripcion": row.get("Descripcion", "")
            })
        return productos
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/registrar-pedido")
async def registrar_pedido(datos: Request):
    try:
        data = await datos.json()
        client = get_gsheet_client()
        # ACCEDEMOS A LA PESTAÑA 'Pedidos'
        sheet = client.open_by_key(os.getenv("G_SHEET_ID")).worksheet("Pedidos")
        
        nueva_fila = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("producto"),
            data.get("talla"),
            data.get("tipo_envio", "Domicilio"),
            "SÍ 🎁" if data.get("es_regalo") else "No",
            data.get("nombre_recibe"),
            data.get("direccion"),
            data.get("mensaje_tarjeta", ""),
            "PENDIENTE ⏳", # Estado inicial para auditoría
            "" # Notas del vendedor
        ]
        
        sheet.append_row(nueva_fila)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"status": "Bandido Mundialista API is Live ⚽"}