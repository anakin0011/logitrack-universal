"""Design-system tokens and CSS for LogiTrack."""

# ── Color tokens ──────────────────────────────────────────────────────────────
P          = "#185FA5"    # primary blue
P_DARK     = "#0C447C"    # header / sidebar
BG         = "#F4F5F7"    # page background
SURFACE    = "#FFFFFF"    # cards, tables
TEXT       = "#1A1F2B"    # body text
MUTED      = "#5F6672"    # labels, metadata
SUCCESS    = "#3B6D11"
SUCCESS_BG = "#EAF3DE"
WARNING    = "#854F0B"
WARNING_BG = "#FAEEDA"
CRITICAL   = "#A32D2D"
CRITICAL_BG = "#FCEBEB"
NEUTRAL_BG = "#F0F1F3"

_FONTS = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Inter:wght@400;500;600;700;800"
    "&family=IBM+Plex+Mono:wght@400;500&display=swap');"
)

GLOBAL_CSS = f"""
<style>
{_FONTS}

/* ── Base ─────────────────────────────────────────────────────────────────── */
/* Target content elements only — never override icon fonts */
body, p, div, span, a, li, td, th, label, input, textarea, button, select,
h1, h2, h3, h4, h5, h6, caption, blockquote {{
    font-family: 'Inter', system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
}}
/* Restore Material Icons untouched */
.material-icons, .material-icons-outlined,
.material-icons-round, .material-icons-sharp,
[class*="material-icon"], [class*="MaterialIcon"] {{
    font-family: 'Material Icons', 'Material Icons Outlined' !important;
}}
.stApp {{ background: {BG}; }}
[data-testid="collapsedControl"] {{ display: none !important; }}
.block-container {{ padding-top: 1.5rem !important; max-width: 1100px; }}

/* ── Page header ──────────────────────────────────────────────────────────── */
.lt-header {{
    background: {P_DARK};
    border-radius: 10px;
    padding: 0.7rem 1.2rem;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    flex-wrap: wrap;
}}
.lt-header-brand {{
    font-size: 1.05rem; font-weight: 700;
    color: #FFFFFF; margin: 0; letter-spacing: -0.01em;
}}
.lt-header-meta  {{
    font-size: 0.74rem;
    color: rgba(255,255,255,0.65);
    margin: 0;
}}
.lt-header-badge {{
    margin-left: auto;
    background: rgba(255,255,255,0.15);
    color: #FFFFFF;
    border-radius: 999px;
    padding: 0.18rem 0.75rem;
    font-size: 0.72rem; font-weight: 600;
    white-space: nowrap;
    max-width: 200px;
    overflow: hidden; text-overflow: ellipsis;
}}

/* ── KPI cards ────────────────────────────────────────────────────────────── */
.kpi-card {{
    background: {SURFACE};
    border-radius: 10px;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    border: 1px solid #E4E6EA;
}}
.kpi-label {{
    font-size: 0.7rem; font-weight: 600;
    color: {MUTED};
    text-transform: uppercase; letter-spacing: 0.05em;
    margin: 0 0 0.35rem;
}}
.kpi-value {{
    font-size: 1.8rem; font-weight: 500;
    color: {TEXT}; line-height: 1;
    font-feature-settings: "tnum";
    margin: 0;
}}
.kpi-delta {{
    font-size: 0.72rem; font-weight: 500;
    margin-top: 0.3rem; color: {MUTED};
}}
.kpi-delta.up   {{ color: {SUCCESS}; }}
.kpi-delta.down {{ color: {CRITICAL}; }}

/* ── Section label ────────────────────────────────────────────────────────── */
.section-lbl {{
    font-size: 0.7rem; font-weight: 600;
    letter-spacing: 0.06em; text-transform: uppercase;
    color: {MUTED}; margin: 1.4rem 0 0.5rem;
}}

/* ── Severity badges ──────────────────────────────────────────────────────── */
.badge {{
    display: inline-block;
    border-radius: 4px;
    padding: 0.14rem 0.5rem;
    font-size: 0.7rem; font-weight: 600;
    line-height: 1.4; white-space: nowrap;
}}
.badge-critical {{ background: {CRITICAL_BG}; color: {CRITICAL}; }}
.badge-warning  {{ background: {WARNING_BG};  color: {WARNING};  }}
.badge-success  {{ background: {SUCCESS_BG};  color: {SUCCESS};  }}
.badge-neutral  {{ background: {NEUTRAL_BG};  color: {MUTED};    }}
.badge-info     {{ background: #EBF3FC;        color: {P};        }}

/* ── Tracking IDs ─────────────────────────────────────────────────────────── */
.tracking-id {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem; font-weight: 500;
    color: {P};
    background: #EBF3FC;
    border-radius: 4px;
    padding: 0.1rem 0.4rem;
}}

/* ── Alert / resumen boxes ────────────────────────────────────────────────── */
.alert-box {{
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin: 0.5rem 0;
    font-size: 0.87rem;
    border-left: 4px solid;
    line-height: 1.6;
    color: {TEXT};
}}
.alert-box.critical {{ background: {CRITICAL_BG}; border-color: {CRITICAL}; }}
.alert-box.warning  {{ background: {WARNING_BG};  border-color: {WARNING};  }}
.alert-box.success  {{ background: {SUCCESS_BG};  border-color: {SUCCESS};  }}
.alert-box.info     {{ background: #EBF3FC;        border-color: {P};        }}

.resumen-box {{
    background: #EBF3FC;
    border-left: 4px solid {P};
    border-radius: 0 8px 8px 0;
    padding: 0.85rem 1.1rem;
    margin: 0.5rem 0;
    font-size: 0.87rem;
    color: {TEXT};
    line-height: 1.6;
}}

/* ── Lookup box (Mesa Operativa) ──────────────────────────────────────────── */
.lookup-box {{
    background: {BG};
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
    border-left: 4px solid {P};
}}
.lookup-row {{ font-size: 0.84rem; color: {TEXT}; margin: 0.2rem 0; }}

/* ── Footer ───────────────────────────────────────────────────────────────── */
.app-footer {{
    margin-top: 3rem; padding-top: 1.2rem;
    border-top: 1px solid #E4E6EA;
    text-align: center;
    color: {MUTED}; font-size: 0.78rem;
}}

/* ── Mobile ───────────────────────────────────────────────────────────────── */
@media (max-width: 768px) {{
    .block-container {{
        padding: 0.5rem 0.6rem 5.5rem !important;
        max-width: 100% !important;
    }}
    .kpi-value {{ font-size: 1.4rem; }}
    .lt-header {{ padding: 0.55rem 0.9rem; gap: 0.5rem; }}
    .lt-header-badge {{ margin-left: 0; max-width: calc(100% - 1rem); }}
    .stButton > button, [data-testid="stDownloadButton"] > button {{
        min-height: 48px !important; font-size: 0.88rem !important;
        width: 100% !important;
    }}
    [data-testid="stFileUploadDropzone"] {{ min-height: 100px !important; }}
    div[data-testid="stRadio"] > div {{ flex-wrap: wrap !important; gap: 0.35rem !important; }}
    div[data-testid="stRadio"] label {{ min-height: 44px; display: flex; align-items: center; }}
}}
</style>
"""


