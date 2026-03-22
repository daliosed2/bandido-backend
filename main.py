import os
import gspread
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oauth2client.service_account import ServiceAccountCredentials

app = FastAPI()

# Configuración de CORS para que tu dominio oficial pueda entrar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shop.davidfernandomartinez.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DE GOOGLE SHEETS ---
def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Extraemos las variables que pusiste en Render
    creds_dict = {
        "type": "service_account",
        "project_id": os.getenv("G_SHEET_PROJECT_ID"),
        "private_key": os.getenv("G_SHEET_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("G_SHEET_CLIENT_EMAIL"),
        "token_uri": "https://oauth2.google.com/token",
    }
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

@app.get("/api/productos")
async def get_productos():
    try:
        client = get_gsheet_client()
        # Aquí usa el ID que pegaste en las variables de Render
        sheet = client.open_by_key(os.getenv("G_SHEET_ID")).sheet1
        data = sheet.get_all_records()
        
        productos_formateados = []
        for row in data:
            # Limpiamos la lista de imágenes para no enviar URLs vacías
            raw_imgs = [row.get("Imagen_1"), row.get("Imagen_2"), row.get("Imagen_3"), row.get("Imagen_4")]
            lista_imagenes = [img for img in raw_imgs if img and str(img).startswith('http')]

            productos_formateados.append({
                "id": row.get("ID"),
                "equipo": row.get("Equipo"),
                "sku": row.get("SKU"),
                "precio_venta": float(row.get("Precio", 0)),
                "imagenes": lista_imagenes,
                "tallas": {
                    "S": int(row.get("Talla_S", 0)),
                    "M": int(row.get("Talla_M", 0)),
                    "L": int(row.get("Talla_L", 0)),
                    "XL": int(row.get("Talla_XL", 0))
                },
                "descripcion": row.get("Descripcion", "")
            })
        return productos_formateados
    except Exception as e:
        return {"error": str(e)}