import streamlit as st
import pandas as pd
import urllib.parse
import json
import os
from datetime import datetime

LOGO_URL = "https://raw.githubusercontent.com/Montoya100/Mostacho-Botanas-Web/main/logo.png"
DATA_FILE = "productos_mostacho.json"
POPULAR_FILE = "populares_mostacho.json"
BANNER_FILE = "banner_mostacho.json"
CONFIG_FILE = "config_mostacho.json"
UPLOAD_DIR = "uploaded_images"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

st.set_page_config(
    page_title="Julissa",
    page_icon=LOGO_URL,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar estados
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "nav_view" not in st.session_state:
    st.session_state.nav_view = "catalogo"
if "selected_cat" not in st.session_state:
    st.session_state.selected_cat = "Todo"
if "saved_customer_name" not in st.session_state:
    st.session_state.saved_customer_name = ""
if "saved_customer_address" not in st.session_state:
    st.session_state.saved_customer_address = ""
if "saved_customer_gps" not in st.session_state:
    st.session_state.saved_customer_gps = ""

WHATSAPP_PHONE = "522381174698"
DEFAULT_BANNER = "https://raw.githubusercontent.com/Montoya100/Mostacho-Botanas-Web/main/banner.jpg"
DEFAULT_PRODUCT_IMG = "https://raw.githubusercontent.com/Montoya100/Mostacho-Botanas-Web/main/image.jpg"

def load_saved_products():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    cleaned = []
                    for idx, item in enumerate(data):
                        if isinstance(item, dict):
                            item_id = str(item.get("id", f"auto_{idx}"))
                            item["id"] = item_id if item_id.strip() != "" else f"auto_{idx}"
                            item["name"] = str(item.get("name", "Sin nombre"))
                            item["category"] = str(item.get("category", "Individual"))
                            item["price"] = float(item.get("price", 0.0))
                            item["description"] = str(item.get("description", "")) if pd.notna(item.get("description")) else ""
                            item["bestseller"] = bool(item.get("bestseller", False))
                            img_val = str(item.get("image", "")).strip()
                            item["image"] = img_val if img_val and img_val.lower() != "nan" and "placeholder" not in img_val else DEFAULT_PRODUCT_IMG
                            cleaned.append(item)
                    if cleaned:
                        return sorted(cleaned, key=lambda x: str(x.get("name", "")).lower())
        except:
            pass
    return [
        {"id": "p1", "name": "Pistaches Salados (90g)", "category": "Individual", "price": 35.0, "description": "Pistaches tostados con sal de mar.", "image": DEFAULT_PRODUCT_IMG, "bestseller": True},
        {"id": "p2", "name": "Fritura (Con Chile)", "category": "Para compartir", "price": 25.0, "description": "Crujientes frituras artesanales.", "image": DEFAULT_PRODUCT_IMG, "bestseller": True}
    ]

if "products" not in st.session_state:
    st.session_state.products = load_saved_products()

# Estilos CSS Limpios y Forzados a Tema Claro
st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
<style>
    #MainMenu, footer, header {visibility: hidden !important; display: none !important;}
    :root { color-scheme: light !important; }
    body, .stApp { background-color: #f8fafc !important; color: #1e293b !important; }
    .product-card {
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px;
        padding: 14px; margin-bottom: 14px; position: relative; box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }
    .bestseller-badge {
        position: absolute; top: 10px; right: 10px;
        background: linear-gradient(135deg, #FF4500 0%, #ff6a33);
        color: white; font-size: 0.65rem; font-weight: 800; padding: 3px 8px; border-radius: 20px;
    }
    .whatsapp-btn-active {
        background: linear-gradient(135deg, #25D366 0%, #1EBE5D 100%);
        color: white; padding: 14px; border-radius: 14px; text-align: center;
        font-weight: 800; display: block; text-decoration: none; margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

def add_to_cart(pid):
    st.session_state.cart[pid] = st.session_state.cart.get(pid, 0) + 1

def remove_from_cart(pid):
    if pid in st.session_state.cart:
        if st.session_state.cart[pid] > 1:
            st.session_state.cart[pid] -= 1
        else:
            del st.session_state.cart[pid]

total_items = sum(st.session_state.cart.values())

# Navegación superior sencilla
col_n1, col_n2, col_n3 = st.columns(3)
with col_n1:
    if st.button("🏠 Inicio", use_container_width=True):
        st.session_state.nav_view = "catalogo"
        st.rerun()
with col_n2:
    if st.button(f"🛒 Carrito ({total_items})", use_container_width=True):
        st.session_state.nav_view = "carrito"
        st.rerun()
with col_n3:
    if st.button("⚙️ Catálogo Admin", use_container_width=True):
        st.session_state.nav_view = "admin"
        st.rerun()

st.write("---")

if st.session_state.nav_view == "catalogo":
    st.markdown("### 🥜 Catálogo Mostacho Botanas")
    
    cols = st.columns(2)
    for idx, p in enumerate(st.session_state.products):
        with cols[idx % 2]:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            if p.get("bestseller", False):
                st.markdown('<div class="bestseller-badge">🔥 Más Vendido</div>', unsafe_allow_html=True)
            st.image(p.get("image", DEFAULT_PRODUCT_IMG), use_container_width=True)
            st.markdown(f"**{p.get('name')}**")
            st.markdown(f"<span style='color: #FE8330; font-weight: 900;'>${p.get('price'):.2f} MXN</span>", unsafe_allow_html=True)
            
            pid = str(p.get("id"))
            if st.button("Agregar", key=f"add_{pid}_{idx}", use_container_width=True):
                add_to_cart(pid)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.nav_view == "carrito":
    st.markdown("### 🛒 Carrito de Compras")
    if not st.session_state.cart:
        st.info("Tu carrito está vacío.")
    else:
        total_price = 0.0
        order_summary = []
        for pid, qty in list(st.session_state.cart.items()):
            p = next((item for item in st.session_state.products if str(item.get("id")) == str(pid)), None)
            if p:
                sub = p.get("price") * qty
                total_price += sub
                order_summary.append(f"- {qty}x {p.get('name')} (${sub:.2f})")
                st.write(f"**{p.get('name')}** x {qty} = ${sub:.2f} MXN")

        st.write("---")
        st.markdown(f"### Total: **${total_price:.2f} MXN**")

        # Sugerencia cruzada (Cross-selling)
        st.info("💡 **Sugerencia:** ¿Te gustaría complementar tu botana con unos pistaches o frituras extra?")

        st.write("---")
        st.subheader("📍 Datos de Entrega y Pago")
        c_name = st.text_input("Nombre completo", value=st.session_state.saved_customer_name)
        c_address = st.text_area("Dirección o referencias", value=st.session_state.saved_customer_address)
        
        # Selector de Método de pago
        pay_method = st.selectbox("Forma de pago", ["Efectivo", "Transferencia bancaria", "Tarjeta al recibir"])
        cash_note = ""
        if pay_method == "Efectivo":
            cash_amount = st.text_input("¿Con cuánto billete pagarás? (Para calcular tu cambio)")
            if cash_amount:
                cash_note = f"Paga con: {cash_amount}"

        c_gps = st.text_input("Enlace o Coordenadas de Google Maps (Ubicación GPS)", value=st.session_state.saved_customer_gps, placeholder="Ej. https://maps.app.goo.gl/... o lat,long")

        st.session_state.saved_customer_name = c_name
        st.session_state.saved_customer_address = c_address
        st.session_state.saved_customer_gps = c_gps

        # Generar mensaje de WhatsApp
        msg = f"NUEVO PEDIDO:\n" + "\n".join(order_summary) + f"\n\nTOTAL: ${total_price:.2f} MXN\nCLIENTE: {c_name}\nDIRECCION: {c_address}\nPAGO: {pay_method} {cash_note}\nGPS: {c_gps}"
        wa_url = f"https://wa.me/{WHATSAPP_PHONE}?text={urllib.parse.quote(msg)}"

        if c_name and c_address:
            st.markdown(f'<a href="{wa_url}" target="_blank" class="whatsapp-btn-active">💬 Enviar pedido por WhatsApp</a>', unsafe_allow_html=True)
        else:
            st.warning("Completa tu nombre y dirección para habilitar el botón de WhatsApp.")

elif st.session_state.nav_view == "admin":
    st.markdown("### ⚙️ Administración de Productos")
    st.info("Aquí puedes ver y editar tus productos rápidamente.")
    df = pd.DataFrame(st.session_state.products)
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("Guardar Cambios"):
        st.session_state.products = edited_df.to_dict(orient="records")
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.products, f, ensure_ascii=False, indent=4)
        st.success("¡Guardado con éxito!")
        st.rerun()