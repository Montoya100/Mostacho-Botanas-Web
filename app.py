import streamlit as st
import pandas as pd
import urllib.parse
import requests
import json
import os
from datetime import datetime

LOGO_URL = "https://raw.githubusercontent.com/Montoya100/Mostacho-Botanas-Web/main/logo.png"
DATA_FILE = "productos_mostacho.json"
POPULAR_FILE = "populares_mostacho.json"
BANNER_FILE = "banner_mostacho.json"
UPLOAD_DIR = "uploaded_images"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

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

if "nav_view" not in st.session_state:
    st.session_state.nav_view = "catalogo"

if "selected_cat" not in st.session_state:
    st.session_state.selected_cat = "Todo"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

LOYVERSE_TOKEN = "1a4ee083d81e4525a48503180767c22d"
WHATSAPP_PHONE = "522381174698"

# ==========================================
# LIGAS POR DEFECTO CON TU IMAGEN DE GITHUB
# ==========================================
DEFAULT_BANNER = "https://raw.githubusercontent.com/Montoya100/Mostacho-Botanas-Web/main/banner.jpg"
DEFAULT_PRODUCT_IMG = "https://raw.githubusercontent.com/Montoya100/Mostacho-Botanas-Web/main/image.jpg"

def load_saved_banner():
    if os.path.exists(BANNER_FILE):
        try:
            with open(BANNER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    url = data.get("url", "").strip()
                    if url:
                        return url
        except:
            pass
    return DEFAULT_BANNER

def save_banner_to_file(url):
    try:
        data = {"url": url}
        with open(BANNER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except:
        pass

if "banner_url" not in st.session_state:
    st.session_state.banner_url = load_saved_banner()

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
                if "compartir" in cat_lower or "familiar" in cat_lower or "fritura" in cat_lower:
                    category_mapped = "Para compartir"
                else:
                    category_mapped = "Individual"
                    
                variants = item.get("variants", [])
                item_name = item.get("item_name", "Producto")
                desc = item.get("description", "")
                
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
                            "image": DEFAULT_PRODUCT_IMG
                        })
    except:
        pass

    if not products_list:
        products_list = [
            {"id": "p1", "name": "Pistaches Salados (90g)", "category": "Individual", "price": 35.0, "description": "Pistaches tostados con sal de mar.", "image": DEFAULT_PRODUCT_IMG},
            {"id": "p2", "name": "Fritura (Con Chile)", "category": "Para compartir", "price": 25.0, "description": "Crujientes frituras artesanales.", "image": DEFAULT_PRODUCT_IMG},
            {"id": "p3", "name": "Fritura (Sin Chile)", "category": "Para compartir", "price": 25.0, "description": "Ideales para toda la familia.", "image": DEFAULT_PRODUCT_IMG}
        ]
    return products_list

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
                            img_val = item.get("image", "")
                            
                            if not img_val or str(img_val).strip() == "" or str(img_val).strip() == "nan" or "placeholder" in str(img_val) or "imgur" in str(img_val):
                                item["image"] = DEFAULT_PRODUCT_IMG
                            else:
                                item["image"] = str(img_val).strip()
                                
                            cleaned.append(item)
                    if cleaned:
                        cleaned = sorted(cleaned, key=lambda x: str(x.get("name", "")).lower())
                        return cleaned
        except:
            pass
    initial_products = fetch_loyverse_products()
    initial_products = sorted(initial_products, key=lambda x: str(x.get("name", "")).lower())
    save_products_to_file(initial_products)
    return initial_products

def save_products_to_file(prod_list):
    try:
        prod_list = sorted(prod_list, key=lambda x: str(x.get("name", "")).lower())
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(prod_list, f, ensure_ascii=False, indent=4)
    except:
        pass

