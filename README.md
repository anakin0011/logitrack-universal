<div align="center">

# 🚚 LogiTrack Universal

### Dashboard logístico inteligente — cargá cualquier Excel de envíos y obtené KPIs, gráficos y análisis con IA en segundos

[![Demo en vivo](https://img.shields.io/badge/▶%20Demo%20en%20vivo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://logitrack-universal-dncy6uzruhxj5zfdbhdz3w.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-52B788?style=for-the-badge)](LICENSE)

---

> **¿Tenés una planilla de envíos y querés entender qué está pasando en 30 segundos?**
> Subí tu archivo, LogiTrack detecta las columnas automáticamente y te arma el dashboard completo — sin configurar nada.

---

<!-- Reemplazá esta línea con un screenshot o GIF de la app -->
![Demo de LogiTrack Universal](https://via.placeholder.com/900x480/FFF3C4/FF8C69?text=Screenshot+pendiente+—+LogiTrack+Universal)

</div>

---

## ✨ Features principales

| | Feature | Descripción |
|---|---|---|
| 📂 | **Carga universal** | Acepta `.xlsx` y `.csv` con cualquier estructura — sin plantilla previa |
| 🔍 | **Detección automática de columnas** | Identifica cadetes, zonas, empresas y estados con matching fuzzy (exacto · parcial · similar) |
| 🧠 | **Detección de encabezado inteligente** | Escanea hasta 6 filas para encontrar dónde empieza la tabla real |
| 📊 | **KPIs instantáneos** | Total de envíos · Pendientes · Entregados — calculados automáticamente |
| 🏆 | **Top 5 con podio** | Ranking visual de los 5 principales por cualquier dimensión |
| 📝 | **Resumen en lenguaje natural** | Texto automático: "María García tiene 142 envíos · 38 pendientes · 104 entregados" |
| 📈 | **4 tipos de gráficos** | Barras verticales · Torta · Línea · Barras horizontales — todos con Plotly interactivo |
| 💬 | **Chat con IA** | Preguntale a tus datos en español usando LLaMA 3.3 70B vía Groq |
| 📷 | **Exportar gráfico PNG** | Descargá el gráfico como imagen de alta resolución |
| 📥 | **Exportar Excel** | Resumen agrupado + datos completos en un solo archivo `.xlsx` |

---

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend / App | [Streamlit](https://streamlit.io) |
| Visualización | [Plotly Express](https://plotly.com/python/plotly-express/) |
| Procesamiento de datos | [Pandas](https://pandas.pydata.org) |
| IA / Chat | [Groq](https://console.groq.com) · LLaMA 3.3 70B Versatile |
| Exportación Excel | [xlsxwriter](https://xlsxwriter.readthedocs.io) · [openpyxl](https://openpyxl.readthedocs.io) |
| Deploy | [Streamlit Community Cloud](https://streamlit.io/cloud) |

---

## 🚀 Instalación y uso local

### 1. Clonar el repositorio

```bash
git clone https://github.com/anakin0011/logitrack-universal.git
cd logitrack-universal
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. (Opcional) Configurar API key para el chat con IA

El chat con IA usa Groq gratuitamente. Obtené tu key en [console.groq.com](https://console.groq.com) y configurala:

```bash
# Windows PowerShell
$env:GROQ_API_KEY = "tu-api-key"

# macOS / Linux
export GROQ_API_KEY="tu-api-key"
```

### 5. Ejecutar

```bash
streamlit run app.py
```

La app se abre automáticamente en `http://localhost:8501`.

---

## 🌐 Demo online

**👉 [logitrack-universal-dncy6uzruhxj5zfdbhdz3w.streamlit.app](https://logitrack-universal-dncy6uzruhxj5zfdbhdz3w.streamlit.app)**

No requiere instalación. Subí tu archivo directamente desde el navegador.

---

## 🏢 Casos de uso — ¿para qué empresas sirve?

LogiTrack Universal fue diseñado para cualquier operación que maneje envíos en planillas Excel o CSV:

| Sector | Caso de uso típico |
|---|---|
| 📦 **Distribuidoras y courier** | Ver qué cadetes tienen más envíos pendientes y en qué zonas se acumula la demora |
| 🛒 **E-commerce** | Monitorear estados de pedidos por empresa de transporte o región |
| 🏭 **Logística industrial** | Comparar rendimiento de rutas y analizar concentración de entregas |
| 🏪 **Pymes con reparto propio** | Tener un dashboard operativo sin pagar licencias de BI caras |
| 📊 **Analistas de datos** | Explorar rápidamente un archivo nuevo sin escribir código |

> Si tu equipo usa Excel para registrar envíos y necesita visualizar esos datos de forma inmediata — LogiTrack es para vos.

---

## 🗂️ Estructura del proyecto

```
logitrack-universal/
├── app.py              # Aplicación principal Streamlit
├── requirements.txt    # Dependencias Python
└── README.md
```

---

## 📦 Dependencias

```
streamlit>=1.32.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.0
xlsxwriter>=3.1.0
groq>=0.4.0          # opcional — para activar el chat con IA
kaleido>=0.2.1        # opcional — para exportar gráficos como PNG
```

---

## 🔮 Próximas features

- [ ] 📅 Filtro por rango de fechas
- [ ] 🗺️ Mapa de calor de envíos por zona geográfica
- [ ] 📊 Comparación entre períodos (semana a semana, mes a mes)
- [ ] 🔔 Alertas automáticas por umbral de pendientes
- [ ] 📱 Vista mobile optimizada
- [ ] 🔗 Conexión directa a Google Sheets

---

## 👩‍💻 Autora

**Ayelen Anaquin**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Ayelen%20Anaquin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ayelen-anaquin)

---

<div align="center">

Hecho con ❤️ usando **Streamlit · Plotly · Pandas · Groq**

</div>
