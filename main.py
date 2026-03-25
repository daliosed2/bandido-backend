import os
import gspread
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = FastAPI()

# --- CONFIGURACIÓN DE SEGURIDAD PARA PREPRODUCCIÓN Y PRODUCCIÓN ---
origins = [
    "https://shop.davidfernandomartinez.com",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://bandido-.*\.vercel\.app",
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    private_key = os.getenv("G_SHEET_PRIVATE_KEY").replace('\\n', '\n').strip('"').strip("'")
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

# --- OBTENER PRODUCTOS ---
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

# --- VALIDAR CUPÓN ---
@app.get("/api/validar-cupon/{codigo}")
async def validar_cupon(codigo: str):
    try:
        client = get_gsheet_client()
        sheet = client.open_by_key(os.getenv("G_SHEET_ID")).worksheet("Cupones")
        data = sheet.get_all_records()
        # Busca el cupón activo
        cupon = next((c for c in data if str(c['Codigo']).upper() == codigo.upper() and str(c['Activo']).upper() == "SÍ"), None)
        
        if cupon:
            return {"valido": True, "descuento": float(cupon['Descuento_Porcentaje'])}
        return {"valido": False}
    except:
        return {"valido": False}

# --- REGISTRAR PEDIDO (CON CÁLCULO DE PRECIO FINAL) ---
@app.post("/api/registrar-pedido")
async def registrar_pedido(request: Request):
    try:
        d = await request.json()
        client = get_gsheet_client()
        sheet_id = os.getenv("G_SHEET_ID")
        
        # 1. Validar Cupón nuevamente (Seguridad)
        descuento_pct = 0
        codigo_usado = d.get("cupon", "NINGUNO").upper()
        
        if codigo_usado != "NINGUNO":
            c_sheet = client.open_by_key(sheet_id).worksheet("Cupones")
            c_data = c_sheet.get_all_records()
            found = next((c for c in c_data if str(c['Codigo']).upper() == codigo_usado and str(c['Activo']).upper() == "SÍ"), None)
            if found:
                descuento_pct = float(found['Descuento_Porcentaje'])
            else:
                codigo_usado = "INVALIDO/EXPIRADO"

        # 2. Cálculos de Precio
        precio_original = float(d.get("precio", 0))
        precio_final = precio_original * (1 - (descuento_pct / 100))

        # 3. Mapeo a las columnas del Sheet 'Pedidos'
        # Fecha | Producto | Talla | Envío | Ciudad | Dirección | Nombre | Regalo | Mensaje | Cupón | Precio_Original | Precio_Final | Estado
        sheet = client.open_by_key(sheet_id).worksheet("Pedidos")
        nueva_fila = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            d.get("producto"),
            d.get("talla"),
            d.get("tipo_envio"),
            d.get("ciudad", "N/A"),
            d.get("direccion", "N/A"),
            d.get("nombre_recibe"),
            "SÍ 🎁" if d.get("es_regalo") else "No",
            d.get("mensaje_tarjeta", ""),
            codigo_usado,
            f"{precio_original:.2f}",
            f"{precio_final:.2f}",
            "PENDIENTE ⏳"
        ]
        
        sheet.append_row(nueva_fila)
        return {"status": "success", "precio_final": precio_final}

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"status": "Bandido Mundialista API is Live ⚽"}