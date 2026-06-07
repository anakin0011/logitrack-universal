# 📊 LogiTrack Universal

**Visualizador inteligente de datos Excel** — carga cualquier archivo `.xlsx` y genera gráficos interactivos al instante, sin configuración previa.

---

## ✨ Características

| Funcionalidad | Detalle |
|---|---|
| 📂 Carga universal | Acepta cualquier archivo `.xlsx`, sin importar su estructura |
| 🔍 Detección automática | Identifica todas las columnas y tipos de datos automáticamente |
| 📈 Gráficos interactivos | Barras, Torta y Línea con Plotly |
| 🗂️ Soporte multi-hoja | Elige entre todas las hojas del libro Excel |
| 📊 KPIs automáticos | Total de filas, columnas detectadas y valores únicos |
| ⬇️ Exportación | Descarga el resumen y los datos en Excel con un clic |
| 🌐 Interfaz en español | Diseño profesional, limpio y totalmente en español |

---

## 🚀 Instalación y uso

### 1. Clonar / ubicarse en el proyecto

```bash
cd C:\Users\anaqu\Proyectos\logitrack-universal
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

La app se abrirá automáticamente en `http://localhost:8501`.

---

## 🗂️ Estructura del proyecto

```
logitrack-universal/
├── app.py              # Aplicación principal Streamlit
├── requirements.txt    # Dependencias Python
└── README.md           # Este archivo
```

---

## 🖥️ Cómo usar la app

1. **Sube tu archivo Excel** desde la barra lateral izquierda.
2. **Selecciona la hoja** si tu archivo tiene múltiples pestañas.
3. **Elige el tipo de gráfico**: Barras, Torta o Línea.
4. **Configura los ejes**:
   - *Eje X*: columna de categorías (p. ej. Producto, Ciudad, Mes).
   - *Valores*: columna numérica a graficar (p. ej. Ventas, Cantidad).
5. Explora los **KPIs automáticos** en la parte superior.
6. Descarga el **resumen en Excel** con el botón de exportación.

---

## 📦 Dependencias

```
streamlit>=1.32.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.0
xlsxwriter>=3.1.0
```

---

## 🛠️ Requisitos del sistema

- Python 3.9 o superior
- Sistema operativo: Windows, macOS o Linux

---

## 📄 Licencia

MIT — libre para uso personal y comercial.

---

*Desarrollado con Streamlit · Plotly · Pandas*
