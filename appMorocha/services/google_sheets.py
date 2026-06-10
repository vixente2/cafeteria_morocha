import gspread
from google.oauth2.service_account import Credentials
import os

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_client():
    creds = Credentials.from_service_account_file(
        os.path.join(os.path.dirname(__file__), '../../credentials.json'),
        scopes=SCOPES
    )
    return gspread.authorize(creds)

def exportar_pedidos(pedidos, detalles):
    client = get_client()

    try:
        spreadsheet = client.open("Ventas Cafetera Morocha")
    except:
        spreadsheet = client.create("Ventas Cafetera Morocha")
        spreadsheet.share('TU_CORREO@gmail.com', perm_type='user', role='writer')

    # ── Hoja 1: Pedidos ──
    hoja_pedidos = spreadsheet.sheet1
    hoja_pedidos.update_title("Pedidos")
    hoja_pedidos.clear()
    hoja_pedidos.append_row(['ID Pedido', 'Fecha', 'ID Cliente', 'Mesa', 'Usuario', 'Estado', 'Total'])
    for p in pedidos:
        hoja_pedidos.append_row([
        str(p.get('id_pedido', '')),
        str(p.get('fecha_pedido', '')),
        str(p.get('id_cliente', '')),
        str(p.get('num_mesa', '')),
        str(p.get('nombre_usuario', '')),
        str(p.get('nombre_estadopedido', '')),
        str(p.get('total_pedido', 0) or 0)
    ])

    # ── Hoja 2: Detalle ──
    try:
        hoja_detalle = spreadsheet.worksheet("Detalle")
    except:
        hoja_detalle = spreadsheet.add_worksheet(title="Detalle", rows=1000, cols=10)

    hoja_detalle.clear()
    hoja_detalle.append_row(['ID Detalle', 'ID Pedido', 'Producto', 'Precio', 'Cantidad', 'Subtotal'])
    for d in detalles:
        cantidad = d.get('cantidad', 0) or 0
        precio = d.get('precio_producto', 0) or 0
        hoja_detalle.append_row([
            str(d.get('id_detallepedido', '')),
            str(d.get('id_pedido', '')),
            str(d.get('nombre_producto', '')),
            str(precio),
            str(cantidad),
            str(cantidad * precio)
        ])