import json
import os
import urllib.parse
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Mostacho Botanas - Catálogo y Pedidos",
    page_icon="🥜",
    layout="wide",
)

# ---------------------------------------------------------
# CSS Personalizado (Para ensanchar el diálogo de edición y estilos)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    /* Estilo para ensanchar las ventanas modales (st.dialog) en Streamlit */
    div[data-baseweb="modal"] > div {
        width: 85vw !important;
        max-width: 1200px !important;
    }
    .main-title {
        text-align: center;
        color: #D35400;
        font-weight: bold;
    }
    .sub-title {
        text-align: center;
        color: #7F8C8D;
        margin-bottom: 30px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Archivo local para persistencia simple de productos
DATA_FILE = "productos_mostacho.json"

# Datos iniciales por defecto si no existe el archivo
DEFAULT_PRODUCTS = [
    {
        "id": "1",
        "nombre": "Semilla Tostada",
        "categoria": "Empacado Individual",
        "precio": 6.50,
        "imagen": "assets/producto_01.png",
    },
    {
        "id": "2",
        "nombre": "Semilla Enchilada",
        "categoria": "Empacado Individual",
        "precio": 6.50,
        "imagen": "assets/producto_02.png",
    },
    {
        "id": "3",
        "nombre": "Semilla Frita Limón",
        "categoria": "Empacado Individual",
        "precio": 6.50,
        "imagen": "assets/producto_03.png",
    },
    {
        "id": "4",
        "nombre": "Cacahuate Crujiente",
        "categoria": "Empacado Individual",
        "precio": 6.50,
        "imagen": "assets/producto_04.png",
    },
    {
        "id": "5",
        "nombre": "Cartucho Mostacho",
        "categoria": "Empacado Individual",
        "precio": 20.50,
        "imagen": "assets/producto_05.png",
    },
    {
        "id": "6",
        "nombre": "Pistache Grande Sal",
        "categoria": "Granel / Mayoreo",
        "precio": 30.30,
        "imagen": "assets/producto_06.png",
    },
    {
        "id": "7",
        "nombre": "Pistache Grande Ajillo",
        "categoria": "Granel / Mayoreo",
        "precio": 30.30,
        "imagen": "assets/producto_07.png",
    },
    {
        "id": "8",
        "nombre": "Costalito Girasol Sal",
        "categoria": "Empacado Individual",
        "precio": 10.00,
        "imagen": "assets/producto_08.png",
    },
]


def cargar_productos():
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return DEFAULT_PRODUCTS
  return DEFAULT_PRODUCTS


def guardar_productos(productos):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(productos, f, ensure_ascii=False, indent=4)


# Inicializar estado
if "productos" not in st.session_state:
  st.session_state.productos = cargar_productos()

if "carrito" not in st.session_state:
  st.session_state.carrito = {}  # {id_producto: cantidad}

# ---------------------------------------------------------
# DIÁLOGO DE EDICIÓN (Más ancho y con IDs ocultos por defecto)
# ---------------------------------------------------------


@st.dialog("🛠️ Administrador y Editor de Catálogo")
def modal_editor():
  st.write(
      "Modifica precios, nombres o categorías directamente en la tabla."
      " (Los ID se ocultan por espacio, pero se gestionan de forma interna)."
  )

  df_actual = pd.DataFrame(st.session_state.productos)

  # Ocultar la columna 'id' de la vista de edición para ganar espacio visual
  columnas_config = {
      "id": None,  # Esto oculta la columna ID en st.data_editor
      "nombre": st.column_config.TextColumn("Nombre del Producto", required=True),
      "categoria": st.column_config.SelectboxColumn(
          "Categoría",
          options=["Empacado Individual", "Granel / Mayoreo", "Especiales"],
          required=True,
      ),
      "precio": st.column_config.NumberColumn(
          "Precio ($)", min_value=0.0, format="$%.2f", required=True
      ),
      "imagen": st.column_config.TextColumn("Ruta de Imagen (assets/...)"),
  }

  df_editado = st.data_editor(
      df_actual,
      column_config=columnas_config,
      hide_index=True,
      use_container_width=True,
      num_rows="dynamic",
      key="editor_tabla_productos",
  )

  col1, col2 = st.columns([1, 1])
  with col1:
    if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
      # Reconstruir lista manteniendo o asignando IDs nuevos si se agregaron filas
      nueva_lista = []
      for idx, row in df_editado.iterrows():
        # Si no tenía ID por ser fila nueva, generar uno único
        prod_id = (
            str(row.get("id"))
            if pd.notna(row.get("id")) and str(row.get("id")).strip() != ""
            else str(len(nueva_lista) + 101)
        )
        nueva_lista.append({
            "id": prod_id,
            "nombre": str(row["nombre"]),
            "categoria": str(row["categoria"]),
            "precio": float(row["precio"]),
            "imagen": (
                str(row["imagen"])
                if pd.notna(row["imagen"])
                else "assets/producto_01.png"
            ),
        })
      st.session_state.productos = nueva_lista
      guardar_productos(nueva_lista)
      st.success("¡Catálogo actualizado y guardado exitosamente!")
      st.rerun()

  with col2:
    if st.button("Cerrar", use_container_width=True):
      st.rerun()


# ---------------------------------------------------------
# INTERFAZ PRINCIPAL
# ---------------------------------------------------------
st.markdown(
    "<h1 class='main-title'>.::: Mostacho Botanas :::.</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='sub-title'>!Una probadita casera..! — Catálogo y Pedidos en"
    " Ruta</p>",
    unsafe_allow_html=True,
)

# Barra superior de acciones
col_top1, col_top2 = st.columns([6, 1])
with col_top2:
  if st.button("⚙️ Editar Catálogo", use_container_width=True):
    modal_editor()

# Sidebar: Carrito de Compras
st.sidebar.title("🛒 Pedido Actual")

if not st.session_state.carrito:
  st.sidebar.info("El carrito está vacío. Selecciona productos del catálogo.")
else:
  total_general = 0
  items_carrito_texto = []

  for prod_id, cantidad in list(st.session_state.carrito.items()):
    # Buscar producto
    producto = next(
        (p for p in st.session_state.productos if p["id"] == prod_id), None
    )
    if producto:
      subtotal = producto["precio"] * cantidad
      total_general += subtotal

      c1, c2, c3 = st.sidebar.columns([3, 2, 1])
      c1.write(f"**{producto['nombre']}**")
      c2.write(f"${subtotal:.2f}")

      # Botones de control de cantidad
      sub_col1, sub_col2 = c3.columns(2)
      if sub_col1.button("➕", key=f"mas_{prod_id}"):
        st.session_state.carrito[prod_id] += 1
        st.rerun()
      if sub_col2.button("➖", key=f"menos_{prod_id}"):
        st.session_state.carrito[prod_id] -= 1
        if st.session_state.carrito[prod_id] <= 0:
          del st.session_state.carrito[prod_id]
        st.rerun()

      items_carrito_texto.append(
          f"- {cantidad}x {producto['nombre']} (${subtotal:.2f})"
      )

  st.sidebar.markdown("---")
  st.sidebar.markdown(f"### Total: ${total_general:.2f}")

  # Campo para el número de teléfono o nota del cliente de ruta
  nombre_cliente = st.sidebar.text_input(
      "Cliente / Establecimiento", placeholder="Ej. Miscelánea Los Arcos"
  )

  # Botón de WhatsApp con el texto exacto solicitado
  mensaje_wa = f"Hola, nuevo pedido de *Mostacho Botanas*:\n\nCliente: {nombre_cliente or 'General'}\n"
  mensaje_wa += "\n".join(items_carrito_texto)
  mensaje_wa += f"\n\n*Total a Pagar: ${total_general:.2f}*"

  whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(mensaje_wa)}"

  st.sidebar.markdown(
      f'<a href="{whatsapp_url}" target="_blank"><button'
      ' style="width:100%; background-color:#25D366; color:white; border:none;'
      " padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;'>"
      "Enviar pedido por WhatsApp</button></a>",
      unsafe_allow_html=True,
  )

  if st.sidebar.button("🧹 Vaciar Carrito", use_container_width=True):
    st.session_state.carrito = {}
    st.rerun()

