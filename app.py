import streamlit as st
import pandas as pd
import urllib.parse
import json
import os

LOGO_URL = "https://raw.githubusercontent.com/Mostacho100/Mostacho-Botanas-Web/main/logo.png"
DEFAULT_BANNER = "https://raw.githubusercontent.com/Mostacho100/Mostacho-Botanas-Web/main/banner.jpg"
DEFAULT_PRODUCT_IMG = "https://raw.githubusercontent.com/Mostacho100/Mostacho-Botanas-Web/main/image.jpg"

DATA_FILE = "productos_mostacho.json"
POPULAR_FILE = "populares_mostacho.json"
BANNER_FILE = "banner_mostacho.json"
CONFIG_FILE = "config_mostacho.json"
UPLOAD_DIR = "uploaded_images"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

st.set_page_config(
    page_title="Mostacho Botanas",
    page_icon=LOGO_URL,
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

WHATSAPP_PHONE = "522381174698"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"store_open": True}

if "store_config" not in st.session_state:
    st.session_state.store_config = load_config()

def load_saved_products():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    cleaned = []
                    for idx, item in enumerate(data):
                        if isinstance(item, dict):
                            item["id"] = str(item.get("id", f"auto_{idx}"))
                            item["name"] = str(item.get("name", "Sin nombre"))
                            item["category"] = str(item.get("category", "Individual"))
                            item["price"] = float(item.get("price", 0.0))
                            item["description"] = str(item.get("description", "")) if pd.notna(item.get("description")) else ""
                            img = str(item.get("image", "")).strip()
                            item["image"] = img if img and img.lower() != "nan" and "placeholder" not in img else DEFAULT_PRODUCT_IMG
                            cleaned.append(item)
                    return sorted(cleaned, key=lambda x: str(x.get("name", "")).lower())
        except:
            pass
    return [
        {"id": "p1", "name": "Pistaches Salados (90g)", "category": "Individual", "price": 35.0, "description": "Pistaches tostados con sal de mar.", "image": DEFAULT_PRODUCT_IMG},
        {"id": "p2", "name": "Fritura (Con Chile)", "category": "Para compartir", "price": 25.0, "description": "Crujientes frituras artesanales.", "image": DEFAULT_PRODUCT_IMG}
    ]

if "products" not in st.session_state:
    st.session_state.products = load_saved_products()

def save_products_to_file(prod_list):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(prod_list, f, ensure_ascii=False, indent=4)
    except:
        pass

