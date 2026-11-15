import streamlit as st
import pandas as pd
import urllib.parse
import json
import os
from datetime import datetime

LOGO_URL = "https://raw.githubusercontent.com/Mostacho100/Mostacho-Botanas-Web/main/logo.png"
DATA_FILE = "productos_mostacho.json"
POPULAR_FILE = "populares_mostacho.json"
BANNER_FILE = "banner_mostacho.json"
CONFIG_FILE = "config_mostacho.json"
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

if "show_variants_modal" not in st.session_state:
    st.session_state.show_variants_modal = False

if "current_modal_base" not in st.session_state:
    st.session_state.current_modal_base = ""

if "current_modal_items" not in st.session_state:
    st.session_state.current_modal_items = []

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if "saved_customer_name" not in st.session_state:
    st.session_state.saved_customer_name = ""
if "saved_customer_address" not in st.session_state:
    st.session_state.saved_customer_address = ""
if "saved_customer_gps" not in st.session_state:
    st.session_state.saved_customer_gps = ""

WHATSAPP_PHONE = "522381174698"

# ==========================================
# LIGAS Y ARCHIVOS DE CONFIGURACIÓN
# ==========================================
DEFAULT_BANNER = "https://raw.githubusercontent.com/Mostacho100/Mostacho-Botanas-Web/main/banner.jpg"
DEFAULT_PRODUCT_IMG = "https://raw.githubusercontent.com/Mostacho100/Mostacho-Botanas-Web/main/image.jpg"

def load_config():
    default_cfg = {"store_open": True}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except:
            pass
    return default_cfg

def save_config(cfg_dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg_dict, f, ensure_ascii=False, indent=4)
    except:
        pass

if "store_config" not in st.session_state:
    st.session_state.store_config = load_config()

