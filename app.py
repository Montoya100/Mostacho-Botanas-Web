import streamlit as st
import urllib.parse

# 1. Configuración de la página
st.set_page_config(
    page_title="Mostacho Botanas Web",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Estilos CSS personalizados (Modo Claro con acento Naranja y Modo Oscuro)
st.markdown("""
<style>
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .product-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .product-desc {
        font-size: 0.88rem;
        color: #666666;
        margin-bottom: 8px;
    }
    .product-price {
        font-size: 1.05rem;
        font-weight: bold;
        color: #FF8C00;
    }
    .promo-banner {
        background: linear-gradient(135deg, #FF8C00 0%, #FFA500 100%);
        color: white;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 20px;
    }
    .stButton>button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Inicializar el Carrito y la Lista de Productos en Session State (para que se guarden al editar)
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

# Número de WhatsApp (modifica con tu número a 10 dígitos con código de país, ej: 52...)
WHATSAPP_PHONE = "522380000000"

# Funciones de carrito
def add_to_cart(product_id):
    st.session_state.cart[product_id] = st.session_state.cart.get(product_id, 0) + 1

def remove_from_cart(product_id):
    if product_id in st.session_state.cart:
        if st.session_state.cart[product_id] > 1:
            st.session_state.cart[product_id] -= 1
        else:
            del st.session_state.cart[product_id]

# 4. Encabezado (Logo y Título)
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("https://via.placeholder.com/100x100.png?text=Mostacho", width=100)
with col_title:
    st.title("Mostacho Botanas Web")
    st.caption("Catálogo Virtual y Pedidos en Línea")

# 5. Banner de Promociones (Estilo Historias/Anuncio)
st.markdown(
    '<div class="promo-banner">🔥 ¡Envíos locales o entrega rápida en ruta! Haz tu pedido directo por WhatsApp 🔥</div>', 
    unsafe_allow_html=True
)

# --- PANEL DE ADMINISTRACIÓN BÁSICO (OCULTO EN UN EXPANDER) ---
with st.expander("⚙️ Panel de Administración de Productos (Editar / Agregar)"):
    st.subheader("Modificar productos existentes")
    
    # Selector de producto a editar
    prod_names = [p["name"] for p in st.session_state.products]
    selected_to_edit = st.selectbox("Selecciona un producto para editar", prod_names)
    
    # Encontrar el producto seleccionado
    p_idx = next(i for i, p in enumerate(st.session_state.products) if p["name"] == selected_to_edit)
    current_p = st.session_state.products[p_idx]
    
    with st.form(key="edit_form"):
        new_name = st.text_input("Nombre del producto", value=current_p["name"])
        new_cat = st.selectbox("Categoría", ["Chicos", "Para compartir", "Detalles"], index=["Chicos", "Para compartir", "Detalles"].index(current_p["category"]))
        new_price = st.number_input("Precio ($ MXN)", value=float(current_p["price"]), min_value=0.0)
        new_desc = st.text_area("Descripción", value=current_p["description"])
        new_img = st.text_input("URL de la Imagen", value=current_p["image"])
        
        save_btn = st.form_submit_button("Guardar Cambios")
        if save_btn:
            st.session_state.products[p_idx] = {
                "id": current_p["id"],
                "name": new_name,
                "category": new_cat,
                "price": new_price,
                "description": new_desc,
                "image": new_img
            }
            st.success("¡Producto actualizado correctamente!")
            st.rerun()

    st.markdown("---")
    st.subheader("Agregar nuevo producto")
    with st.form(key="add_form"):
        add_name = st.text_input("Nombre del nuevo producto")
        add_cat = st.selectbox("Categoría del nuevo", ["Chicos", "Para compartir", "Detalles"], key="add_cat")
        add_price = st.number_input("Precio ($ MXN)", min_value=0.0, key="add_price")
        add_desc = st.text_area("Descripción del nuevo", key="add_desc")
        add_img = st.text_input("URL de la Imagen", key="add_img", placeholder="https://...")
        
        add_btn = st.form_submit_button("Agregar al Catálogo")
        if add_btn and add_name:
            new_id = max([p["id"] for p in st.session_state.products]) + 1 if st.session_state.products else 1
            st.session_state.products.append({
                "id": new_id,
                "name": add_name,
                "category": add_cat,
                "price": add_price,
                "description": add_desc,
                "image": add_img if add_img else "https://via.placeholder.com/300"
            })
            st.success("¡Producto agregado con éxito!")
            st.rerun()

# 6. Barra de Búsqueda
search_query = st.text_input("🔍 Buscar productos...", placeholder="Escribe el nombre o ingrediente de la botana...")

# 7. Categorías (Tipo pestañas horizontales)
categories = ["Chicos", "Para compartir", "Detalles"]
selected_category = st.radio("Categorías", categories, horizontal=True)

st.write("---")

# 8. Listado de Productos Filtrados
filtered_products = [
    p for p in st.session_state.products 
    if p["category"] == selected_category and (search_query.lower() in p["name"].lower() or search_query.lower() in p["description"].lower())
]

if not filtered_products:
    st.info("No se encontraron productos en esta categoría con el filtro actual.")
else:
    for product in filtered_products:
        pid = product["id"]
        col_img, col_info, col_action = st.columns([1, 3, 1])
        
        with col_img:
            st.image(product["image"], use_container_width=True)
            
        with col_info:
            st.markdown(f'<div class="product-title">{product["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="product-desc">{product["description"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="product-price">${product["price"]:.2f} MXN</div>', unsafe_allow_html=True)
            
        with col_action:
            qty_in_cart = st.session_state.cart.get(pid, 0)
            if qty_in_cart == 0:
                if st.button("➕ Agregar", key=f"add_{pid}"):
                    add_to_cart(pid)
                    st.rerun()
            else:
                c1, c2, c3 = st.columns([1, 1, 1])
                with c1:
                    if st.button("➖", key=f"minus_{pid}"):
                        remove_from_cart(pid)
                        st.rerun()
                with c2:
                    st.markdown(f"**{qty_in_cart}**")
                with c3:
                    if st.button("➕", key=f"plus_{pid}"):
                        add_to_cart(pid)
                        st.rerun()

# 9. Barra Lateral (Carrito / Ticket de Compra y Datos de Envío)
with st.sidebar:
    st.header("🛒 Mi Carrito / Ticket")
    
    total_items = sum(st.session_state.cart.values())
    st.caption(f"Artículos seleccionados: {total_items}")
    
    if not st.session_state.cart:
        st.write("El carrito está vacío.")
    else:
        total_price = 0.0
        order_summary = []
        
        st.write("---")
        for item_id, qty in list(st.session_state.cart.items()):
            p = next((item for item in st.session_state.products if item["id"] == item_id), None)
            if p:
                subtotal = p["price"] * qty
                total_price += subtotal
                order_summary.append(f"• {qty}x {p['name']} - ${subtotal:.2f}")
                
                col_c1, col_c2 = st.columns([3, 1])
                with col_c1:
                    st.write(f"**{p['name']}**")
                    st.caption(f"{qty} x ${p['price']:.2f} = ${subtotal:.2f}")
                with col_c2:
                    if st.button("🗑️", key=f"del_cart_{item_id}"):
                        del st.session_state.cart[item_id]
                        st.rerun()
                        
        st.write("---")
        st.markdown(f"### Total a Pagar: **${total_price:.2f} MXN**")
        
        # Datos del cliente para el pedido por WhatsApp
        st.subheader("Datos de Entrega")
        customer_name = st.text_input("Nombre del cliente", placeholder="Ej. Juan Pérez")
        customer_address = st.text_area("Dirección / Referencias", placeholder="Calle, número, colonia...")
        customer_notes = st.text_input("Notas adicionales", placeholder="Ej. Cambio de $500")
        
        # Generar mensaje automático de WhatsApp
        msg_header = "📌 *NUEVO PEDIDO - MOSTACHO BOTANAS*\n\n"
        msg_items = "*Detalle:*\n" + "\n".join(order_summary) + "\n\n"
        msg_total = f"*Total:* ${total_price:.2f} MXN\n\n"
        msg_customer = f"*Cliente:* {customer_name if customer_name else 'No especificado'}\n"
        msg_address = f"*Dirección:* {customer_address if customer_address else 'No especificada'}\n"
        msg_notes = f"*Notas:* {customer_notes}\n" if customer_notes else ""
        
        full_message = msg_header + msg_items + msg_total + msg_customer + msg_address + msg_notes
        encoded_message = urllib.parse.quote(full_message)
        whatsapp_url = f"https://wa.me/{WHATSAPP_PHONE}?text={encoded_message}"
        
        if customer_name and customer_address:
            st.link_button("📲 Enviar Pedido por WhatsApp", whatsapp_url, use_container_width=True, type="primary")
        else:
            st.warning("Escribe tu Nombre y Dirección para habilitar el envío por WhatsApp.")