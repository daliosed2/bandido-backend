import os
import gspread
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = FastAPI()

# --- CONFIGURACIÓN DE SEGURIDAD Y PREPRODUCCIÓN (CORS) ---
# Esto permite que tu web oficial Y tus pruebas en Vercel funcionen sin bloquearse
origins = [
    "https://shop.davidfernandomartinez.com",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    # Esta regex es más amplia: acepta cualquier URL que contenga 'bandido' y termine en '.vercel.app'
    allow_origin_regex=r"https://bandido-.*\.vercel\.app",
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_gsheet_client():
    """Conexión con la base de datos en Google Sheets"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    private_key = os.getenv("G_SHEET_PRIVATE_KEY")
    if private_key:
        # Limpieza de la llave privada para evitar errores de formato en Render
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

# --- RUTA 1: OBTENER INVENTARIO PARA LA TIENDA ---
@app.get("/api/productos")
async def get_productos():
    try:
        client = get_gsheet_client()
        sheet_id = os.getenv("G_SHEET_ID")
        sheet = client.open_by_key(sheet_id).sheet1
        data = sheet.get_all_records()
        
        productos_formateados = []
        for row in data:
            # Procesamos las 4 posibles imágenes
            raw_imgs = [row.get("Imagen_1"), row.get("Imagen_2"), row.get("Imagen_3"), row.get("Imagen_4")]
            lista_imagenes = [img for img in raw_imgs if img and str(img).startswith('http')]

            productos_formateados.append({
                "id": row.get("ID"),
                "equipo": row.get("Equipo"),
                "sku": row.get("SKU"),
                # Compatible con 'categoria' o 'Categoria' en el Sheet
                "categoria": row.get("categoria") or row.get("Categoria") or "General",
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
        print(f"Error en inventario: {e}")
        return {"error": str(e)}

# --- RUTA 2: REGISTRAR PEDIDOS EN LA PESTAÑA 'Pedidos' ---
@app.post("/api/registrar-pedido")
async def registrar_pedido(request: Request):
    try:
        datos = await request.json()
        client = get_gsheet_client()
        sheet_id = os.getenv("G_SHEET_ID")
        
        # Accedemos específicamente a la pestaña llamada 'Pedidos'
        sheet = client.open_by_key(sheet_id).worksheet("Pedidos")
        
        # Preparamos la fila para auditoría
        nueva_fila = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Fecha
            datos.get("producto"),                         # Equipo
            datos.get("talla"),                            # Talla elegida
            datos.get("tipo_envio", "Domicilio"),          # Domicilio / Retiro
            "SÍ 🎁" if datos.get("es_regalo") else "No",    # Es regalo
            datos.get("nombre_recibe"),                    # Quién recibe
            f"{datos.get('ciudad', '')} - {datos.get('direccion', '')}", # Ubicación completa
            datos.get("mensaje_tarjeta", ""),              # Mensaje personalizado
            "PENDIENTE ⏳",                                # Estado de venta (Control David)
            ""                                             # Notas adicionales
        ]
        
        sheet.append_row(nueva_fila)
        return {"status": "success", "message": "Pedido guardado"}
    except Exception as e:
        print(f"Error registrando pedido: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"status": "Bandido Mundialista API is Live ⚽"}