def load_saved_banner():
    if os.path.exists(BANNER_FILE):
        try:
            with open(BANNER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    url = str(data.get("url", "")).strip()
                    if url and url.lower() != "nan":
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
                            
                            if not img_val or img_val == "" or img_val.lower() == "nan" or "placeholder" in img_val:
                                item["image"] = DEFAULT_PRODUCT_IMG
                            else:
                                item["image"] = img_val
                                
                            cleaned.append(item)
                    if cleaned:
                        cleaned = sorted(cleaned, key=lambda x: str(x.get("name", "")).lower())
                        return cleaned
        except:
            pass
            
    initial_products = [
        {"id": "p1", "name": "Pistaches Salados (90g)", "category": "Individual", "price": 35.0, "description": "Pistaches tostados con sal de mar.", "image": DEFAULT_PRODUCT_IMG, "bestseller": True},
        {"id": "p2", "name": "Fritura (Con Chile)", "category": "Para compartir", "price": 25.0, "description": "Crujientes frituras artesanales.", "image": DEFAULT_PRODUCT_IMG, "bestseller": True},
        {"id": "p3", "name": "Fritura (Sin Chile)", "category": "Para compartir", "price": 25.0, "description": "Ideales para toda la familia.", "image": DEFAULT_PRODUCT_IMG, "bestseller": False}
    ]
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
                if isinstance(data, list) and len(data) > 0:
                    cleaned_pops = []
                    for p in data:
                        if isinstance(p, dict):
                            p_img = str(p.get("image", "")).strip()
                            if not p_img or p_img.lower() == "nan" or "placeholder" in p_img:
                                p["image"] = DEFAULT_PRODUCT_IMG
                            cleaned_pops.append(p)
                    if cleaned_pops:
                        return cleaned_pops
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

# PALETA DE DISEÑO REDISEÑADA Y FORZADA (BLANCO Y NARANJA)
bg_color = "#f4f6f9"
text_color = "#0f172a"
sub_text_color = "#64748b"
card_bg = "#ffffff"
border_color = "#e2e8f0"

BTN_GENERAL = "#FE8330"
BTN_GENERAL_HOVER = "#e06c20"
BTN_CART_FAB = "#FF4500"        
BTN_CART_FAB_HOVER = "#d93800"

st.markdown(f"""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet">

<style>
    /* ELIMINAR BARRAS NEGRAS, MENÚS Y FOOTERS DE STREAMLIT */
    #MainMenu {{visibility: hidden !important; display: none !important;}}
    footer {{visibility: hidden !important; display: none !important;}}
    header {{visibility: hidden !important; display: none !important;}}
    .stDeployButton {{display: none !important;}}
    [data-testid="stHeader"] {{background-color: transparent !important; display: none !important;}}

    :root {{
        color-scheme: light !important;
    }}

    html, body, [class*="st"] {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}

    div[data-baseweb="modal"] button[aria-label="Close"] {{
        display: none !important;
    }}
    div[data-baseweb="modal"] {{
        background-color: rgba(15, 23, 42, 0.65) !important;
        backdrop-filter: blur(6px);
    }}
    div[data-baseweb="modal"] > div {{
        background-color: #ffffff !important;
        color: #0f172a !important;
        width: 92vw !important;
        max-width: 550px !important;
        border-radius: 28px !important;
        padding: 24px !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }}
    div[data-baseweb="modal"] * {{
        color: #0f172a !important;
    }}
    div[data-baseweb="modal"] div[data-testid="stVerticalBlock"] {{
        max-height: 55vh !important;
        overflow-y: scroll !important;
        padding-right: 6px !important;
        background-color: #ffffff !important;
    }}

    .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}

    .block-container {{
        padding-top: 1.2rem !important;
        padding-bottom: 7.5rem !important;
        max-width: 100% !important;
    }}

    div[data-testid="stVerticalBlock"], div[data-testid="stHorizontalBlock"], div.element-container {{
        background-color: transparent !important;
        color: {text_color} !important;
    }}

    /* CAMPOS DE TEXTO E INPUTS ULTRA MODERNOS Y BLANCOS */
    input, textarea, select, 
    div[data-baseweb="input"], div[data-baseweb="base-input"], 
    div[data-baseweb="textarea"], div[data-baseweb="select"],
    [data-baseweb="input"] > div, [data-baseweb="base-input"] > div {{
        background-color: #ffffff !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        border-color: #cbd5e1 !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.01);
    }}

    input::placeholder, textarea::placeholder {{
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
    }}

    /* ENCABEZADO SUPERIOR ELEGANTE */
    .sticky-header {{
        position: sticky;
        top: 0;
        z-index: 99999;
        background-color: rgba(244, 246, 249, 0.95);
        padding: 12px 0 14px 0;
        border-bottom: 1px solid {border_color};
        margin-bottom: 18px;
        backdrop-filter: blur(12px);
    }}

    .app-title {{
        font-size: 1.7rem !important;
        font-weight: 900 !important;
        color: {text_color} !important;
        margin: 0 !important;
        line-height: 1.1 !important;
        letter-spacing: -0.8px;
    }}
    .app-subtitle {{
        font-size: 0.75rem !important;
        color: {sub_text_color} !important;
        font-weight: 700 !important;
        margin-top: 3px !important;
        display: block;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* BOTÓN FLOTANTE CARRITO (FAB PREMIUM) */
    div[data-testid="stButton"]:has(button[kind="primary"]) {{
        position: fixed !important;
        bottom: 82px !important;
        left: 20px !important;
        right: auto !important;
        z-index: 999998 !important;
        width: auto !important;
    }}
    div[data-testid="stButton"]:has(button[kind="primary"]) > button {{
        background: linear-gradient(135deg, {BTN_CART_FAB} 0%, #ff6a33) !important;
        color: #ffffff !important;
        padding: 12px 26px !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        box-shadow: 0 12px 30px rgba(255, 69, 0, 0.45) !important;
        border: none !important;
        min-height: 50px !important;
        letter-spacing: -0.3px;
    }}
    div[data-testid="stButton"]:has(button[kind="primary"]) > button:hover {{
        transform: scale(1.06) !important;
        background: linear-gradient(135deg, {BTN_CART_FAB_HOVER} 0%, {BTN_CART_FAB} 100%) !important;
    }}

    .whatsapp-btn-disabled {{
        background-color: #e2e8f0 !important;
        color: #64748b !important;
        padding: 15px;
        border-radius: 16px;
        text-align: center;
        font-weight: 700;
        font-size: 0.9rem;
        margin-top: 12px;
        display: block;
        width: 100%;
    }}

    .whatsapp-btn-active {{
        background: linear-gradient(135deg, #25D366 0%, #1EBE5D 100%) !important;
        color: #ffffff !important;
        padding: 16px;
        border-radius: 16px;
        text-align: center;
        font-weight: 800;
        font-size: 1.05rem;
        margin-top: 12px;
        display: block;
        width: 100%;
        text-decoration: none;
        box-shadow: 0 8px 20px rgba(37, 211, 102, 0.4);
    }}
    .whatsapp-btn-active:hover {{
        transform: scale(1.02);
        color: #ffffff !important;
    }}

    label p, .stTextInput label, .stTextArea label, [data-testid="stWidgetLabel"] p {{
        color: {text_color} !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
    }}

    /* BOTONES GENERALES ESTILO APP */
    button, .stButton > button, div[data-testid="stButton"] > button {{
        background-color: {BTN_GENERAL} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(254, 131, 48, 0.25) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    button:hover, .stButton > button:hover {{
        background-color: {BTN_GENERAL_HOVER} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(254, 131, 48, 0.35) !important;
        color: #ffffff !important;
    }}
    button p, .stButton > button p, button span {{
        color: #ffffff !important;
    }}

    .qty-number {{
        font-size: 1.15rem !important;
        font-weight: 900 !important;
        text-align: center;
        color: #0f172a !important;
        margin-top: 6px;
    }}

    .material-symbols-outlined {{
        font-family: 'Material Symbols Outlined' !important;
        font-size: 22px !important;
        vertical-align: middle;
        line-height: 1;
    }}

    /* TARJETAS DE PRODUCTO TIPO GOURMET/DELIVERY */
    .product-card {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 20px;
        padding: 14px;
        margin-bottom: 16px;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.04), 0 8px 10px -6px rgba(0,0,0,0.02);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        position: relative;
        transition: all 0.25s ease;
    }}
    .product-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 20px 30px -10px rgba(0,0,0,0.08);
        border-color: #cbd5e1;
    }}
    .product-title {{
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 4px;
        color: #0f172a !important;
        letter-spacing: -0.3px;
    }}
    .product-desc {{
        font-size: 0.78rem;
        color: #64748b !important;
        margin-bottom: 8px;
        line-height: 1.35;
    }}
    .product-price {{
        font-size: 1.15rem !important;
        font-weight: 900 !important;
        color: {BTN_GENERAL} !important;
        letter-spacing: -0.5px;
    }}
    .bestseller-badge {{
        position: absolute;
        top: 12px;
        right: 12px;
        background: linear-gradient(135deg, #FF4500 0%, #ff6a33);
        color: white;
        font-size: 0.65rem;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 20px;
        box-shadow: 0 4px 10px rgba(255,69,0,0.35);
        z-index: 10;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}

    .promo-banner {{
        background: linear-gradient(135deg, {BTN_GENERAL} 0%, {BTN_CART_FAB} 100%);
        color: white;
        padding: 14px 18px;
        border-radius: 18px;
        text-align: center;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 16px;
        box-shadow: 0 8px 20px rgba(254, 131, 48, 0.25);
    }}

    .store-closed-banner {{
        background: linear-gradient(135deg, #ef4444 0%, #dc2626);
        color: white;
        padding: 16px;
        border-radius: 18px;
        text-align: center;
        font-weight: 800;
        font-size: 1rem;
        margin-bottom: 20px;
        box-shadow: 0 8px 20px rgba(239, 68, 68, 0.3);
    }}

    @media (min-width: 768px) {{
        .desktop-banner-img {{
            height: 240px !important;
        }}
    }}
    @media (max-width: 767px) {{
        .desktop-banner-img {{
            height: 160px !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)

def add_to_cart(product_id):
    st.session_state.cart[product_id] = st.session_state.cart.get(product_id, 0) + 1

def remove_from_cart(product_id):
    if product_id in st.session_state.cart:
        if st.session_state.cart[product_id] > 1:
            st.session_state.cart[product_id] -= 1
        else:
            del st.session_state.cart[product_id]

keys_to_delete = [pid for pid in st.session_state.cart if not any(p.get("id") == pid for p in st.session_state.products)]
for k in keys_to_delete:
    del st.session_state.cart[k]

total_items = sum(st.session_state.cart.values())

# ==========================================
# MODAL DE VARIANTES
# ==========================================
@st.dialog("Seleccionar Variante o Presentación")
def variants_modal_dialog(base_name, variants_list):
    st.markdown(f"<h3 style='color: #0f172a !important; margin-bottom: 4px; font-weight: 800;'>{base_name}</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b !important; font-size: 0.9rem; font-weight: 600;'>Escoge la figura y el sabor que deseas:</p>", unsafe_allow_html=True)
    st.write("---")
    
    for idx, var in enumerate(variants_list):
        v_id = str(var.get("id"))
        v_name = var.get("name")
        v_price = float(var.get("price", 0))
        
        v_img = str(var.get("image", "")).strip()
        if not v_img or v_img.lower() == "nan" or "placeholder" in v_img:
            v_img = DEFAULT_PRODUCT_IMG
            
        col_v1, col_v2, col_v3 = st.columns([1, 2.2, 1.8])
        with col_v1:
            st.image(v_img, width=48)
        with col_v2:
            st.markdown(f"<span style='color: #0f172a !important; font-weight: 800; font-size: 0.95rem;'>{v_name}</span>", unsafe_allow_html=True)
            st.markdown(f"<span style='color: {BTN_GENERAL}; font-weight: 900; font-size: 1rem;'>${v_price:.2f} MXN</span>", unsafe_allow_html=True)
        with col_v3:
            qty_val = st.session_state.cart.get(v_id, 0)
            sub_cv1, sub_cv2, sub_cv3 = st.columns([1, 1, 1])
            with sub_cv1:
                if st.button("-", key=f"m_minus_{v_id}_{idx}", use_container_width=True):
                    remove_from_cart(v_id)
                    st.rerun()
            with sub_cv2:
                st.markdown(f"<div class='qty-number' style='color: #0f172a !important;'>{qty_val}</div>", unsafe_allow_html=True)
            with sub_cv3:
                if st.button("+", key=f"m_plus_{v_id}_{idx}", use_container_width=True):
                    add_to_cart(v_id)
                    st.rerun()
        st.markdown("<hr style='margin: 10px 0; border-color: #f1f5f9;'>", unsafe_allow_html=True)
    
    st.write("")
    if st.button(":material/check_circle: Listo", type="primary", use_container_width=True, key="close_modal_btn"):
        st.session_state.show_variants_modal = False
        st.rerun()

if st.session_state.show_variants_modal:
    variants_modal_dialog(st.session_state.current_modal_base, st.session_state.current_modal_items)

# ==========================================
# HEADER ESTÁTICO SUPERIOR
# ==========================================
st.markdown(f"""
<div class="sticky-header">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <img src="{LOGO_URL}" style="width: 48px; height: 48px; object-fit: contain; background: transparent;" onerror="this.style.display='none'" />
            <div>
                <h1 class="app-title">Mostacho Botanas</h1>
                <span class="app-subtitle">Catálogo y pedidos en línea</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# NAVBAR INFERIOR TIPO APLICACIÓN (3 BOTONES)
# ==========================================
col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    if st.button(":material/home: Inicio", use_container_width=True, key="nav_btn_home"):
        st.session_state.nav_view = "catalogo"
        st.rerun()

with col_nav2:
    cart_label = f":material/shopping_cart: Carrito ({total_items})" if total_items > 0 else ":material/shopping_cart: Carrito"
    if st.button(cart_label, use_container_width=True, key="nav_btn_cart"):
        st.session_state.nav_view = "carrito"
        st.rerun()

with col_nav3:
    if st.button(":material/settings: Config", use_container_width=True, key="nav_btn_admin"):
        st.session_state.nav_view = "admin"
        st.rerun()

st.write("")

store_is_open = st.session_state.store_config.get("store_open", True)

# ==========================================
# VISTAS PRINCIPALES
# ==========================================
if st.session_state.nav_view == "catalogo":
    if not store_is_open:
        st.markdown(
            '<div class="store-closed-banner">🔒 ¡Por el momento estamos cerrados! Puedes ver el catálogo pero los pedidos abrirán en nuestro próximo horario.</div>',
            unsafe_allow_html=True
        )

    search_query = st.text_input("Buscar productos...", placeholder="Buscar semillas, cacahuates, pistaches...", label_visibility="collapsed")
    st.write("---")
    
    st.markdown(
        f'<div class="promo-banner"><span class="material-symbols-outlined" style="vertical-align: -4px; margin-right: 6px;">local_shipping</span> ¡Envíos locales y entregas directas en ruta! Pide fácil y rápido</div>', 
        unsafe_allow_html=True
    )
    
    banner_to_show = str(st.session_state.banner_url).strip()
    if not banner_to_show or banner_to_show.lower() == "nan":
        banner_to_show = DEFAULT_BANNER

    st.markdown(f"""
    <div style="background: {card_bg}; border: 1px solid {border_color}; border-radius: 22px; padding: 8px; margin-bottom: 18px; box-shadow: 0 10px 25px rgba(0,0,0,0.04); text-align: center;">
        <img src="{banner_to_show}" class="desktop-banner-img" style="width: 100%; object-fit: cover; border-radius: 16px; display: block;" onerror="this.onerror=null;this.src='{DEFAULT_BANNER}';" />
    </div>
    """, unsafe_allow_html=True)

    # 1. PRODUCTOS POPULARES
    st.write("")
    st.markdown("### 🔥 Favoritos del Momento")
    st.caption("Toca cualquier producto popular para agregarlo directo a tu carrito:")

    popular_products = st.session_state.popular_items
    if not popular_products:
        popular_products = [
            {"id": "p1", "name": "Pistaches Salados (90g)", "price": 35.0, "image": DEFAULT_PRODUCT_IMG}
        ]

    pop_cols = st.columns(len(popular_products))
    for idx, pop_p in enumerate(popular_products):
        with pop_cols[idx]:
            p_id = str(pop_p.get("id", ""))
            p_name = str(pop_p.get("name", "")).lower().strip()
            
            matched_prod = next((p for p in st.session_state.products if str(p.get("id", "")) == p_id or str(p.get("name", "")).lower().strip() == p_name), None)
            
            if matched_prod and matched_prod.get("image"):
                cand_img = str(matched_prod.get("image")).strip()
                if cand_img != "" and cand_img.lower() != "nan" and "placeholder" not in cand_img:
                    p_img = cand_img
                else:
                    p_img = DEFAULT_PRODUCT_IMG
            else:
                cand_pop = str(pop_p.get("image", "")).strip()
                if cand_pop != "" and cand_pop.lower() != "nan" and "placeholder" not in cand_pop:
                    p_img = cand_pop
                else:
                    p_img = DEFAULT_PRODUCT_IMG

            st.markdown(f"""
            <div style="background: {card_bg}; border: 1px solid {border_color}; border-radius: 18px; padding: 12px; text-align: center; margin-bottom: 12px; box-shadow: 0 6px 15px rgba(0,0,0,0.03);">
                <img src="{p_img}" style="width: 100%; height: 100px; object-fit: cover; border-radius: 12px;" onerror="this.onerror=null;this.src='{DEFAULT_PRODUCT_IMG}';" />
                <div style="font-weight: 800; font-size: 0.88rem; margin-top: 8px; color: #0f172a;">{pop_p.get('name', 'Producto')}</div>
                <div style="color: {BTN_GENERAL}; font-weight: 900; font-size: 1.05rem; margin-top: 2px;">${float(pop_p.get('price', 0)):.2f} MXN</div>
            </div>
            """, unsafe_allow_html=True)

            if store_is_open:
                if st.button("Agregar +", key=f"quick_add_{p_id}_{idx}", use_container_width=True):
                    prod_id = p_id if p_id else str(idx)
                    if not any(str(p.get("id")) == prod_id for p in st.session_state.products):
                        st.session_state.products.append({
                            "id": prod_id,
                            "name": pop_p.get('name'),
                            "category": "Individual",
                            "price": pop_p.get('price'),
                            "description": "",
                            "image": p_img,
                            "bestseller": False
                        })
                        save_products_to_file(st.session_state.products)
                    add_to_cart(prod_id)
                    st.rerun()
            else:
                st.button("Cerrado", key=f"quick_add_closed_{idx}", disabled=True, use_container_width=True)

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

    # 3. LISTADO DE PRODUCTOS
    try:
        current_products_list = sorted(st.session_state.products, key=lambda x: str(x.get("name", "")).lower())
        
        if st.session_state.selected_cat == "Todo":
            cat_filtered = current_products_list
        else:
            cat_filtered = []
            for p in current_products_list:
                c_val = str(p.get("category", "Individual")).strip()
                if c_val == st.session_state.selected_cat:
                    cat_filtered.append(p)

        filtered_products = []
        for p in cat_filtered:
            if isinstance(p, dict):
                p_name = str(p.get("name", "")).lower()
                p_desc = str(p.get("description", "")).lower()
                if search_query.lower() in p_name or search_query.lower() in p_desc:
                    filtered_products.append(p)
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
                if not any(str(it.get("id")) == str(p.get("id")) for it in grouped_dict[base_name]):
                    grouped_dict[base_name].append(p)
            else:
                if name_raw not in grouped_dict:
                    grouped_dict[name_raw] = []
                if not any(str(it.get("id")) == str(p.get("id")) for it in grouped_dict[name_raw]):
                    grouped_dict[name_raw].append(p)

        group_items_list = list(grouped_dict.items())
        group_items_list = sorted(group_items_list, key=lambda x: 0 if len(x[1]) > 1 else 1)
        
        for i in range(0, len(group_items_list), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(group_items_list):
                    base_name, items_group = group_items_list[i + j]
                    representative = items_group[0]
                    pid = representative.get("id")
                    is_best = any(it.get("bestseller", False) for it in items_group)
                    
                    with cols[j]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        
                        if is_best:
                            st.markdown('<div class="bestseller-badge">🔥 Más Vendido</div>', unsafe_allow_html=True)
                        
                        img_src = str(representative.get("image", "")).strip()
                        if not img_src or img_src.lower() == "nan" or "placeholder" in img_src:
                            img_src = DEFAULT_PRODUCT_IMG
                        
                        try:
                            st.image(img_src, use_container_width=True)
                        except:
                            st.image(DEFAULT_PRODUCT_IMG, use_container_width=True)
                        
                        st.markdown(f'<div class="product-title" style="margin-top: 10px;">{base_name}</div>', unsafe_allow_html=True)
                        desc_text = str(representative.get("description", "")).strip()
                        if desc_text and desc_text.lower() != "nan":
                            st.markdown(f'<div class="product-desc">{desc_text}</div>', unsafe_allow_html=True)
                        
                        prices = [float(it.get("price", 0)) for it in items_group]
                        st.markdown(f'<div class="product-price">${prices[0]:.2f} MXN</div>', unsafe_allow_html=True)
                        
                        st.write("")
                        if len(items_group) > 1:
                            if store_is_open:
                                if st.button("Ver Opciones", key=f"variants_btn_{base_name}_{pid}", use_container_width=True):
                                    st.session_state.current_modal_base = base_name
                                    st.session_state.current_modal_items = items_group
                                    st.session_state.show_variants_modal = True
                                    st.rerun()
                            else:
                                st.button("Cerrado", key=f"var_closed_{pid}", disabled=True, use_container_width=True)
                        else:
                            qty_in_cart = st.session_state.cart.get(pid, 0)
                            if not store_is_open:
                                st.button("Cerrado", key=f"single_closed_{pid}", disabled=True, use_container_width=True)
                            else:
                                if qty_in_cart == 0:
                                    if st.button("Agregar", key=f"add_{pid}", use_container_width=True):
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
        if st.button(":material/shopping_cart: Ver Carrito (" + str(total_items) + ")", type="primary", key="native_floating_fab"):
            st.session_state.nav_view = "carrito"
            st.rerun()

elif st.session_state.nav_view == "carrito":
    st.markdown("### :material/shopping_cart: Carrito de Compras y Pedido")
    st.caption(f"Artículos seleccionados: {total_items}")
    
    if not st.session_state.cart:
        st.info("Tu carrito está vacío. Regresa al inicio para agregar productos.")
        if st.button("Ir al Catálogo"):
            st.session_state.nav_view = "catalogo"
            st.rerun()
    else:
        total_price = 0.0
        order_summary = []
        
        st.write("---")
        for item_id, qty in list(st.session_state.cart.items()):
            p = next((item for item in st.session_state.products if str(item.get("id")) == str(item_id)), None)
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

        # SUGERENCIA CRUZADA INTELIGENTE (CROSS-SELLING)
        cart_product_names = [str(p.get("name", "")).lower() for item_id, q in st.session_state.cart.items() for p in st.session_state.products if str(p.get("id")) == str(item_id)]
        has_pistaches = any("pistache" in name for name in cart_product_names)
        has_fritura = any("fritura" in name for name in cart_product_names)

        if not has_pistaches:
            suggested_item = next((p for p in st.session_state.products if "pistache" in str(p.get("name", "")).lower()), None)
            if suggested_item:
                st.info(f"💡 **¿Se te antoja algo más?** Agrega unos **{suggested_item.get('name')}** (${suggested_item.get('price')} MXN) para complementar tu botana.")
                if st.button("Agregar Pistaches al Carrito", key="sugg_add_pist"):
                    add_to_cart(str(suggested_item.get("id")))
                    st.rerun()
        elif not has_fritura:
            suggested_item = next((p for p in st.session_state.products if "fritura" in str(p.get("name", "")).lower()), None)
            if suggested_item:
                st.info(f"💡 **¿Se te antoja algo más?** Complementa con unas **{suggested_item.get('name')}** (${suggested_item.get('price')} MXN).")
                if st.button("Agregar Fritura al Carrito", key="sugg_add_frit"):
                    add_to_cart(str(suggested_item.get("id")))
                    st.rerun()

        st.write("---")
        st.subheader(":material/local_shipping: Datos de Entrega y Ubicación GPS")
        
        customer_name = st.text_input("Nombre del cliente (Obligatorio)", value=st.session_state.saved_customer_name, placeholder="Ej. Juan Pérez")
        customer_address = st.text_area("Dirección / Referencias (Obligatorio)", value=st.session_state.saved_customer_address, placeholder="Calle, número, colonia...")
        
        st.markdown("**Forma de pago:**")
        payment_method = st.selectbox("Selecciona cómo pagarás", ["Efectivo", "Transferencia bancaria", "Tarjeta al recibir"], label_visibility="collapsed")
        
        cash_change_note = ""
        if payment_method == "Efectivo":
            cash_pay = st.text_input("¿Con cuánto billete pagarás? (Opcional, para llevarte cambio)", placeholder="Ej. $200 o $500")
            if cash_pay.strip():
                cash_change_note = f"Paga con: {cash_pay}"

        customer_gps = st.text_input("Enlace o Coordenadas de Google Maps (Opcional)", value=st.session_state.saved_customer_gps, placeholder="Ej. https://maps.app.goo.gl/... o 18.456,-97.389")
        customer_notes = st.text_input("Notas adicionales (Opcional)", placeholder="Ej. Tocar dos veces el timbre")
        
        st.session_state.saved_customer_name = customer_name
        st.session_state.saved_customer_address = customer_address
        st.session_state.saved_customer_gps = customer_gps

        order_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        msg_header = f"NUEVO PEDIDO - MOSTACHO BOTANAS\nFecha: {order_date}\n\n"
        msg_items = "DETALLE DE PRODUCTOS:\n" + "\n".join(order_summary) + "\n\n"
        msg_total = f"TOTAL: ${total_price:.2f} MXN\n\n"
        msg_customer = f"CLIENTE: {customer_name}\n"
        msg_address = f"DIRECCION: {customer_address}\n"
        msg_pay = f"METODO DE PAGO: {payment_method}\n" + (f"{cash_change_note}\n" if cash_change_note else "")
        msg_gps = f"UBICACION GPS: {customer_gps}\n" if customer_gps.strip() else "UBICACION GPS: No proporcionada\n"
        msg_notes = f"NOTAS: {customer_notes}\n" if customer_notes else ""
        
        full_message = msg_header + msg_items + msg_total + msg_customer + msg_address + msg_pay + msg_gps + msg_notes
        encoded_message = urllib.parse.quote(full_message)
        whatsapp_url = f"https://wa.me/{WHATSAPP_PHONE}?text={encoded_message}"
        
        st.write("")
        if store_is_open:
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
        else:
            st.markdown(
                '<div class="store-closed-banner" style="font-size: 0.9rem; padding: 12px;">Lo sentimos, la tienda se encuentra cerrada temporalmente para nuevos pedidos.</div>',
                unsafe_allow_html=True
            )

elif st.session_state.nav_view == "admin":
    st.markdown("### :material/settings: Panel de Administración")
    
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
        
        tab_status, tab_prod, tab_pop, tab_banner, tab_upload = st.tabs(["🟢 Estado Tienda", "📦 Productos", "⭐ Populares", "🖼️ Banner", "📤 Subir"])
        
        with tab_status:
            st.markdown("### Control de Apertura de la Tienda")
            st.caption("Cambia el estado de la tienda en tiempo real para recibir o pausar pedidos:")
            
            current_status = st.session_state.store_config.get("store_open", True)
            new_status = st.toggle("🟢 Tienda Abierta para Pedidos", value=current_status)
            
            if st.button("Guardar Estado de Tienda"):
                st.session_state.store_config["store_open"] = new_status
                save_config(st.session_state.store_config)
                st.success(f"¡Estado actualizado! La tienda ahora está {'Abierta' if new_status else 'Cerrada'}.")
                st.rerun()

        with tab_prod:
            st.markdown("### Inventario de Productos y Destacados")
            st.info("💡 Marca la casilla 'bestseller' para que aparezca la insignia '🔥 Más Vendido'.")
            
            current_sorted_products = sorted(st.session_state.products, key=lambda x: str(x.get("name", "")).lower())
            df_current = pd.DataFrame(current_sorted_products)
            
            column_config = {
                "id": None,
                "category": st.column_config.SelectboxColumn(
                    "Categoría",
                    options=["Individual", "Para compartir"],
                    required=True
                ),
                "bestseller": st.column_config.CheckboxColumn(
                    "🔥 Más Vendido",
                    help="Destacar producto"
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
                    
                    raw_img = str(row.get("image", "")).strip()
                    prod_img = raw_img if raw_img != "" and raw_img.lower() != "nan" and "placeholder" not in raw_img else DEFAULT_PRODUCT_IMG
                    
                    raw_desc = row.get("description")
                    prod_desc = str(raw_desc).strip() if pd.notna(raw_desc) and str(raw_desc).strip() != "nan" else ""
                    
                    is_best_val = bool(row.get("bestseller", False))
                    
                    updated_list.append({
                        "id": prod_id,
                        "name": str(row.get("name", "Nuevo producto")),
                        "category": str(row.get("category", "Individual")),
                        "price": float(row.get("price", 0.0)),
                        "description": prod_desc,
                        "image": prod_img,
                        "bestseller": is_best_val
                    })
                    
                updated_list = sorted(updated_list, key=lambda x: str(x.get("name", "")).lower())
                st.session_state.products = updated_list
                save_products_to_file(updated_list)
                st.success("¡Productos guardados y ordenados!")
                st.rerun()

        with tab_pop:
            st.markdown("### Seleccionar Productos Populares")
            current_pop_ids = [str(p.get("id")) for p in st.session_state.popular_items]
            
            selected_populares_new = []
            for prod in st.session_state.products:
                p_id = str(prod.get("id"))
                p_name = str(prod.get("name"))
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
            new_banner_url = st.text_input("URL de la imagen del banner", value=st.session_state.banner_url)
            if st.button("Guardar Banner"):
                if new_banner_url.strip():
                    st.session_state.banner_url = new_banner_url.strip()
                    save_banner_to_file(new_banner_url.strip())
                    st.success("¡Banner actualizado!")
                    st.rerun()

        with tab_upload:
            st.markdown("### Subir Imagen Directamente")
            uploaded_file = st.file_uploader("Elige una imagen", type=["png", "jpg", "jpeg", "webp"])
            if uploaded_file is not None:
                file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"¡Subida con éxito: `{uploaded_file.name}`!")
                st.image(file_path, width=200)
                local_url = f"/{UPLOAD_DIR}/{uploaded_file.name}"
                st.text_input("Copia esta ruta para usarla:", value=local_url)
        
        st.write("---")
        if st.button("Cerrar Sesión Admin"):
            st.session_state.admin_authenticated = False
            st.rerun()