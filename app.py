import streamlit as st
import requests # ¡La librería clave para APIs!
import io
from PIL import Image

# --- 1. CONFIGURACIÓN (Pega tus claves aquí) ---
# Copia y pega desde la ventana "Prediction URL" de Azure

# Usa st.secrets:
PREDICTION_ENDPOINT = st.secrets["azure"]["endpoint"]
PREDICTION_KEY = st.secrets["azure"]["key"]


# Configura los "headers" (la contraseña) para la API
headers = {
    'Prediction-Key': PREDICTION_KEY,
    'Content-Type': 'application/octet-stream' # Esto significa que enviaremos la imagen en bytes
}

# --- 2. FUNCIÓN DE PREDICCIÓN (La Magia) ---
# Esta función toma la imagen, la envía a Azure y devuelve la respuesta
def predict_image(image_pil):
    # Convertir la imagen de PIL a bytes
    img_byte_arr = io.BytesIO()
    image_pil.save(img_byte_arr, format='JPEG') # Convertimos a JPEG en memoria
    image_bytes = img_byte_arr.getvalue()
    
    try:
        # Enviar la petición POST a la API de Azure
        response = requests.post(PREDICTION_ENDPOINT, headers=headers, data=image_bytes)
        
        # Asegurarse de que la petición fue exitosa
        response.raise_for_status() 
        
        # Devolver el resultado (en formato JSON)
        return response.json()
        
    except Exception as e:
        st.error(f"Error al conectar con la API de Azure: {e}")
        return None

# --- 3. INTERFAZ DE STREAMLIT (La misma de antes) ---
st.set_page_config(page_title="Clasificador de Tueste (Coffe)", layout="wide")
st.title("🤖 Clasificador de Tueste de Café 👁️")
st.write("Sube una foto o usa tu cámara para clasificar el nivel de tueste.")

# Cargar la imagen
st.sidebar.header("Elige tu Imagen")
img_file_buffer = st.sidebar.file_uploader("Sube una imagen:", type=["jpg", "png", "jpeg"])
st.sidebar.write("--- O ---")
camera_buffer = st.sidebar.camera_input("Toma una foto:")

image_pil = None

if img_file_buffer is not None:
    image_pil = Image.open(img_file_buffer)
    st.sidebar.success("Imagen cargada.")
elif camera_buffer is not None:
    image_pil = Image.open(camera_buffer)
    st.sidebar.success("Foto capturada.")

# --- 4. PROCESAMIENTO Y PREDICCIÓN ---
if image_pil is not None:
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Imagen a Clasificar")
        st.image(image_pil, caption="Imagen de entrada", use_container_width=True)
    
    # ¡Llamamos a nuestra nueva función de API!
    with st.spinner('Enviando para clasificar...'):
        prediction_data = predict_image(image_pil)
    
    with col2:
        st.header("Resultado de la Clasificación")
        
        if prediction_data:
            # El JSON de Azure se ve así:
            # { "predictions": [ {"tagName": "MEDIO", "probability": 0.99}, ... ] }
            
            # Obtener la predicción principal
            top_prediction = prediction_data['predictions'][0]
            
            predicted_class = top_prediction['tagName']
            confidence = top_prediction['probability'] * 100
            
            st.success(f"**Predicción: {predicted_class}**")
            st.info(f"**Confianza: {confidence:.2f}%**")
            
            st.subheader("Confianza por Clase:")
            # Formatear todos los resultados para el gráfico de barras
            prob_dict = {pred['tagName']: pred['probability'] for pred in prediction_data['predictions']}
            st.bar_chart(prob_dict)
        else:
            st.error("No se pudo obtener la predicción.")

else:
    st.info("Por favor, sube una imagen o toma una foto para iniciar.")