# Estilos limpios y profesionales
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
    .whatsapp-btn {
        background: #25D366; color: white; padding: 14px; border-radius: 14px;
        text-align: center; font-weight: 800; display: block; text-decoration: none; margin-top: 10px;
    }
    .material-symbols-outlined {
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        vertical-align: middle;
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
store_is_open = st.session_state.store_config.get("store_open", True)

# Modal de Variantes
@st.dialog("Seleccionar Variante")
def variants_modal(base_name, items):
    st.markdown(f"### {base_name}")
    st.write("Elige la presentación:")
    st.write("---")
    for idx, var in enumerate(items):
        v_id = str(var.get("id"))
        col1, col2, col3 = st.columns([1, 2, 1.5])
        with col1:
            st.image(var.get("image", DEFAULT_PRODUCT_IMG), width=45)
        with col2:
            st.markdown(f"**{var.get('name')}**")
            st.markdown(f"<span style='color: #FE8330; font-weight: bold;'>${var.get('price'):.2f} MXN</span>", unsafe_allow_html=True)
        with col3:
            q = st.session_state.cart.get(v_id, 0)
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                if st.button("-", key=f"mv_sub_{v_id}_{idx}", use_container_width=True):
                    remove_from_cart(v_id)
                    st.rerun()
            with sc2:
                st.markdown(f"<div style='text-align:center; font-weight:bold;'>{q}</div>", unsafe_allow_html=True)
            with sc3:
                if st.button("+", key=f"mv_add_{v_id}_{idx}", use_container_width=True):
                    add_to_cart(v_id)
                    st.rerun()
        st.write("---")
    if st.button("Listo", type="primary", use_container_width=True):
        st.session_state.show_variants_modal = False
        st.rerun()

if st.session_state.show_variants_modal:
    variants_modal(st.session_state.current_modal_base, st.session_state.current_modal_items)

# Encabezado con Logo
col_logo, col_info = st.columns([1, 5])
with col_logo:
    st.image(LOGO_URL, width=60)
with col_info:
    st.markdown("<h1 style='margin:0; font-size:1.6rem;'>Mostacho Botanas</h1>", unsafe_allow_html=True)
    st.markdown("<span style='color: #64748b; font-size: 0.8rem; font-weight:700;'>CATÁLOGO Y PEDIDOS EN LÍNEA</span>", unsafe_allow_html=True)

st.write("")

# Navbar
col_n1, col_n2, col_n3 = st.columns(3)
with col_n1:
    if st.button("Inicio", use_container_width=True):
        st.session_state.nav_view = "catalogo"
        st.rerun()
with col_n2:
    if st.button(f"Carrito ({total_items})", use_container_width=True):
        st.session_state.nav_view = "carrito"
        st.rerun()
with col_n3:
    if st.button("Config", use_container_width=True):
        st.session_state.nav_view = "admin"
        st.rerun()

st.write("---")

if st.session_state.nav_view == "catalogo":
    if not store_is_open:
        st.warning("🔒 La tienda se encuentra cerrada temporalmente para nuevos pedidos.")

    search_query = st.text_input("Buscar productos...", placeholder="Buscar botanas...", label_visibility="collapsed")
    
    st.markdown(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 6px; margin: 12px 0 16px 0; text-align: center;">
        <img src="{DEFAULT_BANNER}" style="width: 100%; height: 150px; object-fit: cover; border-radius: 12px;" onerror="this.src='{LOGO_URL}';" />
    </div>
    """, unsafe_allow_html=True)

    cats = ["Todo", "Individual", "Para compartir"]
    cat_cols = st.columns(len(cats))
    for i, c in enumerate(cats):
        with cat_cols[i]:
            if st.button(c, use_container_width=True, key=f"cat_{c}"):
                st.session_state.selected_cat = c
                st.rerun()

    st.write("---")

    filtered = [p for p in st.session_state.products if (st.session_state.selected_cat == "Todo" or str(p.get("category")) == st.session_state.selected_cat) and (search_query.lower() in str(p.get("name")).lower() or search_query.lower() in str(p.get("description")).lower())]

    if not filtered:
        st.info("No se encontraron productos.")
    else:
        grouped = {}
        for p in filtered:
            name_raw = str(p.get("name"))
            base = name_raw.split("(")[0].strip() if "(" in name_raw else name_raw
            if base not in grouped:
                grouped[base] = []
            grouped[base].append(p)

        group_list = list(grouped.items())
        for i in range(0, len(group_list), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(group_list):
                    base_name, items = group_list[i + j]
                    rep = items[0]
                    pid = rep.get("id")

                    with cols[j]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        st.image(rep.get("image", DEFAULT_PRODUCT_IMG), use_container_width=True)
                        st.markdown(f"**{base_name}**")
                        if rep.get("description"):
                            st.caption(rep.get("description"))
                        
                        prices = [float(it.get("price", 0)) for it in items]
                        st.markdown(f"<span style='color: #FE8330; font-weight: 900;'>${prices[0]:.2f} MXN</span>", unsafe_allow_html=True)
                        
                        st.write("")
                        if len(items) > 1:
                            if store_is_open and st.button("Ver Opciones", key=f"opt_{base_name}", use_container_width=True):
                                st.session_state.current_modal_base = base_name
                                st.session_state.current_modal_items = items
                                st.session_state.show_variants_modal = True
                                st.rerun()
                        else:
                            q = st.session_state.cart.get(pid, 0)
                            if store_is_open:
                                if q == 0:
                                    if st.button("Agregar", key=f"add_{pid}", use_container_width=True):
                                        add_to_cart(pid)
                                        st.rerun()
                                else:
                                    sc1, sc2, sc3 = st.columns([1, 1.2, 1])
                                    with sc1:
                                        if st.button("-", key=f"minus_{pid}", use_container_width=True):
                                            remove_from_cart(pid)
                                            st.rerun()
                                    with sc2:
                                        st.markdown(f"<div style='text-align:center; font-weight:bold; margin-top:5px;'>{q}</div>", unsafe_allow_html=True)
                                    with sc3:
                                        if st.button("+", key=f"plus_{pid}", use_container_width=True):
                                            add_to_cart(pid)
                                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.nav_view == "carrito":
    st.markdown("### 🛒 Carrito de Compras")
    if not st.session_state.cart:
        st.info("Tu carrito está vacío.")
    else:
        total = 0.0
        summary = []
        for pid, qty in list(st.session_state.cart.items()):
            p = next((item for item in st.session_state.products if str(item.get("id")) == str(pid)), None)
            if p:
                sub = p.get("price") * qty
                total += sub
                summary.append(f"- {qty}x {p.get('name')} (${sub:.2f})")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{p.get('name')}** x {qty} = ${sub:.2f} MXN")
                with col2:
                    if st.button("Quitar", key=f"del_{pid}", use_container_width=True):
                        del st.session_state.cart[pid]
                        st.rerun()

        st.write("---")
        st.markdown(f"### Total: **${total:.2f} MXN**")
        st.write("---")
        st.subheader("Datos de Entrega")
        
        c_name = st.text_input("Nombre completo")
        c_address = st.text_area("Dirección de entrega y referencias")

        msg = f"NUEVO PEDIDO - MOSTACHO BOTANAS\n\n" + "\n".join(summary) + f"\n\nTOTAL: ${total:.2f} MXN\n\nCLIENTE: {c_name}\nDIRECCION: {c_address}"
        wa_url = f"https://wa.me/{WHATSAPP_PHONE}?text={urllib.parse.quote(msg)}"

        if c_name and c_address:
            st.markdown(f'<a href="{wa_url}" target="_blank" class="whatsapp-btn">💬 Enviar pedido por WhatsApp</a>', unsafe_allow_html=True)
        else:
            st.warning("Completa tu nombre y dirección para habilitar el botón de WhatsApp.")

elif st.session_state.nav_view == "admin":
    st.markdown("### ⚙️ Administración")
    if not st.session_state.admin_authenticated:
        pass_input = st.text_input("Contraseña", type="password")
        if st.button("Ingresar") and pass_input == "7031":
            st.session_state.admin_authenticated = True
            st.rerun()
    else:
        st.success("Acceso concedido")
        df = pd.DataFrame(st.session_state.products)
        edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("Guardar Cambios"):
            st.session_state.products = edited.to_dict(orient="records")
            save_products_to_file(st.session_state.products)
            st.success("¡Guardado!")
            st.rerun()