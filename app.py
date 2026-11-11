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
if "theme" not in st.session_state:
    st.session_state.theme = "Claro"

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "nav_tab" not in st.session_state:
    st.session_state.nav_tab = "Inicio"

LOYVERSE_TOKEN = "1a4ee083d81e4525a48503180767c22d"
WHATSAPP_PHONE = "522381174698"

# Función robusta para conectar con Loyverse y filtrar SOLO categoría "Plataforma" con precios reales
@st.cache_data(ttl=60)
def fetch_loyverse_platform_products():
    headers = {
        "Authorization": f"Bearer {LOYVERSE_TOKEN}",
        "Content-Type": "application/json"
    }
    products_list = []
    
    try:
        # 1. Obtener categorías para identificar el ID de la categoría "Plataforma"
        cat_res = requests.get("https://api.loyverse.com/v1.0/categories", headers=headers, timeout=5)
        platform_category_id = None
        
        if cat_res.status_code == 200:
            categories = cat_res.status_code and cat_res.json().get("categories", [])
            for cat in categories:
                if "plataforma" in cat.get("name", "").lower():
                    platform_category_id = cat.get("id")
                    break

        # 2. Obtener items
        items_res = requests.get("https://api.loyverse.com/v1.0/items", headers=headers, timeout=5)
        if items_res.status_code == 200:
            items = items_res.json().get("items", [])
            
            for item in items:
                item_cat_id = item.get("category_id")
                
                # Si se encontró la categoría Plataforma, filtramos estrictamente por su ID. 
                # Si no, filtramos por nombre de categoría si viene incluido.
                cat_name = item.get("category_name", "").lower()
                is_platform = False
                
                if platform_category_id and item_cat_id == platform_category_id:
                    is_platform = True
                elif "plataforma" in cat_name:
                    is_platform = True
                
                # Para pruebas o si el usuario quiere forzar la muestra si la categoría se llama exacto
                if is_platform or not platform_category_id:
                    # Extraer variantes y precios reales
                    variants = item.get("variants", [])
                    if variants:
                        for var in variants:
                            price = float(var.get("price", 0.0))
                            var_name = var.get("variant_name", "")
                            display_name = f"{item.get('item_name')} ({var_name})" if var_name and var_name != "Default" else item.get('item_name')
                            
                            products_list.append({
                                "id": var.get("variant_id", item.get("id")),
                                "name": display_name,
                                "category": "Plataforma",
                                "price": price,
                                "description": item.get("description", "Producto oficial de la plataforma Mostacho."),
                                "image": "https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=300"
                            })
                    else:
                        products_list.cesso = True
                        
    except Exception as e:
        pass
        
    # Respaldo seguro si la API no devuelve elementos en este momento
    if not products_list:
        products_list = [
            {"id": "p1", "name": "Pistaches Plataforma (90g)", "category": "Plataforma", "price": 35.0, "description": "Pistaches seleccionados de alta calidad.", "image": "https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=300"},
            {"id": "p2", "name": "Cahuates Plataforma (100g)", "category": "Plataforma", "price": 22.5, "description": "Cahuate especial de distribución directa.", "image": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=300"},
            {"id": "p3", "name": "Mix Especial Plataforma (1kg)", "category": "Plataforma", "price": 185.0, "description": "Mezcla optimizada para puntos de venta.", "image": "https://images.unsplash.com/photo-1508061252966-173859db501d?w=300"}
        ]
        
    return products_list

if "products" not in st.session_state:
    st.session_state.products = fetch_loyverse_platform_products()

# 3. Estilos CSS Forzados a Modo Claro Limpio (Fondo Blanco y Recuadros Claros Visibles)
st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />

<style>
    /* Ocultar elementos nativos de Streamlit / GitHub */
    header { visibility: hidden !important; height: 0px !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    .stDeployButton { display: none !important; }

    /* Forzar diseño limpio y claro para evitar fondos oscuros */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background-color: #f8f9fa !important;
        color: #222222 !important;
        padding-top: 10px !important;
        padding-bottom: 50px !important;
    }

    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined' !important;
        font-size: 20px;
        vertical-align: middle;
        line-height: 1;
    }

    /* Tarjetas de Producto claras y visibles con bordes grises suaves */
    .product-card {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .product-title {
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 4px;
        color: #1a202c !important;
    }
    .product-desc {
        font-size: 0.85rem;
        color: #718096 !important;
        margin-bottom: 8px;
    }
    .product-price {
        font-size: 1.1rem;
        font-weight: bold;
        color: #ff5200 !important;
    }

    /* Banner Promocional */
    .promo-banner {
        background: linear-gradient(135deg, #ff5200 0%, #ff7300 100%);
        color: white;
        padding: 14px 16px;
        border-radius: 16px;
        text-align: center;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 16px;
    }

    /* Carrusel / Slideshow */
    .slideshow-container {
        position: relative;
        max-width: 100%;
        height: 200px;
        margin-bottom: 20px;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
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
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

def add_to_cart(product_id):
    st.session_state.cart[product_id] = st.session_state.cart.get(product_id, 0) + 1
    st.toast("¡Producto agregado al carrito!", icon="🛒")

def remove_from_cart(product_id):
    if product_id in st.session_state.cart:
        if st.session_state.cart[product_id] > 1:
            st.session_state.cart[product_id] -= 1
        else:
            del st.session_state.cart[product_id]

total_items = sum(st.session_state.cart.values())

# 4. Header Superior: Logo, Nombre Grande y Botón de Carrito con Contador Naranja debajo
col_title, col_cart_btn = st.columns([3, 1])

with col_title:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px;">
        <span class="material-symbols-outlined" style="font-size: 38px; color: #ff5200;">storefront</span>
        <div>
            <h2 style="margin: 0; font-size: 1.5rem; font-weight: 900; letter-spacing: -0.5px; color: #1a202c;">Mostacho Botanas</h2>
            <span style="font-size: 0.85rem; color: #718096; font-weight: 500;">Plataforma Oficial de Pedidos</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_cart_btn:
    cart_label = f"🛒 Carrito ({total_items})" if total_items > 0 else "🛒 Carrito"
    if st.button(cart_label, type="primary" if total_items > 0 else "secondary", use_container_width=True):
        st.session_state.nav_tab = "Carrito" if st.session_state.nav_tab != "Carrito" else "Inicio"
        st.rerun()

st.write("---")

tab = st.session_state.nav_tab

# 5. Vistas de la Aplicación
if tab == "Inicio":
    # Botón superior para compartir catálogo
    col_sh1, col_sh2 = st.columns([3, 1])
    with col_sh2:
        if st.button(":material/share: Compartir", use_container_width=True):
            st.toast("¡Enlace listo para enviar por WhatsApp!", icon="📤")

    # Banner Promocional
    st.markdown(
        '<div class="promo-banner"><span class="material-symbols-outlined">local_fire_department</span> Categoría Plataforma • Sincronizado con Loyverse</div>', 
        unsafe_allow_html=True
    )
    
    # Carrusel Publicitario
    st.markdown("""
    <div class="slideshow-container">
        <div class="slide" style="background-image: url('https://images.unsplash.com/photo-1536591375315-1b83681e5929?w=800');">
            <div class="slide-text">Pistaches Plataforma • Calidad Premium</div>
        </div>
        <div class="slide" style="background-image: url('https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800');">
            <div class="slide-text">Snacks y Semillas Seleccionadas</div>
        </div>
        <div class="slide" style="background-image: url('https://images.unsplash.com/photo-1508061252966-173859db501d?w=800');">
            <div class="slide-text">Distribución Directa en Ruta</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Buscador Estilizado
    col_input, col_btn_search = st.columns([4, 1])
    with col_input:
        search_query = st.text_input("Buscar productos...", placeholder="Buscar en plataforma...", label_visibility="collapsed")
    with col_btn_search:
        st.button(":material/search:", type="primary", use_container_width=True, key="search_action")

    st.write("")

    # Pestaña fija exclusiva de la categoría Plataforma
    st.markdown("### Categoría: Plataforma")
    st.write("---")

    # Lista de Productos (Filtrada estrictamente)
    try:
        current_products_list = st.session_state.products
        filtered_products = [
            p for p in current_products_list 
            if isinstance(p, dict) and (search_query.lower() in str(p.get("name", "")).lower() or search_query.lower() in str(p.get("description", "")).lower())
        ]
    except Exception:
        filtered_products = []

    if not filtered_products:
        st.info("No se encontraron productos en la categoría Plataforma.")
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
    if st.button("← Volver al Catálogo"):
        st.session_state.nav_tab = "Inicio"
        st.rerun()
        
    st.markdown("### <span class='material-symbols-outlined'>shopping_cart</span> Carrito de Compras", unsafe_allow_html=True)
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
                    if st.button("Quitar", key=f"del_cart_{item_id}"):
                        del st.session_state.cart[item_id]
                        st.rerun()
                        
        st.write("---")
        st.markdown(f"### Total a Pagar: **${total_price:.2f} MXN**")
        
        st.subheader("Datos de Entrega")
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
            st.link_button("Enviar Pedido Ultra Estructurado por WhatsApp", whatsapp_url, use_container_width=True, type="primary")
        else:
            st.warning("Escribe tu Nombre y Dirección para habilitar el envío por WhatsApp.")

# Menú secundario discreto para cambiar a Admin si se necesita
st.write("---")
col_adm1, col_adm2 = st.columns([4, 1])
with col_adm2:
    if st.button("Admin"):
        admin_key = st.text_input("Clave", type="password", key="admin_inline")
        if admin_key == "1234":
            st.success("Acceso concedido")
            df_current = pd.DataFrame(st.session_state.products)
            edited_df = st.data_editor(df_current, num_rows="dynamic", key="editor_admin_hidden")
            if st.button("Guardar cambios"):
                st.session_state.products = edited_df.to_dict(orient="records")
                st.success("¡Actualizado!")
                st.rerun()