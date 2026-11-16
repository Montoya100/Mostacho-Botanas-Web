import streamlit as st
import pandas as pd
import urllib.parse
import requests
import json
import os
import random
import re
from datetime import datetime

LOGO_URL = "https://raw.githubusercontent.com/Montoya100/Mostacho-Botanas-Web/main/logo.png"
DATA_FILE = "productos_mostacho.json"
POPULAR_FILE = "populares_mostacho.json"
BANNER_FILE = "banner_mostacho.json"
SUGGESTION_FILE = "sugerencia_mostacho.json"
THEME_FILE = "tema_mostacho.json"
TRIVIA_FILE = "trivia_mostacho.json"
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

# ==========================================
# GESTIÓN DE MODO OSCURO / CLARO
# ==========================================
def load_dark_mode_setting():
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data.get("auto_dark_mode", True))
        except:
            pass
    return True

def save_dark_mode_setting(enabled):
    try:
        with open(THEME_FILE, "w", encoding="utf-8") as f:
            json.dump({"auto_dark_mode": bool(enabled)}, f, ensure_ascii=False, indent=4)
    except:
        pass

if "auto_dark_mode" not in st.session_state:
    st.session_state.auto_dark_mode = load_dark_mode_setting()

# 2. Inicializar Estado
if "cart" not in st.session_state:
    st.session_state.cart = {}

if "nav_view" not in st.session_state:
    st.session_state.nav_view = "catalogo"

if "selected_cat" not in st.session_state:
    st.session_state.selected_cat = "Todo"

if "show_variants_modal" not in st.session_state:
    st.session_state.show_variants_modal = False

if "show_success_modal" not in st.session_state:
    st.session_state.show_success_modal = False

if "current_modal_base" not in st.session_state:
    st.session_state.current_modal_base = ""

if "current_modal_items" not in st.session_state:
    st.session_state.current_modal_items = []

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if "trivia_answered" not in st.session_state:
    st.session_state.trivia_answered = False

if "trivia_won" not in st.session_state:
    st.session_state.trivia_won = False

if "saved_customer_name" not in st.session_state:
    st.session_state.saved_customer_name = ""

if "saved_customer_address" not in st.session_state:
    st.session_state.saved_customer_address = ""

LOYVERSE_TOKEN = "1a4ee083d81e4525a48503180767c22d"
WHATSAPP_PHONE = "522381174698"

# ==========================================
# GESTIÓN DE TRIVIA CONFIGURABLE
# ==========================================
DEFAULT_TRIVIA = [
    {
        "pregunta": "¿Cuál es el ingrediente principal de un buen guacamole tradicional?",
        "opciones": "Aguacate | Tomate verde | Calabaza",
        "respuesta": "Aguacate"
    },
    {
        "pregunta": "¿En qué estado de la República Mexicana se encuentra Tehuacán y Cacaloapan?",
        "opciones": "Puebla | Veracruz | Oaxaca",
        "respuesta": "Puebla"
    },
    {
        "pregunta": "¿Qué tipo de saborizante natural predomina en las botanas picositas estilo mexicano?",
        "opciones": "Chile y limón | Menta y chocolate | Canela y azúcar",
        "respuesta": "Chile y limón"
    }
]

