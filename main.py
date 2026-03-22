import os
import gspread
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oauth2client.service_account import ServiceAccountCredentials

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shop.davidfernandomartinez.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_gsheet_client():
    """Conexión robusta con Google Sheets"""
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
    
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"Error de autenticación: {e}")
        raise e

@app.get("/api/productos")
async def get_productos():
    try:
        client = get_gsheet_client()
        sheet_id = os.getenv("G_SHEET_ID")
        sheet = client.open_by_key(sheet_id).sheet1
        data = sheet.get_all_records()
        
        productos_formateados = []
        for row in data:
            # Procesamos las imágenes
            raw_imgs = [row.get("Imagen_1"), row.get("Imagen_2"), row.get("Imagen_3"), row.get("Imagen_4")]
            lista_imagenes = [img for img in raw_imgs if img and str(img).startswith('http')]

            productos_formateados.append({
                "id": row.get("ID"),
                "equipo": row.get("Equipo"),
                "sku": row.get("SKU"),
                "categoria": row.get("Categoria", "General"), # LEEMOS LA NUEVA COLUMNA
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
        print(f"Error: {e}")
        return {"error": str(e)}

@app.get("/")
async def root():
    return {"status": "Bandido Mundialista API is Live ⚽"}