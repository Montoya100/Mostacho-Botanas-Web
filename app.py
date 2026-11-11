import streamlit as st
import pandas as pd
import urllib.parse

# 1. Configuración de la página
st.set_page_config(
    page_title="Mostacho Botanas Web",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Inicializar Estado
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

# 3. Estilos CSS adaptativos con Naranja Suave y Contornos Limpios
is_dark = st.session_state.theme == "Oscuro"
bg_color = "#121212" if is_dark else "#ffffff"
card_bg = "#1e1e1e" if is_dark else "#ffffff"
text_color = "#e0e0e0" if is_dark else "#2d3748"
border_color = "#333333" if is_dark else "#e2e8f0"
accent_color = "#f6ad55" if is_dark else "#dd6b20" # Naranja más sutil y elegante

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
        font-size: 20px;
        vertical-align: middle;
    }}
    /* Tarjetas Minimalistas solo con Contorno Sutil */
    .product-card {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }}
    .product-title {{
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 4px;
        color: {text_color};
    }}
    .product-desc {{
        font-size: 0.85rem;
        color: #718096;
        margin-bottom: 8px;
    }}
    .product-price {{
        font-size: 1rem;
        font-weight: bold;
        color: {accent_color};
    }}
    .promo-banner {{
        background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        color: white;
        padding: 14px;
        border-radius: 14px;
        text-align: center;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 16px;
    }}
    
    /* Carrusel / Slideshow Publicitario */
    .slideshow-container {{
        position: relative;
        max-width: 100%;
        height: 160px;
        margin-bottom: 20px;
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid {border_color};
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
        padding: 14px;
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
        background: rgba(0, 0, 0, 0.65);
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
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

# 4. Header & Selector de Tema Compacto en la esquina superior derecha
col_logo, col_title, col_theme = st.columns([1, 4, 1.2])
with col_logo:
    st.image("https://via.placeholder.com/100x100.png?text=Mostacho", width=70)
with col_title:
    st.title("Mostacho Botanas")
    st.caption("Catálogo y Pedidos Directos")
with col_theme:
    # Selector de tema limpio y minimalista en la esquina
    theme_choice = st.selectbox("Modo", ["Claro", "Oscuro"], index=0 if st.session_state.theme == "Claro" else 1, label_visibility="collapsed")
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

st.write("---")

# 5. Banner de Promociones
st.markdown(
    '<div class="promo-banner"><span class="material-symbols-outlined">local_fire_department</span> ¡Envíos locales y entregas en ruta! Pide directo por WhatsApp</div>', 
    unsafe_allow_html=True
)

# 6. Carrusel / Slideshow Publicitario
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

# --- PANEL DE ADMINISTRACIÓN PROTEGIDO CON CONTRASEÑA ---
with st.expander("Panel de Administración (Solo Propietario)"):
    admin_pass = st.text_input("Contraseña de Administrador", type="password", placeholder="Ingresa tu clave...")
    if admin_pass == "1234":  # Puedes cambiar la contraseña aquí si gustas
        st.success("¡Acceso concedido!")
        st.write("Modifica los datos directamente en la tabla:")
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
    elif admin_pass:
        st.error("Contraseña incorrecta.")

# 7. Barra de Búsqueda y Botón de Carrito condicional
total_items = sum(st.session_state.cart.values())

col_search, col_cart_btn = st.columns([3, 1])
with col_search:
    search_query = st.text_input("Buscar productos...", placeholder="Escribe el nombre de la botana...", label_visibility="collapsed")
with col_cart_btn:
    if total_items > 0:
        if st.button(f"Ver Carrito ({total_items})", type="primary", use_container_width=True):
            st.toast("Abre la barra lateral para ver tu ticket y enviar tu pedido", icon="🛒")

# 8. Categorías
categories = ["Chicos", "Para compartir", "Detalles"]
selected_category = st.radio("Categorías", categories, horizontal=True)

st.write("---")

# 9. Listado de Productos con Diseño Outline Limpio
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
        
        # Estructura limpia de tarjeta tipo outline
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

# 10. Sidebar / Ticket de Compra (Cerrado por defecto, se abre limpio)
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