def load_saved_trivia():
    if os.path.exists(TRIVIA_FILE):
        try:
            with open(TRIVIA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except:
            pass
    save_trivia_to_file(DEFAULT_TRIVIA)
    return DEFAULT_TRIVIA

def save_trivia_to_file(trivia_list):
    try:
        with open(TRIVIA_FILE, "w", encoding="utf-8") as f:
            json.dump(trivia_list, f, ensure_ascii=False, indent=4)
    except:
        pass

if "trivia_questions_db" not in st.session_state:
    st.session_state.trivia_questions_db = load_saved_trivia()

# ==========================================
# LIGAS Y ARCHIVOS DE RESPALDO
# ==========================================
DEFAULT_BANNER = "https://raw.githubusercontent.com/Montoya100/Mostacho-Botanas-Web/main/banner.jpg"
DEFAULT_PRODUCT_IMG = "https://raw.githubusercontent.com/Montoya100/Mostacho-Botanas-Web/main/image.jpg"

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

def load_saved_suggestion():
    if os.path.exists(SUGGESTION_FILE):
        try:
            with open(SUGGESTION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except:
            pass
    return {}

if "cart_suggestion" not in st.session_state:
    st.session_state.cart_suggestion = load_saved_suggestion()

def save_suggestion_to_file(sugg_dict):
    try:
        with open(SUGGESTION_FILE, "w", encoding="utf-8") as f:
            json.dump(sugg_dict, f, ensure_ascii=False, indent=4)
    except:
        pass

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

bg_color = "#f8fafc" if not st.session_state.auto_dark_mode else "#121212"
text_color = "#1e293b" if not st.session_state.auto_dark_mode else "#f1f5f9"
sub_text_color = "#64748b" if not st.session_state.auto_dark_mode else "#94a3b8"
card_bg = "#ffffff" if not st.session_state.auto_dark_mode else "#1e293b"
border_color = "#e2e8f0" if not st.session_state.auto_dark_mode else "#334155"

BTN_GENERAL = "#FE8330"
BTN_GENERAL_HOVER = "#e06c20"
BTN_CART_FAB = "#FF4500"        
BTN_CART_FAB_HOVER = "#d93800"

# ==========================================
# CSS DINÁMICO SEGÚN TEMA SELECCIONADO
# ==========================================
if st.session_state.auto_dark_mode:
    theme_specific_css = """
        .stApp, body, html, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #121212 !important;
            color: #f1f5f9 !important;
        }
        .app-title { color: #f8fafc !important; }
        .app-subtitle { color: #94a3b8 !important; }
        .product-card, .pop-card-box, .banner-container {
            background-color: #1e293b !important;
            border-color: #334155 !important;
        }
        .product-title, .pop-card-title, .qty-number {
            color: #f8fafc !important;
        }
        .product-desc { color: #cbd5e1 !important; }
        label p, .stTextInput label, .stTextArea label, [data-testid="stWidgetLabel"] p, .stRadio label p, .stRadio div[data-baseweb="radio"] span {
            color: #f1f5f9 !important;
        }
        input, textarea, select, 
        div[data-baseweb="input"], div[data-baseweb="base-input"], 
        div[data-baseweb="textarea"], div[data-baseweb="select"],
        [data-baseweb="input"] > div, [data-baseweb="base-input"] > div {
            background-color: #1e293b !important;
            color: #f1f5f9 !important;
            -webkit-text-fill-color: #f1f5f9 !important;
            border-color: #475569 !important;
        }
    """
else:
    theme_specific_css = """
        .stApp, body, html, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #f8fafc !important;
            color: #1e293b !important;
        }
        .app-title { color: #1e293b !important; }
        .app-subtitle { color: #64748b !important; }
        .product-card, .pop-card-box, .banner-container {
            background-color: #ffffff !important;
            border-color: #e2e8f0 !important;
        }
        .product-title, .pop-card-title, .qty-number {
            color: #1e293b !important;
        }
        .product-desc { color: #64748b !important; }
        label p, .stTextInput label, .stTextArea label, [data-testid="stWidgetLabel"] p, .stRadio label p, .stRadio div[data-baseweb="radio"] span {
            color: #1e293b !important;
            -webkit-text-fill-color: #1e293b !important;
        }
        input, textarea, select, 
        div[data-baseweb="input"], div[data-baseweb="base-input"], 
        div[data-baseweb="textarea"], div[data-baseweb="select"],
        [data-baseweb="input"] > div, [data-baseweb="base-input"] > div {
            background-color: #ffffff !important;
            color: #1e293b !important;
            -webkit-text-fill-color: #1e293b !important;
            border-color: #cbd5e1 !important;
        }
    """

st.markdown(f"""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />

<style>
    div[data-baseweb="modal"], div[role="dialog"], section[tabindex="-1"], 
    div[data-testid="stModal"], div[data-modal-container="true"] {{
        background-color: rgba(0, 0, 0, 0.5) !important;
        z-index: 999999999 !important;
    }}
    
    div[data-baseweb="modal"] > div, div[role="dialog"] > div,
    section[tabindex="-1"] > div, div[data-testid="stModal"] > div {{
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #1e293b !important;
        width: 90vw !important;
        max-width: 440px !important;
        border-radius: 18px !important;
        padding: 14px 12px !important;
        max-height: 88vh !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25) !important;
        z-index: 1000000000 !important;
        margin: auto !important;
        border: none !important;
    }}

    div[data-baseweb="modal"] *, div[role="dialog"] *, section[tabindex="-1"] * {{
        background-color: transparent !important;
        color: #1e293b !important;
    }}

    div[data-baseweb="modal"] div[data-testid="stVerticalBlock"], 
    div[role="dialog"] div[data-testid="stVerticalBlock"] {{
        max-height: 68vh !important;
        overflow-y: auto !important;
        padding: 0 2px !important;
        background-color: #ffffff !important;
    }}

    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 6rem !important;
        max-width: 100% !important;
    }}

    .app-title {{
        font-size: 2rem !important;
        font-weight: 900 !important;
        margin: 0 !important;
        line-height: 1.1 !important;
    }}
    .app-subtitle {{
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        margin-top: 2px !important;
        display: block;
    }}

    input::placeholder, textarea::placeholder {{
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
    }}

    div[data-testid="stButton"]:has(button[kind="primary"]) {{
        position: fixed !important;
        bottom: 22px !important;
        left: 22px !important;
        right: auto !important;
        transform: none !important;
        z-index: 99999 !important;
        width: auto !important;
    }}
    div[data-testid="stButton"]:has(button[kind="primary"]) > button {{
        background: linear-gradient(135deg, {BTN_CART_FAB} 0%, #ff6a33) !important;
        color: #ffffff !important;
        padding: 12px 22px !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 4px 15px rgba(255, 69, 0, 0.4) !important;
        border: none !important;
        height: 48px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        white-space: nowrap !important;
    }}
    div[data-testid="stButton"]:has(button[kind="primary"]) > button p,
    div[data-testid="stButton"]:has(button[kind="primary"]) > button span {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 0.95rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    .popular-badge {{
        position: absolute;
        top: 10px;
        right: 10px;
        background: linear-gradient(135deg, #FF4500 0%, #ff6a33);
        color: white;
        font-size: 0.65rem;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 20px;
        z-index: 5;
        text-transform: uppercase;
        box-shadow: 0 2px 6px rgba(255,69,0,0.3);
    }}

    .whatsapp-btn-disabled {{
        background-color: #cbd5e1 !important;
        color: #475569 !important;
        padding: 14px;
        border-radius: 14px;
        text-align: center;
        font-weight: 700;
        font-size: 0.9rem;
        margin-top: 10px;
        display: block;
        width: 100%;
    }}

    button, .stButton > button, div[data-testid="stButton"] > button {{
        background-color: {BTN_GENERAL} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(254, 131, 48, 0.2) !important;
        transition: all 0.2s ease-in-out !important;
    }}
    button:hover, .stButton > button:hover {{
        background-color: {BTN_GENERAL_HOVER} !important;
        transform: translateY(-2px) !important;
        color: #ffffff !important;
    }}

    /* CENTRADO PERFECTO DE CANTIDADES EN MÓVIL Y ESCRITORIO */
    .qty-number {{
        font-size: 1.1rem !important;
        font-weight: 900 !important;
        text-align: center !important;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        margin: 0 auto;
    }}

    .promo-banner {{
        background: linear-gradient(135deg, {BTN_GENERAL} 0%, {BTN_CART_FAB} 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 14px;
        text-align: center;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 14px;
        box-shadow: 0 4px 10px rgba(254, 131, 48, 0.2);
    }}

    .banner-container {{
        border: 1px solid {border_color} !important;
        border-radius: 16px;
        padding: 6px;
        margin-bottom: 16px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        text-align: center;
        width: 100%;
        overflow: hidden;
    }}

    {theme_specific_css}
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

def go_to_cart():
    st.session_state.nav_view = "carrito"
    st.rerun()

def go_to_catalogo():
    st.session_state.show_variants_modal = False
    st.session_state.nav_view = "catalogo"
    st.rerun()

def go_to_admin():
    st.session_state.show_variants_modal = False
    st.session_state.nav_view = "admin"
    st.rerun()

keys_to_delete = [pid for pid in st.session_state.cart if not any(p.get("id") == pid for p in st.session_state.products)]
for k in keys_to_delete:
    del st.session_state.cart[k]

total_items = sum(st.session_state.cart.values())

total_cart_amount = sum(
    float(next((p.get("price", 0) for p in st.session_state.products if str(p.get("id")) == str(pid)), 0)) * qty
    for pid, qty in st.session_state.cart.items()
)

# ==========================================
# MODAL DE VARIANTES
# ==========================================
@st.dialog("Seleccionar Variante o Presentación")
def variants_modal_dialog(base_name, variants_list):
    st.markdown(f"<h3 style='color: {BTN_GENERAL} !important; margin-bottom: 2px; text-align: center; font-size: 1.3rem;'>{base_name}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {sub_text_color} !important; font-size: 0.85rem; font-weight: 600; text-align: center; margin-bottom: 8px;'>Escoge la figura y el sabor que deseas:</p>", unsafe_allow_html=True)
    st.markdown(f"<hr style='margin: 4px 0 10px 0; border-color: {border_color};'>", unsafe_allow_html=True)
    
    for idx, var in enumerate(variants_list):
        v_id = str(var.get("id"))
        v_name = var.get("name")
        v_price = float(var.get("price", 0))
        
        v_img = str(var.get("image", "")).strip()
        if not v_img or v_img.lower() == "nan" or "placeholder" in v_img:
            v_img = DEFAULT_PRODUCT_IMG
            
        qty_in_cart = st.session_state.cart.get(v_id, 0)
        
        st.markdown(f"""
        <div style="background: {card_bg}; border: 1px solid {border_color}; border-radius: 10px; padding: 6px 10px; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                <img src="{v_img}" style="width: 32px; height: 32px; object-fit: cover; border-radius: 6px;" onerror="this.src='{DEFAULT_PRODUCT_IMG}';" />
                <div style="flex-grow: 1;">
                    <span style="color: {text_color} !important; font-weight: 800; font-size: 0.8rem; display: block; line-height: 1.1;">{v_name}</span>
                    <span style="color: {BTN_GENERAL}; font-weight: 900; font-size: 0.8rem;">${v_price:.2f} MXN</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col_m, col_n, col_p = st.columns([1, 1.2, 1], vertical_alignment="center")
        with col_m:
            if st.button("-", key=f"m_minus_{v_id}_{idx}", use_container_width=True):
                remove_from_cart(v_id)
                st.rerun()
        with col_n:
            st.markdown(f"<div class='qty-number' style='color: {text_color};'>{qty_in_cart}</div>", unsafe_allow_html=True)
        with col_p:
            if st.button("+", key=f"m_plus_{v_id}_{idx}", use_container_width=True):
                add_to_cart(v_id)
                st.rerun()
                
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("")
    if st.button("Listo / Ver Carrito", type="primary", use_container_width=True, key="close_modal_btn"):
        st.session_state.show_variants_modal = False
        st.rerun()

if st.session_state.show_variants_modal and st.session_state.nav_view == "catalogo":
    variants_modal_dialog(st.session_state.current_modal_base, st.session_state.current_modal_items)

# ==========================================
# MODAL DE ÉXITO AL ENVIAR PEDIDO
# ==========================================
@st.dialog("¡Pedido Realizado con Éxito!")
def success_order_dialog():
    st.markdown(f"""
    <div style="text-align: center; padding: 10px;">
        <span class="material-symbols-outlined" style="font-size: 56px; color: #25D366; margin-bottom: 8px;">check_circle</span>
        <h3 style="color: {text_color}; font-size: 1.2rem; font-weight: 800; margin-bottom: 6px;">¡Tu pedido se ha generado correctamente!</h3>
        <p style="color: {sub_text_color}; font-size: 0.9rem; margin-bottom: 16px;">Se ha abierto WhatsApp para enviar los detalles de tu compra. El sistema se reiniciará para que puedas realizar un nuevo pedido cuando gustes.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Entendido / Nuevo Pedido", type="primary", use_container_width=True):
        st.session_state.cart = {}
        st.session_state.trivia_answered = False
        st.session_state.trivia_won = False
        st.session_state.saved_customer_name = ""
        st.session_state.saved_customer_address = ""
        st.session_state.show_success_modal = False
        go_to_catalogo()

if st.session_state.get("show_success_modal", False):
    success_order_dialog()

# ==========================================
# 4. ENCABEZADO Y BÚSQUEDA
# ==========================================
col_title, col_cart_btn = st.columns([3, 1])

with col_title:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px;">
        <img src="{LOGO_URL}" style="width: 52px; height: 52px; object-fit: contain; background: transparent;" onerror="this.style.display='none'" />
        <div>
            <h1 class="app-title">Mostacho Botanas</h1>
            <span class="app-subtitle">Catálogo y pedidos en línea</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_cart_btn:
    st.write("")
    cart_btn_label = f"({total_items}) - ${total_cart_amount:.2f}" if total_items > 0 else ""
    if st.button(":material/shopping_cart: Carrito " + cart_btn_label, use_container_width=True, key="header_cart_btn"):
        st.session_state.show_variants_modal = False
        if st.session_state.nav_view != "carrito":
            go_to_cart()
        else:
            go_to_catalogo()

st.write("")

if st.session_state.nav_view != "admin":
    search_query = st.text_input("Buscar productos...", placeholder="Buscar semillas, cacahuates, pistaches...", label_visibility="collapsed")
    st.write("---")

# ==========================================
# 5. VISTAS: CATÁLOGO, CARRITO O ADMINISTRACIÓN
# ==========================================
if st.session_state.nav_view == "catalogo":
    st.markdown(
        f'<div class="promo-banner"><span class="material-symbols-outlined" style="vertical-align: -4px; margin-right: 6px;">local_shipping</span> ¡Envíos locales y entregas directas en ruta! Pide fácil y rápido</div>', 
        unsafe_allow_html=True
    )
    
    banner_to_show = str(st.session_state.banner_url).strip()
    if not banner_to_show or banner_to_show.lower() == "nan":
        banner_to_show = DEFAULT_BANNER

    st.markdown(f"""
    <div class="banner-container" style="background: {card_bg};">
        <img src="{banner_to_show}" class="desktop-banner-img" onerror="this.onerror=null;this.src='{DEFAULT_BANNER}';" />
    </div>
    """, unsafe_allow_html=True)

    # POPULARES
    popular_ids = [str(p.get("id")) for p in st.session_state.popular_items]
    if popular_ids:
        st.markdown(f"### <span class='material-symbols-outlined' style='font-size: 24px; color: #FE8330;'>local_fire_department</span> Populares", unsafe_allow_html=True)
        pop_list = [p for p in st.session_state.products if str(p.get("id")) in popular_ids]
        if pop_list:
            pop_cols = st.columns(min(len(pop_list), 3))
            for idx, p in enumerate(pop_list):
                with pop_cols[idx % len(pop_cols)]:
                    pid = p.get("id")
                    st.markdown(f"""
                    <div class="pop-card-box">
                        <div class="popular-badge">🔥 Lo más pedido</div>
                        <img src="{p.get('image', DEFAULT_PRODUCT_IMG)}" style="width: 100%; height: 95px; object-fit: cover; border-radius: 8px; margin-top: 15px;" onerror="this.src='{DEFAULT_PRODUCT_IMG}';" />
                        <div class="pop-card-title">{p.get('name')}</div>
                        <div style="color: {BTN_GENERAL}; font-weight: 900; font-size: 0.95rem;">${p.get('price'):.2f} MXN</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Agregar +", key=f"pop_add_{pid}_{idx}", use_container_width=True):
                        add_to_cart(pid)
                        st.rerun()
            st.write("---")

    # CATEGORÍAS
    cats = ["Todo", "Individual", "Para compartir"]
    cat_cols = st.columns(len(cats))
    for i, c in enumerate(cats):
        with cat_cols[i]:
            is_active = (st.session_state.selected_cat == c)
            display_label = f"● {c}" if is_active else c
            if st.button(display_label, use_container_width=True, key=f"cat_btn_{c}"):
                st.session_state.selected_cat = c
                st.rerun()

    st.write("---")

    # LISTADO
    try:
        current_products_list = sorted(st.session_state.products, key=lambda x: str(x.get("name", "")).lower())
        
        if st.session_state.selected_cat == "Todo":
            cat_filtered = current_products_list
        else:
            cat_filtered = [p for p in current_products_list if str(p.get("category", "Individual")).strip() == st.session_state.selected_cat]

        filtered_products = [p for p in cat_filtered if search_query.lower() in str(p.get("name", "")).lower() or search_query.lower() in str(p.get("description", "")).lower()]
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

        group_items_list = sorted(list(grouped_dict.items()), key=lambda x: 0 if len(x[1]) > 1 else 1)
        
        for i in range(0, len(group_items_list), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(group_items_list):
                    base_name, items_group = group_items_list[i + j]
                    representative = items_group[0]
                    pid = representative.get("id")
                    
                    with cols[j]:
                        st.markdown(f'<div class="product-card" style="background-color: {card_bg}; border: 1px solid {border_color};">', unsafe_allow_html=True)
                        
                        img_src = str(representative.get("image", "")).strip()
                        if not img_src or img_src.lower() == "nan" or "placeholder" in img_src:
                            img_src = DEFAULT_PRODUCT_IMG
                        
                        try:
                            st.image(img_src, use_container_width=True)
                        except:
                            st.image(DEFAULT_PRODUCT_IMG, use_container_width=True)
                        
                        st.markdown(f'<div class="product-title" style="margin-top: 8px;">{base_name}</div>', unsafe_allow_html=True)
                        desc_text = str(representative.get("description", "")).strip()
                        if desc_text and desc_text.lower() != "nan":
                            st.markdown(f'<div class="product-desc" style="color: {sub_text_color};">{desc_text}</div>', unsafe_allow_html=True)
                        
                        prices = [float(it.get("price", 0)) for it in items_group]
                        st.markdown(f'<div class="product-price">${prices[0]:.2f} MXN</div>', unsafe_allow_html=True)
                        
                        st.write("")
                        if len(items_group) > 1:
                            if st.button("Ver Opciones", key=f"variants_btn_{base_name}_{pid}", use_container_width=True):
                                st.session_state.current_modal_base = base_name
                                st.session_state.current_modal_items = items_group
                                st.session_state.show_variants_modal = True
                                st.rerun()
                        else:
                            qty_in_cart = st.session_state.cart.get(pid, 0)
                            if qty_in_cart == 0:
                                if st.button("Agregar", key=f"add_{pid}", use_container_width=True):
                                    add_to_cart(pid)
                                    st.rerun()
                            else:
                                sub_c1, sub_c2, sub_c3 = st.columns([1, 1.2, 1], vertical_alignment="center")
                                with sub_c1:
                                    if st.button("-", key=f"minus_{pid}", use_container_width=True):
                                        remove_from_cart(pid)
                                        st.rerun()
                                with sub_c2:
                                    st.markdown(f"<div class='qty-number' style='color: {text_color};'>{qty_in_cart}</div>", unsafe_allow_html=True)
                                with sub_c3:
                                    if st.button("+", key=f"plus_{pid}", use_container_width=True):
                                        add_to_cart(pid)
                                        st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

    if total_items > 0:
        fab_label = f":material/shopping_cart: Ver Carrito ({total_items}) - ${total_cart_amount:.2f} MXN"
        st.button(
            fab_label,
            type="primary",
            on_click=go_to_cart,
            key="native_floating_fab"
        )

elif st.session_state.nav_view == "carrito":
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
            p = next((item for item in st.session_state.products if str(item.get("id")) == str(item_id)), None)
            if p:
                subtotal = float(p.get("price", 0)) * qty
                total_price += subtotal
                order_summary.append(f"- {qty}x {p.get('name')} - ${subtotal:.2f} MXN")
                
                col_c1, col_c2 = st.columns([3, 1], vertical_alignment="center")
                with col_c1:
                    st.markdown(f"**{p.get('name')}**")
                    st.caption(f"{qty} x ${float(p.get('price', 0)):.2f} = ${subtotal:.2f}")
                with col_c2:
                    if st.button(":material/delete: Quitar", key=f"del_cart_{item_id}", use_container_width=True):
                        del st.session_state.cart[item_id]
                        st.rerun()
                        
        st.write("---")

        # --- TOTAL A PAGAR EN GRANDE EN EL CARRITO ---
        st.markdown(f"""
        <div style="background: {card_bg}; border: 2px solid {BTN_GENERAL}; border-radius: 12px; padding: 14px; text-align: center; margin-bottom: 16px;">
            <span style="font-size: 0.95rem; font-weight: 700; color: {sub_text_color}; display: block;">TOTAL DEL PEDIDO:</span>
            <span style="font-size: 1.6rem; font-weight: 900; color: {BTN_GENERAL};">${total_price:.2f} MXN</span>
        </div>
        """, unsafe_allow_html=True)

        # --- PRODUCTO GANCHO / SUGERENCIA DESDE EL PANEL ---
        sugg_id = st.session_state.cart_suggestion.get("id")
        if sugg_id:
            sugg_prod = next((p for p in st.session_state.products if str(p.get("id")) == str(sugg_id)), None)
            if sugg_prod and str(sugg_id) not in st.session_state.cart:
                st.info(f"💡 **¿Te hace falta alguna botanita para acompañar?** ¡Acompaña tu pedido con unos deliciosos **{sugg_prod.get('name')}** por solo **${sugg_prod.get('price'):.2f} MXN**!")
                if st.button(f"Agregar {sugg_prod.get('name')} al carrito", key="add_sugg_btn"):
                    add_to_cart(str(sugg_id))
                    st.rerun()
        
        st.subheader(":material/local_shipping: Datos de Entrega")
        
        customer_name = st.text_input("Nombre del cliente (Obligatorio)", value=st.session_state.saved_customer_name, placeholder="Ej. Juan Pérez")
        customer_address = st.text_area("Dirección / Referencias (Obligatorio)", value=st.session_state.saved_customer_address, placeholder="Calle, número, colonia...")
        customer_notes = st.text_input("Notas adicionales (Opcional)", placeholder="Ej. Cambio de $500")
        
        st.session_state.saved_customer_name = customer_name
        st.session_state.saved_customer_address = customer_address

        # --- TRIVIA PRE-WHATSAPP ---
        st.markdown("---")
        st.subheader("🧠 ¡Juega y gana una botana sorpresa antes de enviar!")

        if not st.session_state.trivia_answered:
            if "current_trivia_idx" not in st.session_state:
                st.session_state.current_trivia_idx = random.randint(0, len(st.session_state.trivia_questions_db) - 1)
            
            if st.session_state.current_trivia_idx >= len(st.session_state.trivia_questions_db):
                st.session_state.current_trivia_idx = 0

            t_data = st.session_state.trivia_questions_db[st.session_state.current_trivia_idx]
            raw_options = str(t_data.get("opciones", "A | B | C"))
            opciones_list = [o.strip() for o in raw_options.split("|") if o.strip()]

            st.info(f"**Pregunta:** {t_data.get('pregunta')}")
            respuesta_usuario = st.radio(
                "Elige tu respuesta:",
                opciones_list,
                key="trivia_selection"
            )

            if st.button("Comprobar respuesta", key="check_trivia_btn"):
                st.session_state.trivia_answered = True
                correct_ans = str(t_data.get("respuesta")).strip()
                if str(respuesta_usuario).strip().lower() == correct_ans.lower():
                    st.session_state.trivia_won = True
                st.rerun()
        else:
            if st.session_state.trivia_won:
                st.success("🎉 ¡Correcto! Has ganado una botana sorpresa en tu pedido.")
            else:
                st.warning("¡Casi la tienes! No te preocupes, tu pedido sigue en pie.")

            if st.button("Jugar otra pregunta", key="reset_trivia_btn"):
                st.session_state.trivia_answered = False
                st.session_state.trivia_won = False
                if "current_trivia_idx" in st.session_state:
                    del st.session_state.current_trivia_idx
                st.rerun()

        now = datetime.now()
        order_date = now.strftime("%d/%m/%Y %H:%M")
        
        # Código de verificación solo con mes y día (Ej. MOSTACHO-OK-1115)
        date_tag = now.strftime("%m%d")
        verification_code = f"MOSTACHO-OK-{date_tag}"

        # --- CÁLCULO AUTOMÁTICO DE CAMBIO DESDE LAS NOTAS ---
        change_text = ""
        if customer_notes.strip():
            numbers_in_notes = re.findall(r'\d+(?:\.\d+)?', customer_notes)
            if numbers_in_notes:
                amounts = [float(n) for n in numbers_in_notes]
                valid_cash = [amt for amt in amounts if amt >= total_price]
                if valid_cash:
                    cash_given = valid_cash[0]
                    change = cash_given - total_price
                    change_text = f"💵 Paga con: ${cash_given:.2f} MXN\n🪙 Cambio: ${change:.2f} MXN\n"

        # --- ESTRUCTURA EXACTA DEL MENSAJE DE WHATSAPP ---
        msg_header = "NUEVO PEDIDO\n"
        msg_date = f"Fecha: {order_date}\n"
        msg_customer = f"CLIENTE: {customer_name}\n"
        msg_address = f"DIRECCIÓN: {customer_address}\n"
        msg_notes = f"NOTAS: {customer_notes}\n" if customer_notes else ""
        msg_change = change_text
        
        msg_items_header = "\nDETALLE DE PRODUCTOS:\n" + "\n".join(order_summary) + "\n\n"
        msg_total = f"TOTAL: *${total_price:.2f} MXN*\n"
        
        msg_trivia = f"\n🎁 PREMIO GANADO: Botana Sorpresa\n🏷️ {verification_code}" if st.session_state.trivia_won else ""

        full_message = msg_header + msg_date + msg_customer + msg_address + msg_notes + msg_change + msg_items_header + msg_total + msg_trivia
        encoded_message = urllib.parse.quote(full_message)
        whatsapp_url = f"https://wa.me/{WHATSAPP_PHONE}?text={encoded_message}"
        
        st.write("")
        if customer_name.strip() and customer_address.strip():
            # Botón único con callback dedicado para evitar disparos accidentales
            def handle_whatsapp_click():
                st.session_state.show_success_modal = True

            st.link_button("💬 Enviar pedido por WhatsApp", url=whatsapp_url, use_container_width=True, type="primary")
            
            if st.button("Confirmar que ya abrí WhatsApp y reiniciar pedido", use_container_width=True, key="confirm_sent_btn"):
                st.session_state.cart = {}
                st.session_state.trivia_answered = False
                st.session_state.trivia_won = False
                st.session_state.saved_customer_name = ""
                st.session_state.saved_customer_address = ""
                st.session_state.show_success_modal = False
                go_to_catalogo()
        else:
            st.markdown(
                '<div class="whatsapp-btn-disabled">Completa Nombre y Dirección para activar el botón de envío</div>',
                unsafe_allow_html=True
            )

elif st.session_state.nav_view == "admin":
    if st.button(":material/arrow_back: Volver al Catálogo", use_container_width=False, key="back_from_admin"):
        go_to_catalogo()

    st.markdown("### :material/settings: Panel de Administración y Configuración")
    
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
        
        tab_prod, tab_pop, tab_sugg, tab_banner, tab_upload, tab_trivia, tab_theme = st.tabs([
            "📦 Productos", 
            "⭐ Populares", 
            "💡 Sugerencia Carrito", 
            "🖼️ Banner", 
            "📤 Subir",
            "🧠 Trivia",
            "🌓 Apariencia"
        ])
        
        with tab_prod:
            st.markdown("### Inventario de Productos")
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
                            r_img = str(row.get("image", "")).strip()
                            
                            desc_val = str(r_desc).strip() if pd.notna(r_desc) and str(r_desc).strip() != "nan" else ""
                            img_val = r_img if r_img != "" and r_img.lower() != "nan" and "placeholder" not in r_img else DEFAULT_PRODUCT_IMG
                            
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
                except Exception as e:
                    st.error(f"Error al procesar el archivo: {e}")

            st.write("---")
            current_sorted_products = sorted(st.session_state.products, key=lambda x: str(x.get("name", "")).lower())
            df_current = pd.DataFrame(current_sorted_products)
            column_config = {
                "id": None,
                "category": st.column_config.SelectboxColumn("Categoría", options=["Individual", "Para compartir"], required=True)
            }
            edited_df = st.data_editor(df_current, num_rows="dynamic", key="editor_admin_table", column_config=column_config, hide_index=True, use_container_width=True)
            
            if st.button("Guardar Cambios de Productos"):
                updated_list = []
                for idx, row in edited_df.iterrows():
                    raw_id = row.get("id")
                    prod_id = str(raw_id).strip() if pd.notna(raw_id) and str(raw_id).strip() != "" else f"prod_{int(datetime.now().timestamp())}_{idx}"
                    raw_img = str(row.get("image", "")).strip()
                    prod_img = raw_img if raw_img != "" and raw_img.lower() != "nan" and "placeholder" not in raw_img else DEFAULT_PRODUCT_IMG
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
                st.success("¡Productos guardados correctamente!")
                st.rerun()

        with tab_pop:
            st.markdown("### Seleccionar productos Populares")
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
            if st.button("Guardar Populares"):
                st.session_state.popular_items = selected_populares_new
                save_populares_to_file(selected_populares_new)
                st.success("¡Populares actualizados con éxito!")
                st.rerun()

        with tab_sugg:
            st.markdown("### Producto Gancho Sugerido en el Carrito")
            prod_options = {p.get("name"): p.get("id") for p in st.session_state.products}
            current_sugg_id = st.session_state.cart_suggestion.get("id")
            current_sugg_name = next((name for name, pid in prod_options.items() if str(pid) == str(current_sugg_id)), list(prod_options.keys())[0] if prod_options else "")
            
            selected_sugg_name = st.selectbox("Producto sugerido", options=list(prod_options.keys()), index=list(prod_options.keys()).index(current_sugg_name) if current_sugg_name in prod_options else 0)
            
            if st.button("Guardar Sugerencia de Carrito"):
                chosen_id = prod_options.get(selected_sugg_name)
                st.session_state.cart_suggestion = {"id": chosen_id}
                save_suggestion_to_file(st.session_state.cart_suggestion)
                st.success("¡Sugerencia gancho guardada correctamente!")
                st.rerun()

        with tab_banner:
            st.markdown("### Imagen del Banner Principal")
            new_banner_url = st.text_input("URL de la imagen del banner", value=st.session_state.banner_url)
            if st.button("Guardar Banner"):
                if new_banner_url.strip():
                    st.session_state.banner_url = new_banner_url.strip()
                    save_banner_to_file(new_banner_url.strip())
                    st.success("¡Banner actualizado con éxito!")
                    st.rerun()

        with tab_upload:
            st.markdown("### Subir Imágenes al Servidor")
            uploaded_file = st.file_uploader("Elige una imagen", type=["png", "jpg", "jpeg", "webp"])
            if uploaded_file is not None:
                file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"¡Subida con éxito: `{uploaded_file.name}`!")
                st.image(file_path, width=200)
                local_url = f"/{UPLOAD_DIR}/{uploaded_file.name}"
                st.text_input("Copia esta ruta:", value=local_url)

        with tab_trivia:
            st.markdown("### Administrar Preguntas de la Trivia")
            df_trivia = pd.DataFrame(st.session_state.trivia_questions_db)
            edited_trivia_df = st.data_editor(
                df_trivia,
                num_rows="dynamic",
                key="editor_trivia_table",
                use_container_width=True
            )
            
            if st.button("Guardar Preguntas de Trivia"):
                updated_trivia_list = []
                for _, row in edited_trivia_df.iterrows():
                    p_text = str(row.get("pregunta", "")).strip()
                    o_text = str(row.get("opciones", "")).strip()
                    r_text = str(row.get("respuesta", "")).strip()
                    if p_text and o_text and r_text:
                        updated_trivia_list.append({
                            "pregunta": p_text,
                            "opciones": o_text,
                            "respuesta": r_text
                        })
                if updated_trivia_list:
                    st.session_state.trivia_questions_db = updated_trivia_list
                    save_trivia_to_file(updated_trivia_list)
                    st.success("¡Preguntas de trivia guardadas exitosamente!")
                    st.rerun()
                else:
                    st.error("Debe haber al menos una pregunta válida.")

        with tab_theme:
            st.markdown("### Control de Apariencia y Modo Oscuro")
            dark_toggle = st.toggle("Activar detección automática de Modo Oscuro", value=st.session_state.auto_dark_mode)
            if st.button("Guardar Configuración de Tema"):
                st.session_state.auto_dark_mode = dark_toggle
                save_dark_mode_setting(dark_toggle)
                st.success("¡Preferencia guardada!")
                st.rerun()
        
        st.write("---")
        if st.button("Cerrar Sesión Admin", use_container_width=True):
            st.session_state.admin_authenticated = False
            go_to_catalogo()

# ==========================================
# 7. PIE DE PÁGINA
# ==========================================
st.write("---")
st.markdown("<br><br>", unsafe_allow_html=True)

col_foot1, col_foot_admin, col_foot2 = st.columns(3)
with col_foot_admin:
    if st.button(":material/settings: Admin", use_container_width=True, key="admin_footer_btn"):
        go_to_admin()