def inject_css() -> None:
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def kpi_card(label: str, value, delta: str = "", delta_dir: str = "", accent: str = "") -> str:
    delta_html = (
        f'<div class="kpi-delta {delta_dir}">{delta}</div>' if delta else ""
    )
    card_style  = f'border-left:4px solid {accent};' if accent else ''
    value_style = f'color:{accent};' if accent else ''
    return (
        f'<div class="kpi-card" style="{card_style}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value" style="{value_style}">{value}</div>'
        f'{delta_html}'
        f'</div>'
    )


def badge(text: str, level: str = "neutral") -> str:
    return f'<span class="badge badge-{level}">{text}</span>'


def header_html(icon: str, brand: str, meta: str, file_badge: str = "") -> str:
    badge_str = (
        f'<span class="lt-header-badge">📂 {file_badge}</span>'
        if file_badge else ""
    )
    return (
        f'<div class="lt-header">'
        f'<span style="font-size:1.35rem;line-height:1">{icon}</span>'
        f'<div>'
        f'<p class="lt-header-brand">{brand}</p>'
        f'<p class="lt-header-meta">{meta}</p>'
        f'</div>'
        f'{badge_str}'
        f'</div>'
    )


def prio_level(prioridad: str) -> str:
    return {"Alta": "critical", "Media": "warning", "Baja": "success"}.get(
        prioridad, "neutral"
    )


def estado_level(estado: str) -> str:
    e = estado.lower()
    if "resuelto" in e:
        return "success"
    if "pendiente" in e or "en_gestion" in e or "gestión" in e:
        return "warning"
    if "cancelado" in e or "transferido" in e:
        return "neutral"
    return "neutral"
