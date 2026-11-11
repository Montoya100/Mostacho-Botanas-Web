import streamlit as st
import pandas as pd
import urllib.parse
import requests
import json
import os
from datetime import datetime

# Enlace Raw real de tu logo en tu repositorio de GitHub
LOGO_URL = "https://raw.githubusercontent.com/Montoya100/Mostacho-Botanas-Web/main/logo.png"
DATA_FILE = "productos_mostacho.json"
POPULAR_FILE = "populares_mostacho.json"

# 1. Configuración de la página
st.set_page_config(
    page_title="Mostacho Botanas",
    page_icon=LOGO_URL,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Inicializar Estado
if "cart" not in st.session_state:
    st.session_state.cart = {}

if "nav_tab" not in st.session_state:
    st.session_state.nav_tab = "Inicio"

if "selected_cat" not in st.session_state:
    st.session_state.selected_cat = "Todo"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

LOYVERSE_TOKEN = "1a4ee083d81e4525a48503180767c22d"
WHATSAPP_PHONE = "522381174698"

# ==========================================
# CONFIGURACIÓN DE IMÁGENES DEL CARRUSEL (DIAPOSITIVAS)
SLIDER_ITEMS = [
    {
        "url": "https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=1200",
        "caption": "Pistaches y Garbanzos • Calidad Premium"
    },
    {
        "url": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=1200",
        "caption": "Snacks y Semillas Seleccionadas"
    },
    {
        "url": "https://images.unsplash.com/photo-1508061252966-173859db501d?w=1200",
        "caption": "Distribución Directa en Ruta"
    }
]
# ==========================================

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
                cat_name = item.get("category_name", "Individual")
                if not cat_name:
                    cat_name = "Individual"
                
                cat_lower = cat_name.lower()
                if "compartir" in cat_lower or "familiar" in cat_lower:
                    category_mapped = "Para compartir"
                else:
                    category_mapped = "Individual"
                    
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
                            "category": category_mapped,
                            "price": price,
                            "description": desc,
                            "image": "https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=300"
                        })
    except:
        pass

    if not products_list:
        products_list = [
            {"id": "p1", "name": "Pistaches Salados (90g)", "category": "Individual", "price": 35.0, "description": "Pistaches tostados con sal de mar.", "image": "https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=300"},
            {"id": "p2", "name": "Mix Botanero (1kg)", "category": "Para compartir", "price": 180.0, "description": "Mix ideal para reuniones.", "image": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=300"},
            {"id": "p3", "name": "Cahuates Japoneses (200g)", "category": "Individual", "price": 25.0, "description": "Cahuates crujientes tradicionales.", "image": "https://images.unsplash.com/photo-1508061252966-173859db501d?w=300"}
        ]
    return products_list

# Sistema de Persistencia de Productos (JSON)
def load_saved_products():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except:
            pass
    initial_products = fetch_loyverse_products()
    save_products_to_file(initial_products)
    return initial_products

def save_products_to_file(prod_list):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(prod_list, f, ensure_ascii=False, indent=4)
    except:
        pass

# Sistema de Persistencia de Populares (JSON)
def load_saved_populares():
    if os.path.exists(POPULAR_FILE):
        try:
            with open(POPULAR_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except:
            pass
    # Predeterminados iniciales
    default_pops = [
        {"id": "p1", "name": "Pistaches Salados (90g)", "price": 35.0, "image": "https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=300"},
        {"id": "p2", "name": "Mix Botanero (1kg)", "price": 180.0, "image": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=300"},
        {"id": "p3", "name": "Cahuates Japoneses (200g)", "price": 25.0, "image": "https://images.unsplash.com/photo-1508061252966-173859db501d?w=300"}
    ]
    save_populares_to_file(default_pops)
    return default_pops

def save_populares_to_file(pop_list):
    try:
        with open(POPULAR_FILE, "w", encoding="utf-8") as f:
            json.dump(pop_list, f, ensure_ascii=False, indent=4)
    except:
        pass

if "products" not in st.session_state:
    st.session_state.products = load_saved_products()

if "popular_items" not in st.session_state:
    st.session_state.popular_items = load_saved_populares()

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# 3. Colores dinámicos limpios
is_dark = st.session_state.dark_mode

bg_color = "#121824" if is_dark else "#f8f7f4"
text_color = "#f1f5f9" if is_dark else "#222222"
sub_text_color = "#94a3b8" if is_dark else "#4a5568"
card_bg = "#1e293b" if is_dark else "#ffffff"
border_color = "#334155" if is_dark else "#e2e8f0"
input_bg = "#0f172a" if is_dark else "#ffffff"

st.markdown(f"""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />

<style>
    header {{ visibility: hidden !important; height: 0px !important; display: none !important; }}
    #MainMenu {{ visibility: hidden !important; }}
    footer {{ visibility: hidden !important; }}
    .stDeployButton {{ display: none !important; }}
    
    .block-container {{
        padding-top: 0.5rem !important;
        padding-bottom: 3rem !important;
        background-color: {bg_color} !important;
        animation: fadeIn 0.4s ease-in-out;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .stApp, body, html, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}

    div[data-testid="stVerticalBlock"], div[data-testid="stHorizontalBlock"], div.element-container {{
        background-color: transparent !important;
        color: {text_color} !important;
    }}

    .app-title {{
        font-size: 2.3rem !important;
        font-weight: 900 !important;
        color: {text_color} !important;
        margin: 0 !important;
        line-height: 1.0 !important;
    }}
    .app-subtitle {{
        font-size: 0.9rem !important;
        color: {sub_text_color} !important;
        font-weight: 700 !important;
        margin-top: 2px !important;
        display: block;
    }}

    .cart-cta-container button {{
        min-height: 75px !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
    }}

    .whatsapp-btn-disabled {{
        background-color: {"#334155" if is_dark else "#1a202c"} !important;
        color: #ffffff !important;
        padding: 14px;
        border-radius: 14px;
        text-align: center;
        font-weight: 700;
        font-size: 0.95rem;
        margin-top: 10px;
        display: block;
        width: 100%;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }}

    .whatsapp-btn-active {{
        background: linear-gradient(135deg, #ff5200 0%, #ff7300 100%) !important;
        color: #ffffff !important;
        padding: 14px;
        border-radius: 14px;
        text-align: center;
        font-weight: 800;
        font-size: 1.05rem;
        margin-top: 10px;
        display: block;
        width: 100%;
        text-decoration: none;
        box-shadow: 0 4px 15px rgba(255, 82, 0, 0.4);
        animation: pulseButton 1.5s infinite;
        transition: transform 0.2s ease;
    }}
    .whatsapp-btn-active:hover {{
        transform: scale(1.02);
    }}

    @keyframes pulseButton {{
        0% {{ box-shadow: 0 0 0 0 rgba(255, 82, 0, 0.5); }}
        70% {{ box-shadow: 0 0 0 10px rgba(255, 82, 0, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(255, 82, 0, 0); }}
    }}

    label p, .stTextInput label, .stTextArea label, [data-testid="stWidgetLabel"] p {{
        color: {text_color} !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }}

    button, .stButton > button, div[data-testid="stButton"] > button {{
        background-color: #ff5200 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(255, 82, 0, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
    }}
    button:hover, .stButton > button:hover {{
        background-color: #e04800 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(255, 82, 0, 0.35) !important;
        color: #ffffff !important;
    }}
    button p, .stButton > button p, button span {{
        color: #ffffff !important;
    }}

    div[data-testid="column"] button {{
        font-size: 1.6rem !important;
        font-weight: 900 !important;
        padding: 4px 0px !important;
        min-height: 48px !important;
    }}
    .qty-number {{
        font-size: 1.5rem !important;
        font-weight: 900 !important;
        text-align: center;
        color: {text_color} !important;
        margin-top: 10px;
    }}

    input, textarea, select, div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"], div[data-baseweb="select"] {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }}
    input:focus, textarea:focus, div[data-baseweb="input"]:focus-within {{
        border-color: #ff5200 !important;
        box-shadow: 0 0 0 3px rgba(255,82,0,0.18) !important;
    }}
    input::placeholder, textarea::placeholder {{
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
    }}

    .material-symbols-outlined {{
        font-family: 'Material Symbols Outlined' !important;
        font-size: 22px !important;
        vertical-align: middle;
        line-height: 1;
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    }}

    .product-card {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    }}
    .product-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.07);
    }}
    .product-title {{
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 2px;
        color: {text_color} !important;
    }}
    .product-desc {{
        font-size: 0.85rem;
        color: {sub_text_color} !important;
        margin-bottom: 6px;
    }}
    .product-price {{
        font-size: 1.15rem;
        font-weight: bold;
        color: #ff5200 !important;
    }}

    .promo-banner {{
        background: linear-gradient(135deg, #ff5200 0%, #ff7300 100%);
        color: white;
        padding: 14px 18px;
        border-radius: 16px;
        text-align: center;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(255,82,0,0.2);
    }}

    .slideshow-container {{
        position: relative;
        max-width: 100%;
        height: 280px;
        margin-bottom: 18px;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid {border_color};
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        background-color: #000000;
    }}
    .slide {{
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        opacity: 0;
        animation: slideAnimation 12s infinite;
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: flex-end;
        padding: 16px;
    }}
    .slide:nth-child(1) {{ animation-delay: 0s; }}
    .slide:nth-child(2) {{ animation-delay: 4s; }}
    .slide:nth-child(3) {{ animation-delay: 8s; }}
    
    @keyframes slideAnimation {{
        0% {{ opacity: 0; }}
        12% {{ opacity: 1; }}
        33% {{ opacity: 1; }}
        45% {{ opacity: 0; }}
        100% {{ opacity: 0; }}
    }}
    .slide-text {{
        background: rgba(255, 82, 0, 0.88);
        color: white;
        padding: 6px 14px;
        border-radius: 12px;
        font-size: 0.9rem;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }}
</style>
""", unsafe_allow_html=True)

def add_to_cart(product_id):
    st.session_state.cart[product_id] = st.session_state.cart.get(product_id, 0) + 1
    st.toast("¡Producto añadido al carrito con éxito!", icon="🛒")

def remove_from_cart(product_id):
    if product_id in st.session_state.cart:
        if st.session_state.cart[product_id] > 1:
            st.session_state.cart[product_id] -= 1
        else:
            del st.session_state.cart[product_id]

total_items = sum(st.session_state.cart.values())
tab = st.session_state.nav_tab

# 4. Header Superior con Logo limpio y Botón de Carrito imponente
col_title, col_cart_btn = st.columns([3, 1])

with col_title:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px;">
        <img src="{LOGO_URL}" style="width: 58px; height: 58px; object-fit: contain; background: transparent;" onerror="this.style.display='none'" />
        <div>
            <h1 class="app-title">Mostacho Botanas</h1>
            <span class="app-subtitle">Catálogo y pedidos en línea</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_cart_btn:
    st.write("") 
    cart_label = f"Carrito ({total_items})" if total_items > 0 else "Carrito"
    st.markdown('<div class="cart-cta-container">', unsafe_allow_html=True)
    if st.button(":material/shopping_cart: " + cart_label, use_container_width=True):
        st.session_state.nav_tab = "Carrito" if st.session_state.nav_tab != "Carrito" else "Inicio"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# 5. Vistas
if tab == "Inicio":
    st.markdown(
        '<div class="promo-banner"><span class="material-symbols-outlined" style="vertical-align: -4px; margin-right: 6px;">local_shipping</span> ¡Envíos locales y entregas directas en ruta! Pide fácil y rápido</div>', 
        unsafe_allow_html=True
    )
    
    # CARRUSEL AUTOMÁTICO SEGURO
    slides_html = '<div class="slideshow-container">'
    for slide_item in SLIDER_ITEMS:
        slides_html += f'''
        <div class="slide" style="background-image: url('{slide_item["url"]}');">
            <div class="slide-text">{slide_item["caption"]}</div>
        </div>
        '''
    slides_html += '</div>'
    st.markdown(slides_html, unsafe_allow_html=True)

    # 1. BARRA DE BÚSQUEDA
    search_query = st.text_input("Buscar productos...", placeholder="Escribe el nombre del producto...", label_visibility="collapsed")

    # 2. PRODUCTOS POPULARES (Dinamicos seleccionados desde admin)
    st.write("")
    st.markdown("### Productos Populares")
    st.caption("Toca cualquier producto popular para agregarlo directo a tu carrito:")
    
    popular_products = st.session_state.popular_items
    if not popular_products:
        popular_products = [
            {"id": "p1", "name": "Pistaches Salados (90g)", "price": 35.0, "image": "https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=300"}
        ]
    
    pop_cols = st.columns(len(popular_products))
    for idx, pop_p in enumerate(popular_products):
        with pop_cols[idx]:
            st.markdown(f"""
            <div style="background: {card_bg}; border: 1px solid {border_color}; border-radius: 12px; padding: 10px; text-align: center; margin-bottom: 10px;">
                <img src="{pop_p.get('image', 'https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=300')}" style="width: 100%; height: 90px; object-fit: cover; border-radius: 8px;" />
                <div style="font-weight: 800; font-size: 0.9rem; margin-top: 6px; color: {text_color};">{pop_p.get('name', 'Producto')}</div>
                <div style="color: #ff5200; font-weight: bold; font-size: 0.95rem;">${float(pop_p.get('price', 0)):.2f} MXN</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Agregar +", key=f"quick_add_{pop_p.get('id', idx)}", use_container_width=True):
                prod_id = pop_p.get('id', str(idx))
                if not any(p.get("id") == prod_id for p in st.session_state.products):
                    st.session_state.products.append({
                        "id": prod_id,
                        "name": pop_p.get('name'),
                        "category": "Individual",
                        "price": pop_p.get('price'),
                        "description": "Producto popular seleccionado.",
                        "image": pop_p.get('image')
                    })
                    save_products_to_file(st.session_state.products)
                add_to_cart(prod_id)
                st.rerun()

    st.write("---")

    # 3. SECCIÓN DE CATEGORÍAS (Con Título Legible)
    st.markdown("### Categorías")
    category_options = ["Todo", "Individual", "Para compartir"]
    
    cat_cols = st.columns(len(category_options))
    for i, cat in enumerate(category_options):
        with cat_cols[i]:
            is_active = (st.session_state.selected_cat == cat)
            display_label = f"● {cat}" if is_active else cat
            
            if st.button(display_label, use_container_width=True):
                st.session_state.selected_cat = cat
                st.rerun()

    # Botón de compartir abajo de las categorías
    st.write("")
    col_space_sh, col_share_btn = st.columns([3, 1])
    with col_share_btn:
        if st.button(":material/share: Compartir", use_container_width=True):
            st.toast("Enlace listo para enviar por WhatsApp")

    st.write("---")

    # 4. LISTADO DE PRODUCTOS GENERALES FILTRADOS
    try:
        current_products_list = st.session_state.products
        
        if st.session_state.selected_cat == "Todo":
            cat_filtered = current_products_list
        else:
            cat_filtered = [p for p in current_products_list if p.get("category") == st.session_state.selected_cat]

        filtered_products = [
            p for p in cat_filtered 
            if isinstance(p, dict) and (search_query.lower() in str(p.get("name", "")).lower() or search_query.lower() in str(p.get("description", "")).lower())
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
                        st.markdown(f"<div class='qty-number'>{qty_in_cart}</div>", unsafe_allow_html=True)
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
                order_summary.append(f"- {qty}x {p.get('name')} - ${subtotal:.2f} MXN")
                
                col_c1, col_c2 = st.columns([3, 1])
                with col_c1:
                    st.markdown(f"**{p.get('name')}**")
                    st.caption(f"{qty} x ${float(p.get('price', 0)):.2f} = ${subtotal:.2f}")
                with col_c2:
                    if st.button(":material/delete: Quitar", key=f"del_cart_{item_id}", use_container_width=True):
                        del st.session_state.cart[item_id]
                        st.rerun()
                        
        st.write("---")
        st.markdown(f"### :material/payments: Total a Pagar: **${total_price:.2f} MXN**")
        
        st.subheader(":material/local_shipping: Datos de Entrega")
        customer_name = st.text_input("Nombre del cliente (Obligatorio)", placeholder="Ej. Juan Pérez")
        customer_address = st.text_area("Dirección / Referencias (Obligatorio)", placeholder="Calle, número, colonia...")
        customer_notes = st.text_input("Notas adicionales (Opcional)", placeholder="Ej. Cambio de $500")
        
        order_folio = f"MOSTACHO-{datetime.now().strftime('%H%M%S')}"
        order_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        msg_header = f"NUEVO PEDIDO [{order_folio}]\nFecha: {order_date}\n\n"
        msg_items = "DETALLE DE PRODUCTOS:\n" + "\n".join(order_summary) + "\n\n"
        msg_total = f"TOTAL: ${total_price:.2f} MXN\n\n"
        msg_customer = f"CLIENTE: {customer_name}\n"
        msg_address = f"DIRECCION: {customer_address}\n"
        msg_notes = f"NOTAS: {customer_notes}\n" if customer_notes else ""
        
        full_message = msg_header + msg_items + msg_total + msg_customer + msg_address + msg_notes
        encoded_message = urllib.parse.quote(full_message)
        whatsapp_url = f"https://wa.me/{WHATSAPP_PHONE}?text={encoded_message}"
        
        st.write("")
        if customer_name.strip() and customer_address.strip():
            st.markdown(
                f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn-active">Enviar Pedido por WhatsApp ({order_folio})</a>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="whatsapp-btn-disabled">Completa Nombre y Dirección para activar el envío</div>',
                unsafe_allow_html=True
            )

# 6. Panel de Administración y Configuración en POP-UP (Modal)
st.write("---")
col_theme, col_space_footer, col_admin = st.columns([1, 4, 1])

with col_theme:
    theme_icon = ":material/light_mode:" if is_dark else ":material/dark_mode:"
    if st.button(theme_icon, use_container_width=True, help="Cambiar tema"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

@st.dialog("Panel de Administración y Configuración")
def admin_modal():
    if not st.session_state.admin_authenticated:
        st.subheader("Acceso Restringido")
        pass_input = st.text_input("Ingresa la contraseña de administrador", type="password", placeholder="Clave de 4 dígitos...")
        if st.button("Ingresar"):
            if pass_input == "7031":
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    else:
        st.success("¡Acceso concedido!")
        
        # NOTAS Y GUÍA DE TAMAÑOS DE IMAGEN
        st.info(
            "📌 **GUÍA DE TAMAÑOS DE IMAGEN RECOMENDADOS:**\n\n"
            "• **Imágenes del Carrusel (Banner):** `1200 x 600 px` (Proporción 2:1 horizontal).\n"
            "• **Imágenes de Productos:** `600 x 600 px` (Proporción 1:1 cuadrada).\n\n"
            "*Usar estas medidas evita que las imágenes se compriman, estiren o distorsionen al cambiar entre versión web y móvil.*"
        )
        
        tab_prod, tab_pop = st.tabs(["📦 Editar Productos", "⭐ Seleccionar Populares"])
        
        with tab_prod:
            st.markdown("### Inventario de Productos")
            st.caption("Modifica precios, nombres o asigna la categoría correcta:")
            df_current = pd.DataFrame(st.session_state.products)
            
            column_config = {
                "category": st.column_config.SelectboxColumn(
                    "Categoría",
                    help="Selecciona estrictamente Individual o Para compartir",
                    options=["Individual", "Para compartir"],
                    required=True
                )
            }
            
            edited_df = st.data_editor(
                df_current, 
                num_rows="dynamic", 
                key="editor_admin_table",
                column_config=column_config
            )
            
            if st.button("Guardar Cambios de Productos"):
                updated_list = edited_df.to_dict(orient="records")
                st.session_state.products = updated_list
                save_products_to_file(updated_list)
                st.success("¡Productos guardados permanentemente!")
                st.rerun()

        with tab_pop:
            st.markdown("### Seleccionar Productos Populares")
            st.caption("Elige cuáles productos aparecerán destacados en la sección de populares:")
            
            current_pop_ids = [p.get("id") for p in st.session_state.popular_items]
            
            selected_populares_new = []
            for prod in st.session_state.products:
                p_id = prod.get("id")
                p_name = prod.get("name")
                is_currently_pop = p_id in current_pop_ids
                
                if st.checkbox(f"{p_name} (${prod.get('price', 0)} MXN)", value=is_currently_pop, key=f"check_pop_{p_id}"):
                    selected_populares_new.append({
                        "id": p_id,
                        "name": p_name,
                        "price": prod.get("price"),
                        "image": prod.get("image", "https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=300")
                    })
            
            if st.button("Guardar Productos Populares"):
                if selected_populares_new:
                    st.session_state.popular_items = selected_populares_new
                    save_populares_to_file(selected_populares_new)
                    st.success("¡Productos populares actualizados con éxito!")
                    st.rerun()
                else:
                    st.warning("Debes seleccionar al menos un producto popular.")
        
        st.write("---")
        if st.button("Cerrar Sesión de Admin"):
            st.session_state.admin_authenticated = False
            st.rerun()

with col_admin:
    if st.button(":material/settings: Admin", use_container_width=True):
        admin_modal()