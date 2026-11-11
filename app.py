import streamlit as st
import pandas as pd
import urllib.parse
import requests
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(
    page_title="Mostacho Botanas Web",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Inicializar Estado
if "cart" not in st.session_state:
    st.session_state.cart = {}

if "nav_tab" not in st.session_state:
    st.session_state.nav_tab = "Inicio"

LOYVERSE_TOKEN = "1a4ee083d81e4525a48503180767c22d"
WHATSAPP_PHONE = "522381174698"

# Enlace de tu logo en GitHub (Asegúrate de que coincida exactamente con el archivo .png de tu repo)
LOGO_URL = "https://raw.githubusercontent.com/tu-usuario/tu-repositorio/main/assets/logo.png"

@st.cache_data(ttl=60)
def fetch_loyverse_products():
    headers = {
        "Authorization": f"Bearer {LOYVERSE_TOKEN}",
        "Content-Type": "application/json"
    }
    products_list = []
    try:
        items_res = requests.get("https://api.loyverse.com/v1.0/items", headers=headers, timeout=5)
        if items_res.status_code == 200:
            for item in items_res.json().get("items", []):
                cat_name = item.get("category_name", "Chicos")
                if not cat_name:
                    cat_name = "Chicos"
                    
                variants = item.get("variants", [])
                item_name = item.get("item_name", "Producto")
                desc = item.get("description", "Snack seleccionado de alta calidad.")
                
                if variants:
                    for var in variants:
                        price = 0.0
                        price_val = var.get("price")
                        if price_val is None and "store_prices" in var:
                            store_prices = var.get("store_prices", {})
                            if store_prices:
                                price_val = list(store_prices.values())[0]
                        try:
                            price = float(price_val or 0.0)
                        except:
                            price = 0.0

                        var_name = var.get("variant_name", "")
                        display_name = f"{item_name} ({var_name})" if var_name and var_name != "Default" else item_name

                        products_list.append({
                            "id": str(var.get("variant_id", item.get("id"))),
                            "name": display_name,
                            "category": cat_name,
                            "price": price,
                            "description": desc,
                            "image": "https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=300"
                        })
    except:
        pass

    if not products_list:
        products_list = [
            {"id": "p1", "name": "Pistaches Salados (90g)", "category": "Chicos", "price": 35.0, "description": "Pistaches tostados con sal de mar.", "image": "https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=300"},
            {"id": "p2", "name": "Mix Botanero (1kg)", "category": "Para compartir", "price": 180.0, "description": "Mezcla ideal para reuniones.", "image": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=300"},
            {"id": "p3", "name": "Frasco Regalo Pistache", "category": "Detalles", "price": 150.0, "description": "Frasco de cristal decorado.", "image": "https://images.unsplash.com/photo-1508061252966-173859db501d?w=300"}
        ]
    return products_list

if "products" not in st.session_state:
    st.session_state.products = fetch_loyverse_products()

# 3. Estilos CSS: Corrección definitiva de bordes negros en barra de búsqueda web y blindaje claro
st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />

<style>
    header { visibility: hidden !important; height: 0px !important; display: none !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 3rem !important;
        background-color: #f8f7f4 !important;
    }

    .stApp, body, html, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f8f7f4 !important;
        color: #222222 !important;
    }

    div[data-testid="stVerticalBlock"], div[data-testid="stHorizontalBlock"], div.element-container, .stAlert, div[data-testid="stInfoBox"] {
        background-color: transparent !important;
        color: #222222 !important;
    }

    /* BOTONES NARANJAS CON TEXTO BLANCO */
    button, .stButton > button, div[data-testid="stButton"] > button {
        background-color: #ff5200 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(255, 82, 0, 0.25) !important;
    }
    button:hover, .stButton > button:hover {
        background-color: #e04800 !important;
        color: #ffffff !important;
    }
    button p, .stButton > button p, button span {
        color: #ffffff !important;
    }

    /* BARRA DE BÚSQUEDA Y CAMPOS: Eliminar bordes negros/sombras al enfocar en versión web */
    input, textarea, select, div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"], div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #222222 !important;
        -webkit-text-fill-color: #222222 !important;
        border-color: #cbd5e0 !important;
        border-radius: 30px !important;
    }
    input:focus, textarea:focus, div[data-baseweb="input"]:focus-within {
        border-color: #ff5200 !important;
        box-shadow: 0 0 0 2px rgba(255,82,0,0.2) !important;
    }
    input::placeholder, textarea::placeholder {
        color: #718096 !important;
        -webkit-text-fill-color: #718096 !important;
    }

    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined' !important;
        font-size: 20px !important;
        vertical-align: middle;
        line-height: 1;
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    }

    .product-card {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 20px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .product-title {
        font-size: 1.1rem;
        font-weight: 800;
        margin-bottom: 2px;
        color: #1a202c !important;
    }
    .product-desc {
        font-size: 0.82rem;
        color: #718096 !important;
        margin-bottom: 6px;
    }
    .product-price {
        font-size: 1.05rem;
        font-weight: bold;
        color: #ff5200 !important;
    }

    .promo-banner {
        background: linear-gradient(135deg, #ff5200 0%, #ff7300 100%);
        color: white;
        padding: 14px 18px;
        border-radius: 30px;
        text-align: center;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(255,82,0,0.2);
    }

    .slideshow-container {
        position: relative;
        max-width: 100%;
        height: 230px;
        margin-bottom: 18px;
        border-radius: 24px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }
    .slide {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        opacity: 0;
        animation: slideAnimation 12s infinite;
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: flex-end;
        padding: 16px;
    }
    .slide:nth-child(1) { animation-delay: 0s; }
    .slide:nth-child(2) { animation-delay: 4s; }
    .slide:nth-child(3) { animation-delay: 8s; }
    
    @keyframes slideAnimation {
        0% { opacity: 0; }
        10% { opacity: 1; }
        33% { opacity: 1; }
        43% { opacity: 0; }
        100% { opacity: 0; }
    }
    .slide-text {
        background: rgba(255, 82, 0, 0.85);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

def add_to_cart(product_id):
    st.session_state.cart[product_id] = st.session_state.cart.get(product_id, 0) + 1
    st.toast("Producto agregado al carrito")

def remove_from_cart(product_id):
    if product_id in st.session_state.cart:
        if st.session_state.cart[product_id] > 1:
            st.session_state.cart[product_id] -= 1
        else:
            del st.session_state.cart[product_id]

total_items = sum(st.session_state.cart.values())
tab = st.session_state.nav_tab

# 4. Header Superior con Logo y Carrito con Icono Outline
col_title, col_cart_btn = st.columns([3, 1])

with col_title:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px;">
        <img src="{LOGO_URL}" style="width: 42px; height: 42px; border-radius: 50%; object-fit: cover; border: 2px solid #ff5200;" onerror="this.style.display='none'" />
        <div>
            <h2 style="margin: 0; font-size: 1.35rem; font-weight: 900; color: #1a202c;">Mostacho Botanas</h2>
            <span style="font-size: 0.8rem; color: #718096; font-weight: 500;">Catálogo y Pedidos</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_cart_btn:
    cart_label = f":material/shopping_cart: Carrito ({total_items})" if total_items > 0 else ":material/shopping_cart: Carrito"
    if st.button(cart_label, use_container_width=True):
        st.session_state.nav_tab = "Carrito" if st.session_state.nav_tab != "Carrito" else "Inicio"
        st.rerun()

st.write("---")

# 5. Vistas
if tab == "Inicio":
    col_sh1, col_sh2 = st.columns([3, 1])
    with col_sh2:
        if st.button(":material/share: Compartir", use_container_width=True):
            st.toast("Enlace listo para enviar por WhatsApp")

    st.markdown(
        '<div class="promo-banner"><span class="material-symbols-outlined" style="vertical-align: -4px; margin-right: 6px;">local_shipping</span> ¡Envíos locales y entregas directas en ruta! Pide fácil y rápido</div>', 
        unsafe_allow_html=True
    )
    
    st.markdown("""
    <div class="slideshow-container">
        <div class="slide" style="background-image: url('https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=800');">
            <div class="slide-text">Pistaches y Garbanzos • Calidad Premium</div>
        </div>
        <div class="slide" style="background-image: url('https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800');">
            <div class="slide-text">Snacks y Semillas Seleccionadas</div>
        </div>
        <div class="slide" style="background-image: url('https://images.unsplash.com/photo-1508061252966-173859db501d?w=800');">
            <div class="slide-text">Distribución Directa en Ruta</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    search_query = st.text_input("Buscar productos...", placeholder="Escribe el nombre del producto...", label_visibility="collapsed")

    all_categories = sorted(list(set([p.get("category", "Chicos") for p in st.session_state.products if isinstance(p, dict)])))
    if not all_categories:
        all_categories = ["Chicos", "Para compartir", "Detalles"]

    selected_category = st.radio("Categorías", all_categories, horizontal=True, label_visibility="collapsed")
    st.write("---")

    try:
        current_products_list = st.session_state.products
        filtered_products = [
            p for p in current_products_list 
            if isinstance(p, dict) and p.get("category") == selected_category and (search_query.lower() in str(p.get("name", "")).lower() or search_query.lower() in str(p.get("description", "")).lower())
        ]
    except:
        filtered_products = []

    if not filtered_products:
        st.info("No se encontraron productos en esta categoría.")
    else:
        for product in filtered_products:
            pid = product.get("id")
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            col_img, col_info, col_action = st.columns([1, 2.5, 1.5])
            
            with col_img:
                st.image(product.get("image", "https://via.placeholder.com/300"), use_container_width=True)
                
            with col_info:
                st.markdown(f'<div class="product-title">{product.get("name")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="product-desc">{product.get("description")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="product-price">${float(product.get("price", 0)):.2f} MXN</div>', unsafe_allow_html=True)
                
            with col_action:
                qty_in_cart = st.session_state.cart.get(pid, 0)
                if qty_in_cart == 0:
                    if st.button("Agregar", key=f"add_{pid}", use_container_width=True):
                        add_to_cart(pid)
                        st.rerun()
                else:
                    sub_c1, sub_c2, sub_c3 = st.columns([1, 1, 1])
                    with sub_c1:
                        if st.button("-", key=f"minus_{pid}", use_container_width=True):
                            remove_from_cart(pid)
                            st.rerun()
                    with sub_c2:
                        st.markdown(f"<div style='text-align: center; font-weight: bold;'>{qty_in_cart}</div>", unsafe_allow_html=True)
                    with sub_c3:
                        if st.button("+", key=f"plus_{pid}", use_container_width=True):
                            add_to_cart(pid)
                            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif tab == "Carrito":
    if st.button(":material/arrow_back: Volver al Catálogo", use_container_width=False):
        st.session_state.nav_tab = "Inicio"
        st.rerun()
        
    st.markdown("### :material/shopping_cart: Carrito de Compras")
    st.caption(f"Artículos seleccionados: {total_items}")
    
    if not st.session_state.cart:
        st.info("Tu carrito está vacío. Agrega productos desde el inicio.")
    else:
        total_price = 0.0
        order_summary = []
        
        st.write("---")
        for item_id, qty in list(st.session_state.cart.items()):
            p = next((item for item in st.session_state.products if item.get("id") == item_id), None)
            if p:
                subtotal = float(p.get("price", 0)) * qty
                total_price += subtotal
                order_summary.append(f"• {qty}x {p.get('name')} - ${subtotal:.2f}")
                
                col_c1, col_c2 = st.columns([3, 1])
                with col_c1:
                    st.markdown(f"**{p.get('name')}**")
                    st.caption(f"{qty} x ${float(p.get('price', 0)):.2f} = ${subtotal:.2f}")
                with col_c2:
                    if st.button(":material/delete:", key=f"del_cart_{item_id}"):
                        del st.session_state.cart[item_id]
                        st.rerun()
                        
        st.write("---")
        st.markdown(f"### :material/payments: Total a Pagar: **${total_price:.2f} MXN**")
        
        st.subheader(":material/local_shipping: Datos de Entrega")
        customer_name = st.text_input("Nombre del cliente", placeholder="Ej. Juan Pérez")
        customer_address = st.text_area("Dirección / Referencias", placeholder="Calle, número, colonia...")
        customer_notes = st.text_input("Notas adicionales", placeholder="Ej. Cambio de $500")
        
        order_folio = f"MOSTACHO-{datetime.now().strftime('%H%M%S')}"
        order_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        msg_header = f"📌 *NUEVO PEDIDO* `[{order_folio}]`\n📅 *Fecha:* {order_date}\n\n"
        msg_items = "*Detalle de Productos:*\n" + "\n".join(order_summary) + "\n\n"
        msg_total = f"*Total:* ${total_price:.2f} MXN\n\n"
        msg_customer = f"*Cliente:* {customer_name if customer_name else 'No especificado'}\n"
        msg_address = f"*Dirección:* {customer_address if customer_address else 'No especificada'}\n"
        msg_notes = f"*Notas:* {customer_notes}\n" if customer_notes else ""
        
        full_message = msg_header + msg_items + msg_total + msg_customer + msg_address + msg_notes
        encoded_message = urllib.parse.quote(full_message)
        whatsapp_url = f"https://wa.me/{WHATSAPP_PHONE}?text={encoded_message}"
        
        if customer_name and customer_address:
            st.link_button("Enviar Pedido por WhatsApp", whatsapp_url, use_container_width=True)
        else:
            st.warning("Escribe tu Nombre y Dirección para habilitar el envío por WhatsApp.")

# 6. Panel de Administración Discreto
st.write("---")
col_space, col_admin_btn = st.columns([5, 1])
with col_admin_btn:
    if st.button(":material/settings: Admin", use_container_width=True):
        st.session_state.show_admin_login = not st.session_state.get("show_admin_login", False)

if st.session_state.get("show_admin_login", False):
    admin_key = st.text_input("Clave de acceso", type="password", key="admin_pass_mini", placeholder="Contraseña...")
    if admin_key == "1234":
        st.success("Acceso concedido")
        df_current = pd.DataFrame(st.session_state.products)
        edited_df = st.data_editor(df_current, num_rows="dynamic", key="editor_admin_table")
        if st.button("Guardar cambios"):
            st.session_state.products = edited_df.to_dict(orient="records")
            st.success("¡Actualizado con éxito!")
            st.rerun()
    elif admin_key:
        st.error("Incorrecta")