def load_saved_populares():
    if os.path.exists(POPULAR_FILE):
        try:
            with open(POPULAR_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except:
            pass
    default_pops = [
        {"id": "p1", "name": "Pistaches Salados (90g)", "price": 35.0, "image": DEFAULT_PRODUCT_IMG},
        {"id": "p2", "name": "Fritura (Con Chile)", "price": 25.0, "image": DEFAULT_PRODUCT_IMG}
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

# 3. Colores y estilos (Forzando cuadrícula estricta de 2 columnas en móviles y web)
is_dark = st.session_state.dark_mode

bg_color = "#121824" if is_dark else "#ffffff"
text_color = "#f1f5f9" if is_dark else "#222222"
sub_text_color = "#94a3b8" if is_dark else "#4a5568"
card_bg = "#1e293b" if is_dark else "#ffffff"
border_color = "#334155" if is_dark else "#e2e8f0"
input_bg = "#ffffff" if not is_dark else "#1e293b"
input_text_color = "#222222" if not is_dark else "#f1f5f9"

BTN_GENERAL = "#FE8330"
BTN_GENERAL_HOVER = "#e06c20"
BTN_CART_FAB = "#FF4500"
BTN_CART_FAB_HOVER = "#d93800"

st.markdown(f"""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />

<style>
    div[data-baseweb="modal"] > div {{
        width: 95vw !important;
        max-width: 1400px !important;
    }}
    
    .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}

    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 6rem !important;
        background-color: transparent !important;
        animation: fadeIn 0.3s ease-in-out;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}

    body, html, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}

    div[data-testid="stVerticalBlock"], div[data-testid="stHorizontalBlock"], div.element-container {{
        background-color: transparent !important;
        color: {text_color} !important;
    }}

    /* FORZAR CUADRÍCULA ESTRICTA DE 2 COLUMNAS EN MÓVIL Y ESCRITORIO */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
    }}
    div[data-testid="column"] {{
        flex: 1 1 45% !important;
        min-width: 140px !important;
        max-width: 48% !important;
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

    /* FAB FLOTANTE EN LADO IZQUIERDO */
    div[data-testid="stButton"]:has(button[kind="primary"]) {{
        position: fixed !important;
        bottom: 24px !important;
        left: 24px !important;
        right: auto !important;
        z-index: 99999999 !important;
        width: auto !important;
    }}
    div[data-testid="stButton"]:has(button[kind="primary"]) > button {{
        background: linear-gradient(135deg, {BTN_CART_FAB} 0%, #ff6a33) !important;
        color: #ffffff !important;
        padding: 14px 28px !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 8px 25px rgba(255, 69, 0, 0.6) !important;
        border: none !important;
        min-height: 56px !important;
    }}
    div[data-testid="stButton"]:has(button[kind="primary"]) > button:hover {{
        transform: scale(1.06) !important;
        background: linear-gradient(135deg, {BTN_CART_FAB_HOVER} 0%, {BTN_CART_FAB} 100%) !important;
    }}

    /* BOTÓN DE CARRITO EN ENCABEZADO */
    div[data-testid="column"]:has(button[key*="header_cart_btn"]) button,
    button[key="header_cart_btn"] {{
        background-color: {BTN_CART_FAB} !important;
    }}
    button[key="header_cart_btn"]:hover {{
        background-color: {BTN_CART_FAB_HOVER} !important;
    }}

    .whatsapp-btn-disabled {{
        background-color: {"#334155" if is_dark else "#cbd5e1"} !important;
        color: {"#94a3b8" if is_dark else "#475569"} !important;
        padding: 14px;
        border-radius: 14px;
        text-align: center;
        font-weight: 700;
        font-size: 0.95rem;
        margin-top: 10px;
        display: block;
        width: 100%;
    }}

    .whatsapp-btn-active {{
        background: linear-gradient(135deg, #25D366 0%, #1EBE5D 100%) !important;
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
        box-shadow: 0 4px 15px rgba(37, 211, 102, 0.4);
    }}
    .whatsapp-btn-active:hover {{
        transform: scale(1.02);
        color: #ffffff !important;
    }}

    label p, .stTextInput label, .stTextArea label, [data-testid="stWidgetLabel"] p {{
        color: {text_color} !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }}

    /* BOTONES GENERALES */
    button, .stButton > button, div[data-testid="stButton"] > button {{
        background-color: {BTN_GENERAL} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(254, 131, 48, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
    }}
    button:hover, .stButton > button:hover {{
        background-color: {BTN_GENERAL_HOVER} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(254, 131, 48, 0.35) !important;
        color: #ffffff !important;
    }}
    button p, .stButton > button p, button span {{
        color: #ffffff !important;
    }}

    .qty-number {{
        font-size: 1.2rem !important;
        font-weight: 900 !important;
        text-align: center;
        color: {text_color} !important;
        margin-top: 6px;
    }}

    /* BARRA DE BÚSQUEDA */
    div[data-baseweb="input"], [data-baseweb="input"] {{
        background-color: {input_bg} !important;
        color: {input_text_color} !important;
        border: 3px solid {BTN_GENERAL} !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 12px rgba(254, 131, 48, 0.25) !important;
    }}
    div[data-baseweb="input"]:focus-within, [data-baseweb="input"]:focus-within {{
        border-color: {BTN_GENERAL_HOVER} !important;
        box-shadow: 0 0 0 4px rgba(254, 131, 48, 0.4) !important;
    }}
    input, textarea, select, div[data-baseweb="base-input"], div[data-baseweb="textarea"], div[data-baseweb="select"] {{
        background-color: transparent !important;
        color: {input_text_color} !important;
        -webkit-text-fill-color: {input_text_color} !important;
        border: none !important;
        box-shadow: none !important;
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
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        height: 100%;
    }}
    .product-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.07);
    }}
    .product-title {{
        font-size: 1.05rem;
        font-weight: 800;
        margin-bottom: 2px;
        color: {text_color} !important;
    }}
    .product-desc {{
        font-size: 0.8rem;
        color: {sub_text_color} !important;
        margin-bottom: 4px;
    }}
    .product-price {{
        font-size: 1.2rem !important;
        font-weight: 900 !important;
        color: {BTN_GENERAL} !important;
    }}

    .promo-banner {{
        background: linear-gradient(135deg, {BTN_GENERAL} 0%, {BTN_CART_FAB} 100%);
        color: white;
        padding: 14px 18px;
        border-radius: 16px;
        text-align: center;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(254, 131, 48, 0.2);
    }}
</style>
""", unsafe_allow_html=True)

def add_to_cart(product_id):
    st.session_state.cart[product_id] = st.session_state.cart.get(product_id, 0) + 1
    st.toast("Producto añadido al carrito", icon="🛒")

def remove_from_cart(product_id):
    if product_id in st.session_state.cart:
        if st.session_state.cart[product_id] > 1:
            st.session_state.cart[product_id] -= 1
        else:
            del st.session_state.cart[product_id]

def go_to_cart():
    st.session_state.nav_view = "carrito"
    st.rerun()

def go_to_catalogo():
    st.session_state.nav_view = "catalogo"
    st.rerun()

keys_to_delete = [pid for pid in st.session_state.cart if not any(p.get("id") == pid for p in st.session_state.products)]
for k in keys_to_delete:
    del st.session_state.cart[k]

total_items = sum(st.session_state.cart.values())

# ==========================================
# POP-UP DE VARIANTES / PRESENTACIONES
# ==========================================
@st.dialog("Seleccionar Variante o Presentación")
def variants_modal(base_name, variants_list):
    st.markdown(f"### {base_name}")
    st.caption("Elige la presentación, gramaje o variedad deseada:")
    
    for var in variants_list:
        v_id = var.get("id")
        v_name = var.get("name")
        v_price = float(var.get("price", 0))
        v_img = var.get("image", DEFAULT_PRODUCT_IMG)
        if not v_img or str(v_img).strip() == "" or str(v_img) == "nan" or "placeholder" in str(v_img) or "imgur" in str(v_img):
            v_img = DEFAULT_PRODUCT_IMG
            
        col_v1, col_v2, col_v3 = st.columns([1, 2.5, 1.5])
        with col_v1:
            st.image(v_img, width=60)
        with col_v2:
            st.markdown(f"**{v_name}**")
            st.markdown(f"<span style='color: {BTN_GENERAL}; font-weight: 900; font-size: 1.1rem;'>${v_price:.2f} MXN</span>", unsafe_allow_html=True)
        with col_v3:
            qty_val = st.session_state.cart.get(v_id, 0)
            if st.button(f"Agregar ({qty_val})", key=f"modal_add_{v_id}", use_container_width=True):
                add_to_cart(v_id)
                st.rerun()
        st.write("---")

# ==========================================
# 4. ENCABEZADO Y BÚSQUEDA
# ==========================================
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
    cart_btn_label = f"({total_items})" if total_items > 0 else ""
    if st.button(":material/shopping_cart: Carrito " + cart_btn_label, use_container_width=True, key="header_cart_btn"):
        if st.session_state.nav_view != "carrito":
            go_to_cart()
        else:
            go_to_catalogo()

st.write("")

# BÚSQUEDA MEXICANA
search_query = st.text_input("Buscar productos...", placeholder="Buscar semillas, cacahuates, pistaches...", label_visibility="collapsed")

st.write("---")

# ==========================================
# 5. VISTA DE CATÁLOGO O CARRITO
# ==========================================
if st.session_state.nav_view == "catalogo":
    st.markdown(
        f'<div class="promo-banner"><span class="material-symbols-outlined" style="vertical-align: -4px; margin-right: 6px;">local_shipping</span> ¡Envíos locales y entregas directas en ruta! Pide fácil y rápido</div>', 
        unsafe_allow_html=True
    )
    
    # BANNER PRINCIPAL
    banner_to_show = st.session_state.banner_url if st.session_state.banner_url else DEFAULT_BANNER
    st.markdown(f"""
    <div style="background: {card_bg}; border: 1px solid {border_color}; border-radius: 16px; padding: 12px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center;">
        <img src="{banner_to_show}" style="width: 100%; height: 260px; object-fit: cover; border-radius: 12px; display: block;" onerror="this.onerror=null;this.src='{DEFAULT_BANNER}';" />
    </div>
    """, unsafe_allow_html=True)

    # 1. PRODUCTOS POPULARES
    st.write("")
    st.markdown("### Productos Populares")
    st.caption("Toca cualquier producto popular para agregarlo directo a tu carrito:")

    popular_products = st.session_state.popular_items
    if not popular_products:
        popular_products = [
            {"id": "p1", "name": "Pistaches Salados (90g)", "price": 35.0, "image": DEFAULT_PRODUCT_IMG}
        ]

    pop_cols = st.columns(len(popular_products))
    for idx, pop_p in enumerate(popular_products):
        with pop_cols[idx]:
            p_img = pop_p.get('image', DEFAULT_PRODUCT_IMG)
            if not p_img or str(p_img).strip() == "" or str(p_img) == "nan" or "placeholder" in str(p_img) or "imgur" in str(p_img):
                p_img = DEFAULT_PRODUCT_IMG
            st.markdown(f"""
            <div style="background: {card_bg}; border: 1px solid {border_color}; border-radius: 12px; padding: 10px; text-align: center; margin-bottom: 10px;">
                <img src="{p_img}" style="width: 100%; height: 90px; object-fit: cover; border-radius: 8px;" />
                <div style="font-weight: 800; font-size: 0.9rem; margin-top: 6px; color: {text_color};">{pop_p.get('name', 'Producto')}</div>
                <div style="color: {BTN_GENERAL}; font-weight: 900; font-size: 1.05rem;">${float(pop_p.get('price', 0)):.2f} MXN</div>
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
                        "description": "",
                        "image": p_img
                    })
                    save_products_to_file(st.session_state.products)
                add_to_cart(prod_id)
                st.rerun()

    st.write("---")

    # 2. CATEGORÍAS
    st.markdown("### Categorías")
    category_options = ["Todo", "Individual", "Para compartir"]

    cat_cols = st.columns(len(category_options))
    for i, cat in enumerate(category_options):
        with cat_cols[i]:
            is_active = (st.session_state.selected_cat == cat)
            display_label = f"● {cat}" if is_active else cat
            
            if st.button(display_label, use_container_width=True, key=f"cat_btn_{cat}"):
                st.session_state.selected_cat = cat
                st.rerun()

    st.write("---")

    # 3. LISTADO DE PRODUCTOS AGRUPADOS Y ORDENADOS ALFABÉTICAMENTE
    try:
        current_products_list = sorted(st.session_state.products, key=lambda x: str(x.get("name", "")).lower())
        
        if st.session_state.selected_cat == "Todo":
            cat_filtered = current_products_list
        else:
            cat_filtered = [p for p in current_products_list if p.get("category", "Individual") == st.session_state.selected_cat]

        filtered_products = [
            p for p in cat_filtered 
            if isinstance(p, dict) and (search_query.lower() in str(p.get("name", "")).lower() or search_query.lower() in str(p.get("description", "")).lower())
        ]
    except:
        filtered_products = []

    if not filtered_products:
        st.info("No se encontraron productos en esta categoría.")
    else:
        grouped_dict = {}
        for p in filtered_products:
            name_raw = str(p.get("name", "Producto")).strip()
            
            if "(" in name_raw and ")" in name_raw:
                base_name = name_raw.split("(")[0].strip()
                if base_name not in grouped_dict:
                    grouped_dict[base_name] = []
                grouped_dict[base_name].append(p)
            else:
                if name_raw not in grouped_dict:
                    grouped_dict[name_raw] = []
                if not any(it.get("name") == name_raw for it in grouped_dict[name_raw]):
                    grouped_dict[name_raw].append(p)

        group_items_list = list(grouped_dict.items())
        
        # RENDERIZADO EN CUADRÍCULA ESTRICTA DE 2 COLUMNAS
        for i in range(0, len(group_items_list), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(group_items_list):
                    base_name, items_group = group_items_list[i + j]
                    representative = items_group[0]
                    pid = representative.get("id")
                    
                    with cols[j]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        
                        col_img, col_info = st.columns([1, 2])
                        with col_img:
                            img_src = representative.get("image")
                            if not img_src or str(img_src).strip() == "" or str(img_src) == "nan" or "placeholder" in str(img_src) or "imgur" in str(img_src):
                                img_src = DEFAULT_PRODUCT_IMG
                            st.image(img_src, use_container_width=True)
                            
                        with col_info:
                            st.markdown(f'<div class="product-title">{base_name}</div>', unsafe_allow_html=True)
                            
                            desc_text = str(representative.get("description", "")).strip()
                            if desc_text and desc_text.lower() != "nan":
                                st.markdown(f'<div class="product-desc">{desc_text}</div>', unsafe_allow_html=True)
                            
                            if len(items_group) > 1:
                                prices = [float(it.get("price", 0)) for it in items_group]
                                st.markdown(f'<div class="product-price">Desde ${min(prices):.2f}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="product-price">${float(representative.get("price", 0)):.2f} MXN</div>', unsafe_allow_html=True)
                        
                        st.write("")
                        if len(items_group) > 1:
                            # BOTÓN DE OPCIONES CON TEXTO PLANO (SIN HTML COMPLEJO)
                            if st.button("Ver Opciones", key=f"variants_btn_{base_name}_{pid}", use_container_width=True):
                                variants_modal(base_name, items_group)
                        else:
                            qty_in_cart = st.session_state.cart.get(pid, 0)
                            if qty_in_cart == 0:
                                if st.button("Agregar al Carrito", key=f"add_{pid}", use_container_width=True):
                                    add_to_cart(pid)
                                    st.rerun()
                            else:
                                sub_c1, sub_c2, sub_c3 = st.columns([1, 1.2, 1])
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

    if total_items > 0:
        st.button(
            ":material/shopping_cart: Ver Carrito (" + str(total_items) + ")",
            type="primary",
            on_click=go_to_cart,
            key="native_floating_fab"
        )

elif st.session_state.nav_view == "carrito":
    st.markdown('<div id="top-cart-anchor"></div>', unsafe_allow_html=True)
    
    if st.button(":material/arrow_back: Volver al Catálogo", use_container_width=False, key="back_to_cat_btn"):
        go_to_catalogo()
        
    st.markdown("### :material/shopping_cart: Carrito de Compras y Pedido")
    st.caption(f"Artículos seleccionados: {total_items}")
    
    if not st.session_state.cart:
        st.info("Tu carrito está vacío. Agrega productos desde el catálogo.")
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
        
        order_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        msg_header = f"NUEVO PEDIDO\nFecha: {order_date}\n\n"
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
                f'''<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn-active">
                    <span class="material-symbols-outlined" style="vertical-align: -5px; margin-right: 6px; font-size: 24px;">chat</span>
                    Enviar pedido por WhatsApp
                </a>''',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="whatsapp-btn-disabled">Completa Nombre y Dirección para activar el botón de envío</div>',
                unsafe_allow_html=True
            )

# ==========================================
# 7. PIE DE PÁGINA Y PANEL DE ADMIN
# ==========================================
st.write("---")
st.markdown("<br><br>", unsafe_allow_html=True)

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
        
        tab_prod, tab_pop, tab_banner, tab_upload = st.tabs(["📦 Editar Productos", "⭐ Populares", "🖼️ Imagen Banner", "📤 Subir Imágenes"])
        
        with tab_prod:
            st.markdown("### Inventario de Productos")
            st.info("💡 Para agrupar variantes (ej. Frituras con/sin chile), pon el mismo nombre base seguido de la variante entre paréntesis. Los productos se ordenan alfabéticamente en automático.")
            
            uploaded_excel = st.file_uploader("Cargar catálogo desde Excel o CSV (.xlsx, .csv)", type=["xlsx", "csv"])
            if uploaded_excel is not None:
                try:
                    if uploaded_excel.name.endswith(".csv"):
                        df_uploaded = pd.read_csv(uploaded_excel)
                    else:
                        df_uploaded = pd.read_excel(uploaded_excel)
                    
                    if "name" in df_uploaded.columns and "price" in df_uploaded.columns:
                        new_loaded_list = []
                        for idx, row in df_uploaded.iterrows():
                            r_id = str(row.get("id", f"excel_{idx}"))
                            r_desc = row.get("description", "")
                            r_img = row.get("image", DEFAULT_PRODUCT_IMG)
                            
                            desc_val = str(r_desc).strip() if pd.notna(r_desc) and str(r_desc).strip() != "nan" else ""
                            img_val = str(r_img).strip() if pd.notna(r_img) and str(r_img).strip() != "nan" and str(r_img).strip() != "" and "placeholder" not in str(r_img) and "imgur" not in str(r_img) else DEFAULT_PRODUCT_IMG
                            
                            new_loaded_list.append({
                                "id": r_id if r_id.strip() != "" and r_id != "nan" else f"excel_{idx}",
                                "name": str(row.get("name", "Producto")),
                                "category": str(row.get("category", "Individual")),
                                "price": float(row.get("price", 0.0)),
                                "description": desc_val,
                                "image": img_val
                            })
                        new_loaded_list = sorted(new_loaded_list, key=lambda x: str(x.get("name", "")).lower())
                        st.session_state.products = new_loaded_list
                        save_products_to_file(new_loaded_list)
                        st.success("¡Catálogo cargado y ordenado alfabéticamente desde el archivo!")
                        st.rerun()
                    else:
                        st.error("El archivo debe contener al menos las columnas 'name' y 'price'.")
                except Exception as e:
                    st.error(f"Error al procesar el archivo: {e}")

            st.write("---")
            
            current_sorted_products = sorted(st.session_state.products, key=lambda x: str(x.get("name", "")).lower())
            df_current = pd.DataFrame(current_sorted_products)
            
            column_config = {
                "id": None,
                "category": st.column_config.SelectboxColumn(
                    "Categoría",
                    options=["Individual", "Para compartir"],
                    required=True
                )
            }
            
            edited_df = st.data_editor(
                df_current, 
                num_rows="dynamic", 
                key="editor_admin_table",
                column_config=column_config,
                hide_index=True,
                use_container_width=True
            )
            
            if st.button("Guardar Cambios de Productos"):
                updated_list = []
                for idx, row in edited_df.iterrows():
                    raw_id = row.get("id")
                    prod_id = str(raw_id).strip() if pd.notna(raw_id) and str(raw_id).strip() != "" else f"prod_{int(datetime.now().timestamp())}_{idx}"
                    
                    raw_img = row.get("image")
                    prod_img = str(raw_img).strip() if pd.notna(raw_img) and str(raw_img).strip() != "" and str(raw_img).strip() != "nan" and "placeholder" not in str(raw_img) and "imgur" not in str(raw_img) else DEFAULT_PRODUCT_IMG
                    
                    raw_desc = row.get("description")
                    prod_desc = str(raw_desc).strip() if pd.notna(raw_desc) and str(raw_desc).strip() != "nan" else ""
                    
                    updated_list.append({
                        "id": prod_id,
                        "name": str(row.get("name", "Nuevo producto")),
                        "category": str(row.get("category", "Individual")),
                        "price": float(row.get("price", 0.0)),
                        "description": prod_desc,
                        "image": prod_img
                    })
                    
                updated_list = sorted(updated_list, key=lambda x: str(x.get("name", "")).lower())
                st.session_state.products = updated_list
                save_products_to_file(updated_list)
                st.success("¡Productos guardados y ordenados alfabéticamente!")
                st.rerun()

        with tab_pop:
            st.markdown("### Seleccionar Productos Populares")
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
                        "image": prod.get("image", DEFAULT_PRODUCT_IMG)
                    })
            
            if st.button("Guardar Productos Populares"):
                if selected_populares_new:
                    st.session_state.popular_items = selected_populares_new
                    save_populares_to_file(selected_populares_new)
                    st.success("¡Populares actualizados!")
                    st.rerun()
                else:
                    st.warning("Selecciona al menos uno.")

        with tab_banner:
            st.markdown("### Cambiar Imagen Rectangular del Banner")
            st.caption("Tamaño recomendado: 1200 x 500 px. Actualiza el enlace de la imagen principal:")
            new_banner_url = st.text_input("URL de la imagen del banner", value=st.session_state.banner_url)
            if st.button("Guardar Banner"):
                if new_banner_url.strip():
                    st.session_state.banner_url = new_banner_url.strip()
                    save_banner_to_file(new_banner_url.strip())
                    st.success("¡Banner actualizado con éxito!")
                    st.rerun()

        with tab_upload:
            st.markdown("### Subir Imagen Directamente")
            st.caption("Tamaño recomendado: Artículos (600x600 px)")
            uploaded_file = st.file_uploader("Elige una imagen", type=["png", "jpg", "jpeg", "webp"])
            if uploaded_file is not None:
                file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"¡Subida con éxito: `{uploaded_file.name}`!")
                st.image(file_path, width=200)
                local_url = f"/{UPLOAD_DIR}/{uploaded_file.name}"
                st.text_input("Copia esta ruta para usarla en tu banner o productos:", value=local_url)
        
        st.write("---")
        if st.button("Cerrar Sesión"):
            st.session_state.admin_authenticated = False
            st.rerun()

col_foot1, col_foot_admin, col_foot2 = st.columns(3)
with col_foot_admin:
    if st.button(":material/settings: Admin", use_container_width=True, key="admin_footer_btn"):
        admin_modal()