# ---------------------------------------------------------
# CUERPO PRINCIPAL: FILTROS Y TARJETAS DE PRODUCTOS
# ---------------------------------------------------------
categorias_disponibles = ["Todos"] + list(
    set(p["categoria"] for p in st.session_state.productos)
)
categoria_seleccionada = st.selectbox(
    "Filtrar por categoría:", categorias_disponibles
)

busqueda = st.text_input(
    "🔍 Buscar producto por nombre...", placeholder="Ej. Semilla, Cacahuate..."
)

# Filtrado
productos_filtrados = st.session_state.productos
if categoria_seleccionada != "Todos":
  productos_filtrados = [
      p for p in productos_filtrados if p["categoria"] == categoria_seleccionada
  ]

if busqueda:
  productos_filtrados = [
      p
      for p in productos_filtrados
      if busqueda.lower() in p["nombre"].lower()
  ]

# Renderizado en Grid de columnas (3 columnas)
cols = st.columns(3)
for index, producto in enumerate(productos_filtrados):
  col = cols[index % 3]
  with col:
    with st.container(border=True):
      st.markdown(f"### {producto['nombre']}")
      st.caption(f"Categoría: {producto['categoria']}")

      # Mostrar imagen si existe, sino icono por defecto
      if os.path.exists(producto["imagen"]):
        st.image(producto["imagen"], use_container_width=True)
      else:
        st.info("🥜 Imagen no disponible localmente")

      st.markdown(f"**Precio:** ${producto['precio']:.2f}")

      # Botón para agregar al carrito
      if st.button(
          f"Agregar 🛒",
          key=f"add_{producto['id']}_{index}",
          use_container_width=True,
      ):
        if producto["id"] in st.session_state.carrito:
          st.session_state.carrito[producto["id"]] += 1
        else:
          st.session_state.carrito[producto["id"]] = 1
        st.success(f"¡Agregado: {producto['nombre']}!")
        st.rerun()