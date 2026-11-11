import streamlit as st
import pandas as pd
import urllib.parse

# 1. Configuración de la página (sidebar colapsado por defecto para móviles/usuarios)
st.set_page_config(
    page_title="Mostacho Botanas Web",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Inicializar Estado (Tema, Carrito, Productos)
if "theme" not in st.session_state:
    st.session_state.theme = "Claro"

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "products" not in st.session_state:
    st.session_state.products = [
        {"id": 1, "name": "Pistaches Salados (90g)", "category": "Chicos", "price": 35.0, "description": "Pistaches tostados con sal de mar, empaque individual de 90g.", "image": "https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=300"},
        {"id": 2, "name": "Cahuates Japoneses (100g)", "category": "Chicos", "price": 20.0, "description": "Cahuate crujiente estilo japonés, empaque chico.", "image": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=300"},
        {"id": 3, "name": "Semillas de Girasol Tostadas (80g)", "category": "Chicos", "price": 25.0, "description": "Semillas de girasol con sazón de la casa.", "image": "https://images.unsplash.com/photo-1508061252966-173859db501d?w=300"},
        {"id": 4, "name": "Pistaches Seleccionados (900g)", "category": "Para compartir", "price": 280.0, "description": "Bolsa familiar/distribución de 900g de pistache de alta calidad.", "image": "https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=300"},
        {"id": 5, "name": "Mix Botanero XL (1kg)", "category": "Para compartir", "price": 180.0, "description": "Mezcla de cacahuates, pepitas, habas y churritos sazonados.", "image": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=300"},
        {"id": 6, "name": "Frasco Regalo Pistache & Nuez", "category": "Detalles", "price": 150.0, "description": "Frasco de cristal decorado con combinación premium de semillas.", "image": "https://images.unsplash.com/photo-1508061252966-173859db501d?w=300"}
    ]

WHATSAPP_PHONE = "522381174698"

# 3. Estilos CSS adaptativos (Modo Día / Modo Noche tipo One UI)
is_dark = st.session_state.theme == "Oscuro"
bg_color = "#121212" if is_dark else "#f8f9fa"
card_bg = "#1e1e1e" if is_dark else "#ffffff"
text_color = "#e0e0e0" if is_dark else "#212529"
border_color = "#2c2c2c" if is_dark else "#e9ecef"

st.markdown(f"""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
<style>
    .stApp {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background-color: {bg_color};
        color: {text_color};
    }}
    .material-symbols-outlined {{
        font-family: 'Material Symbols Outlined';
        font-weight: normal;
        font-style: normal;
        font-size: 20px;
        line-height: 1;
        display: inline-block;
        vertical-align: middle;
    }}
    .product-card {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
    }}
    .product-title {{
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 4px;
        color: {text_color};
    }}
    .product-desc {{
        font-size: 0.88rem;
        color: #a0a0a0 if {is_dark} else #666666;
        margin-bottom: 8px;
    }}
    .product-price {{
        font-size: 1.05rem;
        font-weight: bold;
        color: #FF8C00;
    }}
    .promo-banner {{
        background: linear-gradient(135deg, #FF8C00 0%, #FFA500 100%);
        color: white;
        padding: 16px;
        border-radius: 16px;
        text-align: center;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(255,140,0,0.2);
    }}
    
    /* Slideshow / Carrusel CSS */
    .slideshow-container {{
        position: relative;
        max-width: 100%;
        height: 180px;
        margin-bottom: 24px;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
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
        10% {{ opacity: 1; }}
        33% {{ opacity: 1; }}
        43% {{ opacity: 0; }}
        100% {{ opacity: 0; }}
    }}
    .slide-text {{
        background: rgba(0, 0, 0, 0.6);
        color: white;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
    }}
</style>
""", unsafe_allow_html=True)

# Helper functions
def add_to_cart(product_id):
    st.session_state.cart[product_id] = st.session_state.cart.get(product_id, 0) + 1

def remove_from_cart(product_id):
    if product_id in st.session_state.cart:
        if st.session_state.cart[product_id] > 1:
            st.session_state.cart[product_id] -= 1
        else:
            del st.session_state.cart[product_id]

# 4. Header (Logo, Título y Selector de Tema Día/Noche)
col_logo, col_title, col_theme = st.columns([1, 3, 1.2])
with col_logo:
    st.image("https://via.placeholder.com/100x100.png?text=Mostacho", width=80)
with col_title:
    st.title("Mostacho Botanas")
    st.caption("Catálogo Virtual y Pedidos")
with col_theme:
    st.write("")
    theme_choice = st.selectbox("Tema", ["Claro", "Oscuro"], index=0 if st.session_state.theme == "Claro" else 1, label_visibility="collapsed")
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

st.write("---")

# 5. Banner Principal
st.markdown(
    '<div class="promo-banner"><span class="material-symbols-outlined">local_fire_department</span> ¡Envíos locales y entregas en ruta! Pide directo por WhatsApp <span class="material-symbols-outlined">local_fire_department</span></div>', 
    unsafe_allow_html=True
)

# 6. Carrusel / Slideshow Publicitario (Automático)
st.markdown("""
<div class="slideshow-container">
    <div class="slide" style="background-image: url('https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=800');">
        <div class="slide-text">Pistaches frescos y tostados con sal de mar</div>
    </div>
    <div class="slide" style="background-image: url('https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800');">
        <div class="slide-text">Mix botanero ideal para compartir en reuniones</div>
    </div>
    <div class="slide" style="background-image: url('https://images.unsplash.com/photo-1508061252966-173859db501d?w=800');">
        <div class="slide-text">Calidad premium garantizada en cada presentación</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- PANEL DE ADMINISTRACIÓN (Editor Directo) ---
with st.expander("Administrar Productos (Editor Directo)"):
    st.write("Modifica los datos directamente en la tabla (precios, nombres, descripciones, imágenes):")
    df_current = pd.DataFrame(st.session_state.products)
    
    edited_df = st.data_editor(
        df_current,
        num_rows="dynamic",
        use_container_width=True,
        key="product_table_editor"
    )
    
    if st.button("Guardar Cambios en el Catálogo"):
        st.session_state.products = edited_df.to_dict(orient="records")
        st.success("¡Catálogo actualizado correctamente!")
        st.rerun()

# 7. Barra de Búsqueda y Botón flotante de Carrito (si hay productos seleccionados)
total_items = sum(st.session_state.cart.values())

col_search, col_cart_btn = st.columns([3, 1])
with col_search:
    search_query = st.text_input("Buscar productos...", placeholder="Escribe el nombre de la botana...", label_visibility="collapsed")
with col_cart_btn:
    if total_items > 0:
        if st.button(f"Ver Carrito ({total_items})", type="primary", use_container_width=True):
            st.toast("Abre la barra lateral para completar tu pedido", icon="🛒")

# 8. Categorías con diseño One UI
categories = ["Chicos", "Para compartir", "Detalles"]
selected_category = st.radio("Categorías", categories, horizontal=True)

st.write("---")

# 9. Listado de Productos
try:
    current_products_list = st.session_state.products
    filtered_products = [
        p for p in current_products_list 
        if isinstance(p, dict) and p.get("category") == selected_category and (search_query.lower() in str(p.get("name", "")).lower() or search_query.lower() in str(p.get("description", "")).lower())
    ]
except Exception:
    filtered_products = []

if not filtered_products:
    st.info("No se encontraron productos en esta categoría con el filtro actual.")
else:
    for product in filtered_products:
        pid = product.get("id")
        col_img, col_info, col_action = st.columns([1, 3, 1])
        
        with col_img:
            st.image(product.get("image", "https://via.placeholder.com/300"), use_container_width=True)
            
        with col_info:
            st.markdown(f'<div class="product-title">{product.get("name")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="product-desc">{product.get("description")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="product-price">${float(product.get("price", 0)):.2f} MXN</div>', unsafe_allow_html=True)
            
        with col_action:
            qty_in_cart = st.session_state.cart.get(pid, 0)
            if qty_in_cart == 0:
                if st.button("Agregar", key=f"add_{pid}"):
                    add_to_cart(pid)
                    st.rerun()
            else:
                c1, c2, c3 = st.columns([1, 1, 1])
                with c1:
                    if st.button("-", key=f"minus_{pid}"):
                        remove_from_cart(pid)
                        st.rerun()
                with c2:
                    st.markdown(f"**{qty_in_cart}**")
                with c3:
                    if st.button("+", key=f"plus_{pid}"):
                        add_to_cart(pid)
                        st.rerun()

# 10. Sidebar / Ticket de Compra (Permanente pero cerrado al iniciar)
with st.sidebar:
    st.markdown('### <span class="material-symbols-outlined">shopping_cart</span> Mi Carrito / Ticket', unsafe_allow_html=True)
    st.caption(f"Artículos seleccionados: {total_items}")
    
    if not st.session_state.cart:
        st.write("El carrito está vacío. Agrega productos para ver tu ticket aquí.")
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
                    st.write(f"**{p.get('name')}**")
                    st.caption(f"{qty} x ${float(p.get('price', 0)):.2f} = ${subtotal:.2f}")
                with col_c2:
                    if st.button("X", key=f"del_cart_{item_id}"):
                        del st.session_state.cart[item_id]
                        st.rerun()
                        
        st.write("---")
        st.markdown(f"### Total a Pagar: **${total_price:.2f} MXN**")
        
        st.subheader("Datos de Entrega")
        customer_name = st.text_input("Nombre del cliente", placeholder="Ej. Juan Pérez")
        customer_address = st.text_area("Dirección / Referencias", placeholder="Calle, número, colonia...")
        customer_notes = st.text_input("Notas adicionales", placeholder="Ej. Cambio de $500")
        
        msg_header = "NUEVO PEDIDO - MOSTACHO BOTANAS\n\n"
        msg_items = "Detalle:\n" + "\n".join(order_summary) + "\n\n"
        msg_total = f"Total: ${total_price:.2f} MXN\n\n"
        msg_customer = f"Cliente: {customer_name if customer_name else 'No especificado'}\n"
        msg_address = f"Dirección: {customer_address if customer_address else 'No especificada'}\n"
        msg_notes = f"Notas: {customer_notes}\n" if customer_notes else ""
        
        full_message = msg_header + msg_items + msg_total + msg_customer + msg_address + msg_notes
        encoded_message = urllib.parse.quote(full_message)
        whatsapp_url = f"https://wa.me/{WHATSAPP_PHONE}?text={encoded_message}"
        
        if customer_name and customer_address:
            st.link_button("Enviar Pedido por WhatsApp", whatsapp_url, use_container_width=True, type="primary")
        else:
            st.warning("Escribe tu Nombre y Dirección para habilitar el envío por WhatsApp.")