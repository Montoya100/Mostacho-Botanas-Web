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

if "nav_tab" not in st.session_state:
    st.session_state.nav_tab = "Inicio"

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

# 3. Estilos CSS Estilo App Móvil (Inspiración DiDi / One UI)
is_dark = st.session_state.theme == "Oscuro"
bg_color = "#121212" if is_dark else "#fcfcfc"
card_bg = "#1e1e1e" if is_dark else "#ffffff"
text_color = "#e0e0e0" if is_dark else "#222222"
border_color = "#2c2c2c" if is_dark else "#eaeaea"
accent_color = "#ff5722" if is_dark else "#ff6600" # Naranja vibrante característico

st.markdown(f"""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
<style>
    .stApp {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background-color: {bg_color};
        color: {text_color};
        padding-bottom: 70px; /* Espacio para la barra inferior */
    }}
    .material-symbols-outlined {{
        font-family: 'Material Symbols Outlined';
        font-size: 22px;
        vertical-align: middle;
    }}
    /* Tarjetas Minimalistas Contorneadas */
    .product-card {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    .product-title {{
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 4px;
        color: {text_color};
    }}
    .product-desc {{
        font-size: 0.85rem;
        color: #888888;
        margin-bottom: 8px;
    }}
    .product-price {{
        font-size: 1rem;
        font-weight: bold;
        color: {accent_color};
    }}
    .promo-banner {{
        background: linear-gradient(135deg, #ff6600 0%, #ff8533 100%);
        color: white;
        padding: 14px;
        border-radius: 16px;
        text-align: center;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(255,102,0,0.2);
    }}
    
    /* Carrusel / Slideshow Publicitario */
    .slideshow-container {{
        position: relative;
        max-width: 100%;
        height: 160px;
        margin-bottom: 20px;
        border-radius: 16px;
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
        border-radius: 8px;
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

# 4. Header & Selector de Tema Compacto en Esquina Superior
col_logo, col_title, col_theme = st.columns([1, 4, 1.2])
with col_logo:
    st.image("https://via.placeholder.com/100x100.png?text=Mostacho", width=60)
with col_title:
    st.markdown("### Mostacho Botanas")
    st.caption("Pedidos en línea")
with col_theme:
    theme_choice = st.selectbox("Modo", ["Claro", "Oscuro"], index=0 if st.session_state.theme == "Claro" else 1, label_visibility="collapsed")
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

st.write("---")

total_items = sum(st.session_state.cart.values())

# 5. Contenido según la Pestaña Activa de la Barra Inferior
tab = st.session_state.nav_tab

if tab == "Inicio":
    # Banner y Carrusel
    st.markdown(
        '<div class="promo-banner"><span class="material-symbols-outlined" style="vertical-align: sub;">local_fire_department</span> ¡Envíos locales y entregas en ruta! Pide directo por WhatsApp</div>', 
        unsafe_allow_html=True
    )
    
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

    # Buscador de Productos
    search_query = st.text_input("Buscar productos...", placeholder="Busca tu botana favorita...", label_visibility="collapsed")

    # Categorías estilo píldora
    categories = ["Chicos", "Para compartir", "Detalles"]
    selected_category = st.radio("Categorías", categories, horizontal=True)

    st.write("---")

    # Listado de Productos
    try:
        current_products_list = st.session_state.products
        filtered_products = [
            p for p in current_products_list 
            if isinstance(p, dict) and p.get("category") == selected_category and (search_query.lower() in str(p.get("name", "")).lower() or search_query.lower() in str(p.get("description", "")).lower())
        ]
    except Exception:
        filtered_products = []

    if not filtered_products:
        st.info("No se encontraron productos con el filtro actual.")
    else:
        for product in filtered_products:
            pid = product.get("id")
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

elif tab == "Carrito":
    st.markdown("### <span class='material-symbols-outlined'>shopping_cart</span> Tu Carrito de Compras", unsafe_allow_html=True)
    st.caption(f"Artículos seleccionados: {total_items}")
    
    if not st.session_state.cart:
        st.info("Tu carrito está vacío. Explora el inicio para agregar botanas.")
        if st.button("Ir al Catálogo"):
            st.session_state.nav_tab = "Inicio"
            st.rerun()
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
                    if st.button("Eliminar", key=f"del_cart_{item_id}"):
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

elif tab == "Pedidos":
    st.markdown("### <span class='material-symbols-outlined'>receipt_long</span> Mis Pedidos y Estado", unsafe_allow_html=True)
    st.info("Aquí puedes consultar el estatus de tus pedidos recientes en ruta o envíos locales.")
    st.write("¡Haz tus pedidos directamente desde el catálogo y recíbelos en la puerta de tu casa o negocio!")
    if st.button("Hacer un nuevo pedido"):
        st.session_state.nav_tab = "Inicio"
        st.rerun()

elif tab == "Admin":
    st.markdown("### <span class='material-symbols-outlined'>settings</span> Panel de Administración", unsafe_allow_html=True)
    admin_pass = st.text_input("Contraseña de Administrador", type="password", placeholder="Ingresa tu clave...")
    if admin_pass == "1234":
        st.success("¡Acceso concedido!")
        st.write("Modifica los datos de los productos directamente en la tabla:")
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

# 6. Barra de Navegación Inferior Estilo App (DiDi / Móvil)
st.markdown("""
<style>
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: """ + ("#1e1e1e" if is_dark else "#ffffff") + """;
        border-top: 1px solid """ + border_color + """;
        display: flex;
        justify-content: space-around;
        padding: 8px 0;
        z-index: 99999;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Botones de navegación inferior simulados con columnas de Streamlit en un contenedor fijo inferior
st.write("")
st.write("")
st.write("---")
cols_nav = st.columns(4)

with cols_nav[0]:
    if st.button("🏠 Inicio", use_container_width=True):
        st.session_state.nav_tab = "Inicio"
        st.rerun()
with cols_nav[1]:
    cart_label = f"🛒 Carrito ({total_items})" if total_items > 0 else "🛒 Carrito"
    if st.button(cart_label, use_container_width=True):
        st.session_state.nav_tab = "Carrito"
        st.rerun()
with cols_nav[2]:
    if st.button("📦 Pedidos", use_container_width=True):
        st.session_state.nav_tab = "Pedidos"
        st.rerun()
with cols_nav[3]:
    if st.button("⚙️ Admin", use_container_width=True):
        st.session_state.nav_tab = "Admin"
        st.rerun()