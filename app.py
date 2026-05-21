import colorsys
import concurrent.futures
import json
import re

import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests
import streamlit as st

st.set_page_config(
    page_title="10-Mio-Initiative — Seeland/Biel",
    page_icon=None,
    layout="wide",
)

# ── Apple-like CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Base & Typography */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
                 "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    color: #1d1d1f;
}

/* Hide Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* App background — alle Container explizit weiss */
.stApp, .main, section[data-testid="stMain"],
[data-testid="stAppViewContainer"] { background-color: #ffffff !important; }

/* Streamlit-Header ausblenden (Toolbar, Dekoration) */
header[data-testid="stHeader"] {
    background-color: #ffffff !important;
    height: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
}

/* Logo-iframe: kein Rand, kein Abstand */
[data-testid="stHtml"] { margin: 0 !important; padding: 0 !important; }
[data-testid="stHtml"] iframe { display: block !important; border: none !important; }

/* Main content area */
.block-container {
    padding-top: 1rem;
    padding-bottom: 3rem;
}

/* Title — mittig */
h1 {
    font-size: 1.75rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.3px;
    color: #1d1d1f !important;
    line-height: 1.25 !important;
    padding-bottom: 0.25rem;
    text-align: center !important;
}

/* Subheadings */
h2, h3 {
    font-weight: 500 !important;
    color: #1d1d1f !important;
    letter-spacing: -0.2px;
}

/* Lead text */
p { color: #3a3a3c; line-height: 1.6; }

/* Dividers */
hr {
    border: none !important;
    border-top: 1px solid #d2d2d7 !important;
    margin: 1.5rem 0 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #f5f5f7 !important;
    border-right: 1px solid #d2d2d7;
    width: 280px !important;
    min-width: 280px !important;
}
/* Sidebar scrollt nicht selbst — nur der Listen-Container scrollt */
[data-testid="stSidebarContent"] {
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
}
[data-testid="stSidebarContent"] > div {
    padding: 0 !important;
    margin: 0 !important;
    gap: 0 !important;
}
[data-testid="stSidebarUserContent"] {
    padding: 0 !important;
    margin: 0 !important;
}
[data-testid="stSidebarUserContent"] > div {
    padding: 0 !important;
    margin: 0 !important;
    gap: 0 !important;
    row-gap: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stHeading"] {
    padding: 0.35rem 0.75rem 0.1rem !important;
    margin: 0 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #6e6e73 !important;
}

/* Input labels */
label[data-testid="stWidgetLabel"] > div > p,
.stTextInput label, .stSlider label, .stToggle label {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: #6e6e73 !important;
}

/* Text input */
.stTextInput input {
    border: 1px solid #d2d2d7 !important;
    border-radius: 8px !important;
    background: #ffffff !important;
    color: #1d1d1f !important;
    font-size: 0.875rem !important;
    caret-color: #1d1d1f !important;
}
.stTextInput input:focus {
    border-color: #1d1d1f !important;
    box-shadow: none !important;
    caret-color: #1d1d1f !important;
}

/* Slider track & thumb */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background-color: #1d1d1f !important;
    border-color: #1d1d1f !important;
}

/* Toggle */
[data-testid="stToggle"] input:checked + div {
    background-color: #1d1d1f !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #d2d2d7;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.8125rem;
    font-weight: 500;
    color: #6e6e73;
    padding: 0.625rem 1.125rem;
    border-radius: 0;
    background: transparent;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #1d1d1f; }
.stTabs [aria-selected="true"] {
    color: #1d1d1f !important;
    background: transparent !important;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #f5f5f7;
    border-radius: 10px;
    padding: 1rem 1.1rem 0.9rem;
    border: none;
}
[data-testid="stMetricLabel"] p {
    font-size: 0.6875rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: #6e6e73 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    color: #1d1d1f !important;
    letter-spacing: -0.3px;
}

/* Caption */
.stCaption, [data-testid="stCaptionContainer"] p {
    color: #6e6e73 !important;
    font-size: 0.75rem !important;
}

/* Dataframe — helles Design */
[data-testid="stDataFrame"] > div {
    border: 1px solid #d2d2d7;
    border-radius: 10px;
    overflow: hidden;
    background: #ffffff !important;
}
[data-testid="stDataFrame"] * {
    color: #1d1d1f !important;
}
/* Glide Data Grid canvas-Hintergrund */
[data-testid="stDataFrame"] canvas {
    filter: none !important;
}
/* Header-Zeile */
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [role="gridcell"] {
    background: #ffffff !important;
    color: #1d1d1f !important;
}

/* Warning / Info */
[data-testid="stAlert"] {
    border-radius: 8px;
    border: none;
}

/* Sidebar — alle Abstände killen (Streamlit setzt gap via dynamische Emotion-Klassen) */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] > div,
[data-testid="stSidebarUserContent"] > div,
[data-testid="stSidebarUserContent"] > div > div {
    gap: 0 !important;
    row-gap: 0 !important;
}
[data-testid="stSidebar"] div[data-testid="stButton"] {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding: 0 !important;
}
/* Gemeinde-Listenbuttons */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid #e8e8ed !important;
    border-radius: 0 !important;
    color: #1d1d1f !important;
    font-size: 0.8125rem !important;
    font-weight: 400 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 0.3rem 0.5rem !important;
    box-shadow: none !important;
    min-height: 0 !important;
    width: 100% !important;
    transition: background 0.15s ease, border-radius 0.15s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #e8e8ed !important;
    border-radius: 6px !important;
    border-bottom-color: transparent !important;
    color: #1d1d1f !important;
}
/* Sidebar-Header ohne Abstand */
[data-testid="stSidebar"] h3 {
    margin-top: 0 !important;
    margin-bottom: 0.15rem !important;
    padding-top: 0 !important;
}
/* Logo-iframe in Sidebar: kein Margin */
[data-testid="stSidebar"] [data-testid="stHtml"] {
    margin: 0 !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stHtml"] iframe {
    display: block !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── Konstanten ────────────────────────────────────────────────────────────────
AKTUELLES_JAHR = 2026
_FARB_CAP      = 40
FIND_URL = "https://api3.geo.admin.ch/rest/services/api/MapServer/find"

_AXIS = dict(
    gridcolor="#f0f0f0", linecolor="#d2d2d7", tickcolor="#d2d2d7",
    tickfont=dict(color="#1d1d1f"),
    title_font=dict(color="#1d1d1f"),
)
PLOTLY_LAYOUT = dict(
    font_family="-apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif",
    font_color="#1d1d1f",
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    xaxis=_AXIS,
    yaxis=_AXIS,
)

# Koordinaten — Fallback-Punktkarte
KOORDINATEN = {
    "Biezwil": (47.200, 7.445), "Schnottwil": (47.180, 7.430),
    "Bettlach": (47.202, 7.413), "Grenchen": (47.192, 7.397),
    "Selzach": (47.207, 7.469),
    "Fräschels": (46.994, 7.223), "Kerzers (FR)": (46.975, 7.222),
    "Ried bei Kerzers (FR)": (46.986, 7.154),
    "Aegerten": (47.113, 7.258), "Bellmund": (47.113, 7.244),
    "Biel/Bienne": (47.137, 7.247), "Brügg": (47.124, 7.244),
    "Bühl": (47.105, 7.234), "Epsach": (47.077, 7.217),
    "Evilard": (47.148, 7.241), "Hagneck": (47.070, 7.220),
    "Hermrigen": (47.073, 7.178), "Ipsach": (47.107, 7.220),
    "Jens": (47.080, 7.203), "Lengnau (BE)": (47.178, 7.369),
    "Ligerz": (47.086, 7.136), "Merzligen": (47.075, 7.198),
    "Mörigen": (47.088, 7.163), "Nidau": (47.124, 7.234),
    "Orpund": (47.155, 7.312), "Port": (47.120, 7.258),
    "Safnern": (47.168, 7.325), "Scheuren": (47.102, 7.251),
    "Schwadernau": (47.085, 7.233), "Studen (BE)": (47.109, 7.278),
    "Sutz-Lattrigen": (47.095, 7.168), "Twann-Tüscherz": (47.093, 7.145),
    "Worben": (47.095, 7.269), "Aarberg": (47.036, 7.278),
    "Arch": (47.155, 7.469), "Bargen (BE)": (47.176, 7.305),
    "Brüttelen": (47.027, 7.178), "Büetigen": (47.127, 7.393),
    "Büren an der Aare": (47.138, 7.374), "Diessbach bei Büren": (47.128, 7.410),
    "Dotzigen": (47.116, 7.352), "Erlach": (47.041, 7.094),
    "Finsterhennen": (47.030, 7.162), "Gals": (47.010, 7.063),
    "Gampelen": (47.004, 7.058), "Grossaffoltern": (47.053, 7.325),
    "Ins": (46.993, 7.100), "Kallnach": (47.049, 7.206),
    "Kappelen": (47.043, 7.278), "Leuzigen": (47.152, 7.438),
    "Lyss": (47.074, 7.306), "Lüscherz": (47.022, 7.112),
    "Meienried": (47.119, 7.378), "Meikirch": (47.003, 7.313),
    "Meinisberg": (47.160, 7.340), "Müntschemier": (46.993, 7.073),
    "Oberwil bei Büren": (47.147, 7.386), "Pieterlen": (47.166, 7.356),
    "Radelfingen": (47.047, 7.240), "Rapperswil (BE)": (47.098, 7.316),
    "Rüti bei Büren": (47.127, 7.430), "Schüpfen": (47.032, 7.363),
    "Seedorf (BE)": (47.082, 7.249), "Siselen": (47.033, 7.151),
    "Treiten": (47.018, 7.158), "Tschugg": (47.031, 7.076),
    "Täuffelen": (47.063, 7.177), "Vinelz": (47.029, 7.138),
    "Walperswil": (47.051, 7.251), "Wengi": (47.150, 7.466),
}


# ── Hilfsfunktionen ──────────────────────────────────────────────────────────

def normiere_name(name: str) -> str:
    return re.sub(r"\s*\([^)]+\)", "", name).strip()


def tsd(n) -> str:
    try:
        return f"{int(n):,}".replace(",", "'")
    except (TypeError, ValueError):
        return "—"


def zeitfarbe(jahre, schrumpfend) -> list:
    if schrumpfend or jahre is None:
        ratio = 1.0
    else:
        ratio = min(float(jahre) / _FARB_CAP, 1.0)
    hue = ratio * (120 / 360)
    r, g, b = colorsys.hls_to_rgb(hue, 0.42, 0.78)
    return [int(r * 255), int(g * 255), int(b * 255), 210]


def zeitfarbe_hex(jahre, schrumpfend) -> str:
    r, g, b, _ = zeitfarbe(jahre, schrumpfend)
    return f"#{r:02x}{g:02x}{b:02x}"


def polygon_zentrum(rings) -> tuple:
    """Bounding-Box-Mitte aller Ring-Koordinaten ([lon, lat])."""
    coords = [c for ring in rings for c in ring]
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    return (min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2


def berechne_zoom(rings) -> int:
    """Passende Zoomstufe basierend auf der Ausdehnung des Polygons."""
    coords = [c for ring in rings for c in ring]
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    # Faktor 1.4 korrigiert das Aspektverhältnis bei ~47°N
    extent = max(max(lons) - min(lons), (max(lats) - min(lats)) * 1.4)
    if extent < 0.025: return 14
    if extent < 0.06:  return 13
    if extent < 0.12:  return 12
    if extent < 0.25:  return 11
    return 10


# ── Daten laden ───────────────────────────────────────────────────────────────

@st.cache_data
def lade_daten():
    df = pd.read_excel(
        "10Mio_Initiative_Seeland_Biel.xlsx",
        sheet_name="Gemeindeübersicht",
        header=8,
        usecols="A:H",
    )
    df.columns = [
        "Gemeinde", "Kt", "Region",
        "Bev_2024", "Kontingent", "Verf_Wachstum",
        "Wachstumsrate", "Limit_Jahr",
    ]
    df = df.dropna(subset=["Gemeinde"])
    df["Gemeinde"]     = df["Gemeinde"].str.strip()
    df["Kt"]           = df["Kt"].str.strip()
    df["Region"]       = df["Region"].str.strip()
    df["Bev_2024"]     = pd.to_numeric(df["Bev_2024"],     errors="coerce")
    df = df.dropna(subset=["Bev_2024"])          # Legendenzeilen herausfiltern
    df["Kontingent"]   = pd.to_numeric(df["Kontingent"],   errors="coerce")
    df["Verf_Wachstum"]= pd.to_numeric(df["Verf_Wachstum"],errors="coerce")
    df["Wachstumsrate"]= pd.to_numeric(df["Wachstumsrate"],errors="coerce")
    df["Limit_Jahr"]   = df["Limit_Jahr"].astype(str).str.strip()
    df["Schrumpfend"]  = df["Limit_Jahr"].str.contains(
        "schrumpfend|Kein", case=False, na=False
    )
    df["Wachstumsrate_Pct"] = (df["Wachstumsrate"] * 100).round(2)

    # Bevölkerung 2014 — direkt aus Seeland_Biel_Bevoelkerung.xlsx
    bev = pd.read_excel(
        "Seeland_Biel_Bevoelkerung.xlsx",
        sheet_name="Seeland & Biel",
        header=0,
    )[["Gemeinde", 2014]].rename(columns={2014: "Bev_2014"})
    bev["Gemeinde"] = bev["Gemeinde"].str.strip()
    df = df.merge(bev, on="Gemeinde", how="left")

    # Fallback für Gemeinden ohne Eintrag in der Bevoelkerung-Datei
    mask_fehlt = df["Bev_2014"].isna()
    df.loc[mask_fehlt, "Bev_2014"] = (
        df.loc[mask_fehlt, "Bev_2024"] / (1 + df.loc[mask_fehlt, "Wachstumsrate"]) ** 10
    ).round(0)
    df["Bev_2014"] = df["Bev_2014"].round(0).astype("Int64")

    def berechne_jahre(row):
        if row["Schrumpfend"]:
            return None
        try:
            return int(row["Limit_Jahr"]) - AKTUELLES_JAHR
        except (ValueError, TypeError):
            return None

    df["Jahre_bis_Limit"] = df.apply(berechne_jahre, axis=1)
    df["lat"] = df["Gemeinde"].map(lambda g: KOORDINATEN.get(g, (47.10, 7.25))[0])
    df["lon"] = df["Gemeinde"].map(lambda g: KOORDINATEN.get(g, (47.10, 7.25))[1])
    return df


@st.cache_data(ttl=86400, show_spinner="Gemeindegrenzen werden geladen …")
def lade_geometrien(gemeinden_mit_kanton: tuple) -> dict:
    def hole_eine(gemeinde, kanton):
        for suchname in [gemeinde, normiere_name(gemeinde)]:
            params = {
                "layer": "ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill",
                "searchField": "gemname",
                "searchText": suchname,
                "contains": "false",
                "returnGeometry": "true",
                "sr": "4326",
                "f": "json",
            }
            try:
                r = requests.get(FIND_URL, params=params, timeout=20)
                r.raise_for_status()
                results = r.json().get("results", [])
                aktuell = [x for x in results if x.get("attributes", {}).get("is_current_jahr")]
                if not aktuell:
                    aktuell = sorted(
                        results,
                        key=lambda x: x.get("attributes", {}).get("jahr", 0),
                        reverse=True,
                    )[:1]
                kt_treffer = [
                    x for x in aktuell
                    if x.get("attributes", {}).get("kanton", "").upper() == kanton.upper()
                ]
                kandidat = kt_treffer[0] if kt_treffer else (aktuell[0] if aktuell else None)
                if kandidat:
                    rings = kandidat.get("geometry", {}).get("rings", [])
                    if rings:
                        return gemeinde, rings
            except Exception:
                pass
        return gemeinde, None

    geometrien = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(hole_eine, g, k): g for g, k in gemeinden_mit_kanton}
        for future in concurrent.futures.as_completed(futures):
            name, rings = future.result()
            if rings:
                geometrien[name] = rings
    return geometrien


def erstelle_polygon_features(df_filtered, geometrien: dict) -> list:
    rows = []
    for _, row in df_filtered.iterrows():
        rings = geometrien.get(row["Gemeinde"])
        if not rings:
            continue
        jahre = row["Jahre_bis_Limit"]
        farbe = zeitfarbe(jahre, row["Schrumpfend"])
        jahre_text = f"{int(jahre)} Jahre" if pd.notna(jahre) else "Schrumpfend"

        props = {
            "color": farbe,
            "Gemeinde": row["Gemeinde"],
            "Kt": row["Kt"],
            "Bev_2014":      tsd(row["Bev_2014"]),
            "Bev_2024":      tsd(row["Bev_2024"]),
            "Kontingent":    tsd(row["Kontingent"]),
            "Verf_Wachstum": tsd(row["Verf_Wachstum"]),
            "Wachstumsrate_Pct": float(row["Wachstumsrate_Pct"]),
            "Limit_Jahr":    row["Limit_Jahr"],
            "Jahre_bis_Limit": jahre_text,
        }
        for ring in rings:
            rows.append({"polygon": [ring], **props})
    return rows


# ── Initialisierung ───────────────────────────────────────────────────────────
df_roh = lade_daten()
gemeinden_tuple = tuple(zip(df_roh["Gemeinde"].tolist(), df_roh["Kt"].tolist()))
geometrien      = lade_geometrien(gemeinden_tuple)
api_verfuegbar  = len(geometrien) >= 30


# ── Session State ─────────────────────────────────────────────────────────────
if "selected_gemeinde" not in st.session_state:
    st.session_state.selected_gemeinde = None

with open("ajour-logo.json") as _f:
    _lottie_data = json.dumps(json.load(_f))


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:0.1rem 0 0.3rem;'>
  <h1 style='font-size:3.4rem; font-weight:800; letter-spacing:-1.5px;
             color:#1d1d1f; margin:0 0 0.2rem; line-height:1.05;'>
    10-Millionen-Initiative
  </h1>
  <div style='font-size:1.35rem; font-weight:500; color:#3a3a3c;
              letter-spacing:-0.2px;'>
    So viel dürfte das Seeland noch wachsen
  </div>
</div>
""", unsafe_allow_html=True)
st.divider()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo ganz oben in der Sidebar (280 px breit, Höhe proportional 280/5.49 ≈ 51 px)
    st.components.v1.html(f"""
    <!DOCTYPE html><html><head>
    <style>
    html,body{{margin:0;padding:0;background:#f5f5f7;overflow:hidden;
               width:280px;height:51px;}}
    </style></head>
    <body>
    <div id="logo" style="width:280px;height:51px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
    <script>
    lottie.loadAnimation({{container:document.getElementById('logo'),
        renderer:'svg',loop:true,autoplay:true,animationData:{_lottie_data}}});
    </script>
    </body></html>
    """, height=51)

    if not api_verfuegbar:
        st.caption("Gemeindegrenzen nicht verfügbar — Darstellung als Punkte")

    # Details-Panel — wird oben gerendert (session_state dank st.rerun() bereits korrekt)
    sel = st.session_state.selected_gemeinde
    if sel:
        sel_row = df_roh[df_roh["Gemeinde"] == sel]
        if not sel_row.empty:
            r     = sel_row.iloc[0]
            wrate = f"{r['Wachstumsrate_Pct']:.2f} %" if pd.notna(r["Wachstumsrate_Pct"]) else "—"
            schrumpfend = bool(r.get("Schrumpfend", False))
            lbl = ("font-size:0.76rem; color:#6e6e73; padding:3px 0; "
                   "vertical-align:top; width:55%;")
            val = ("font-size:0.76rem; color:#1d1d1f; font-weight:500; "
                   "text-align:right; vertical-align:top; padding:3px 0 3px 6px;")
            kontingent_str = tsd(r["Kontingent"]) if not schrumpfend else "—"
            verf_str       = tsd(r["Verf_Wachstum"]) if not schrumpfend else "—"
            limit_str      = str(r["Limit_Jahr"]) if not schrumpfend else "Schrumpfend"
            st.markdown(f"""
<div style='font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue",Arial,sans-serif;
            margin:6px 8px 0;'>
  <div style='font-size:0.8125rem; font-weight:600; color:#1d1d1f;
              margin-bottom:5px; padding:0 4px;'>{sel}</div>
  <div style='background:#eaeaec; border-radius:8px; padding:7px 10px;'>
    <table style='width:100%; border-collapse:collapse;
                  table-layout:fixed; line-height:1.6;'>
      <tr><td style='{lbl}'>Bevölkerung 2014</td>
          <td style='{val}'>{tsd(r["Bev_2014"])}</td></tr>
      <tr><td style='{lbl}'>Bevölkerung 2024</td>
          <td style='{val}'>{tsd(r["Bev_2024"])}</td></tr>
      <tr><td style='{lbl}'>Wachstum p. a.</td>
          <td style='{val}'>{wrate}</td></tr>
      <tr><td style='{lbl}'>Kontingent</td>
          <td style='{val}'>{kontingent_str}</td></tr>
      <tr><td style='{lbl}'>Verf. Wachstum</td>
          <td style='{val}'>{verf_str}</td></tr>
      <tr><td style='{lbl}'>Limite</td>
          <td style='{val}'>{limit_str}</td></tr>
    </table>
  </div>
</div>
""", unsafe_allow_html=True)

    if sel:
        st.divider()
    st.header("Gemeinden")

    # Scrollbarer Sub-Container — nur die Liste scrollt, Details-Panel bleibt oben
    _list_height = 420 if sel else 600
    with st.container(height=_list_height, border=False):
        for _, row in df_roh.sort_values("Gemeinde").iterrows():
            name        = row["Gemeinde"]
            is_selected = st.session_state.selected_gemeinde == name
            label       = f"› {name}" if is_selected else name
            if st.button(label, key=f"gem_{name}", use_container_width=True):
                st.session_state.selected_gemeinde = None if is_selected else name
                st.rerun()


# ── Filter ────────────────────────────────────────────────────────────────────
df = df_roh.copy()


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_karte, tab_tabelle, tab_charts = st.tabs(["Karte", "Tabelle", "Diagramme"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — KARTE
# ════════════════════════════════════════════════════════════════════════════
with tab_karte:
    _df_w = df_roh[~df_roh["Schrumpfend"]]

    def kachel(col, label, wert):
        col.markdown(f"""
        <div style='background:#f5f5f7; border-radius:10px;
                    padding:0.7rem 0.8rem 0.6rem; margin-bottom:0.4rem;'>
          <div style='font-size:0.62rem; font-weight:600; text-transform:uppercase;
                      letter-spacing:0.06em; color:#6e6e73;
                      margin-bottom:0.2rem'>{label}</div>
          <div>
            <span style='font-size:1.3rem; font-weight:700;
                         color:#1d1d1f; letter-spacing:-0.3px'>{wert}</span>
            <span style='font-size:0.75rem; color:#6e6e73;
                         margin-left:4px'>Gem.</span>
          </div>
        </div>""", unsafe_allow_html=True)

    col_map, col_desc = st.columns([2, 1], gap="large")

    with col_map:
        if df.empty:
            st.warning("Keine Gemeinden entsprechen den aktuellen Filtereinstellungen.")
        elif not api_verfuegbar:
            st.info("Gemeindegrenzen konnten nicht geladen werden — Darstellung als Punkte.")
            df["farbe"]  = df.apply(lambda r: zeitfarbe(r["Jahre_bis_Limit"], r["Schrumpfend"]), axis=1)
            max_bev      = df_roh["Bev_2024"].max()
            df["radius"] = (df["Bev_2024"] / max_bev * 2200 + 300).round(0)
            layer = pdk.Layer("ScatterplotLayer", data=df,
                              get_position="[lon, lat]", get_fill_color="farbe",
                              get_radius="radius", pickable=True, opacity=0.85)
            view = pdk.ViewState(latitude=df["lat"].mean(), longitude=df["lon"].mean(), zoom=10)
            st.pydeck_chart(
                pdk.Deck(layers=[layer], initial_view_state=view,
                         map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"),
                use_container_width=True,
            )
        else:
            sel_name = st.session_state.selected_gemeinde
            df_map = df.copy()
            if sel_name and sel_name not in df_map["Gemeinde"].values:
                sel_row = df_roh[df_roh["Gemeinde"] == sel_name]
                if not sel_row.empty:
                    df_map = pd.concat([df_map, sel_row], ignore_index=True)

            features = erstelle_polygon_features(df_map, geometrien)

            hl_features = []
            if sel_name and sel_name in geometrien:
                for ring in geometrien[sel_name]:
                    hl_features.append({"polygon": [ring]})

            if not features:
                st.warning("Keine Polygondaten verfügbar. Bitte Seite neu laden.")
            else:
                tooltip = {
                    "html": """
                    <div style='font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue",
                                Arial,sans-serif; font-size:13px; min-width:220px;
                                color:#1d1d1f'>
                      <div style='font-size:15px; font-weight:600;
                                  margin-bottom:8px'>{Gemeinde} <span
                        style='font-weight:400; color:#6e6e73'>({Kt})</span></div>
                      <div style='border-top:1px solid #d2d2d7; margin-bottom:8px'></div>
                      <table style='width:100%; border-collapse:collapse;
                                    font-size:12.5px; line-height:1.7'>
                        <tr><td style='color:#6e6e73'>Bevölkerung 2014</td>
                            <td style='text-align:right; font-weight:500'>{Bev_2014}</td></tr>
                        <tr><td style='color:#6e6e73'>Bevölkerung 2024</td>
                            <td style='text-align:right; font-weight:500'>{Bev_2024}</td></tr>
                        <tr><td style='color:#6e6e73'>Wachstum in % p. a.</td>
                            <td style='text-align:right; font-weight:500'>{Wachstumsrate_Pct} %</td></tr>
                        <tr><td style='color:#6e6e73'>Kontingent bei 10-Millionen-Schweiz</td>
                            <td style='text-align:right; font-weight:500'>{Kontingent}</td></tr>
                        <tr><td style='color:#6e6e73'>Verfügbares Wachstum</td>
                            <td style='text-align:right; font-weight:500'>{Verf_Wachstum}</td></tr>
                        <tr><td style='color:#6e6e73'>Limite erreicht</td>
                            <td style='text-align:right; font-weight:500'>{Limit_Jahr}</td></tr>
                      </table>
                    </div>""",
                    "style": {
                        "backgroundColor": "white",
                        "border": "1px solid #d2d2d7",
                        "borderRadius": "10px",
                        "padding": "12px 14px",
                        "boxShadow": "0 4px 16px rgba(0,0,0,0.10)",
                    },
                }

                view_state = pdk.ViewState(
                    latitude=47.09, longitude=7.24, zoom=10, pitch=0,
                    transition_duration=800,
                )

                layer = pdk.Layer(
                    "PolygonLayer", data=features,
                    get_polygon="polygon",
                    get_fill_color="color",
                    get_line_color=[180, 180, 180, 180],
                    line_width_min_pixels=1,
                    pickable=True, filled=True, stroked=True, opacity=0.85,
                )
                hl_layer = pdk.Layer(
                    "PolygonLayer", data=hl_features,
                    get_polygon="polygon",
                    get_fill_color=[0, 0, 0, 0],
                    get_line_color=[30, 30, 30, 255],
                    line_width_min_pixels=3,
                    filled=True, stroked=True,
                )
                st.pydeck_chart(
                    pdk.Deck(
                        layers=[layer, hl_layer],
                        initial_view_state=view_state,
                        tooltip=tooltip,
                        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
                    ),
                    use_container_width=True,
                    key="hauptkarte",
                )

        # Farbskala — nur so breit wie die Karte
        if not df.empty:
            st.markdown("""
<div style='display:flex;align-items:center;gap:10px;margin:8px 0 4px;'>
  <span style='font-size:0.72rem;color:#6e6e73;white-space:nowrap'>Limit bald erreicht</span>
  <div style='flex:1;height:6px;border-radius:3px;
              background:linear-gradient(to right,#be1717 0%,#bebe17 50%,#17be17 100%)'></div>
  <span style='font-size:0.72rem;color:#6e6e73;white-space:nowrap'>Limit weit entfernt</span>
</div>""", unsafe_allow_html=True)

    with col_desc:
        st.markdown("""
        <p style='font-size:0.9rem; color:#6e6e73; line-height:1.75; margin:0 0 1rem;
                  padding-top:0.25rem;'>
          Die <strong style='color:#3a3a3c;'>10-Millionen-Initiative</strong>
          will die Einwohnerzahl der Schweiz bei
          <strong style='color:#3a3a3c;'>10 Millionen</strong> deckeln.
          Ende 2024 lebten <strong style='color:#3a3a3c;'>9'051'029</strong>
          Personen in der Schweiz — es bleiben noch
          <strong style='color:#3a3a3c;'>948'971</strong> Plätze übrig (+10,5 %).
          Dieses Kontingent wird proportional auf alle Gemeinden verteilt.
          Die Farben zeigen, wie viele Jahre jede Gemeinde bei aktuellem
          Wachstum noch hat, bis sie ihr Kontingent ausschöpft.
        </p>
        """, unsafe_allow_html=True)

        k1, k2 = st.columns(2, gap="small")
        kachel(k1, "Limit bis 2030",  len(_df_w[_df_w["Jahre_bis_Limit"] <= 4]))
        kachel(k2, "Limit 2031–2040", len(_df_w[(_df_w["Jahre_bis_Limit"] > 4) & (_df_w["Jahre_bis_Limit"] <= 14)]))
        k3, k4 = st.columns(2, gap="small")
        kachel(k3, "Limit ab 2041",   len(_df_w[_df_w["Jahre_bis_Limit"] > 14]))
        kachel(k4, "Schrumpfend",     len(df_roh[df_roh["Schrumpfend"]]))


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — TABELLE
# ════════════════════════════════════════════════════════════════════════════
with tab_tabelle:
    # ── Regionale Übersicht ──────────────────────────────────────────────────
    st.markdown(
        "<div style='font-size:0.7rem; font-weight:600; text-transform:uppercase; "
        "letter-spacing:0.07em; color:#6e6e73; margin-bottom:0.6rem;'>"
        "Das ajour-Land im Überblick</div>",
        unsafe_allow_html=True,
    )

    _bev14 = int(df_roh["Bev_2014"].sum())
    _bev24 = int(df_roh["Bev_2024"].sum())
    _kont  = int(df_roh["Kontingent"].sum())
    _verf  = int(df_roh["Verf_Wachstum"].sum())
    _cagr  = ((_bev24 / _bev14) ** (1 / 10) - 1) * 100
    _limit_median = int(
        pd.to_numeric(
            df_roh.loc[~df_roh["Schrumpfend"], "Limit_Jahr"], errors="coerce"
        ).dropna().median()
    )

    def _ovcard(col, label, value):
        col.markdown(f"""
        <div style='background:#f5f5f7; border-radius:10px;
                    padding:0.9rem 1rem 0.8rem;'>
          <div style='font-size:0.65rem; font-weight:600; text-transform:uppercase;
                      letter-spacing:0.06em; color:#6e6e73; margin-bottom:0.25rem'>
            {label}</div>
          <div style='font-size:1.25rem; font-weight:600; color:#1d1d1f;
                      letter-spacing:-0.3px; white-space:nowrap'>{value}</div>
        </div>""", unsafe_allow_html=True)

    ov1, ov2, ov3 = st.columns(3, gap="medium")
    _ovcard(ov1, "Bevölkerung 2014", tsd(_bev14))
    _ovcard(ov2, "Bevölkerung 2024", tsd(_bev24))
    _ovcard(ov3, "Kontingent total", tsd(_kont))

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    ov4, ov5, ov6 = st.columns(3, gap="medium")
    _ovcard(ov4, "Verfügbares Wachstum", tsd(_verf))
    _ovcard(ov5, "Wachstum p. a. (Region)", f"{_cagr:.2f} %")
    _ovcard(ov6, "Medianes Limit-Jahr", str(_limit_median))

    st.divider()

    th = ("padding:10px 14px; text-align:left; font-size:0.75rem; font-weight:600; "
          "text-transform:uppercase; letter-spacing:0.05em; color:#6e6e73; "
          "border-bottom:2px solid #d2d2d7; background:#f5f5f7; white-space:nowrap;")
    th_r = th + "text-align:right;"
    td  = "padding:9px 14px; color:#1d1d1f; border-bottom:1px solid #f0f0f0; font-size:0.875rem;"
    td_r = td + "text-align:right; font-variant-numeric:tabular-nums;"

    rows_html = ""
    for _, r in df_roh.sort_values("Gemeinde").iterrows():
        jahre = str(int(r["Jahre_bis_Limit"])) if pd.notna(r["Jahre_bis_Limit"]) else "—"
        wrate = f"{r['Wachstumsrate_Pct']:.2f} %" if pd.notna(r["Wachstumsrate_Pct"]) else "—"
        rows_html += (
            f"<tr>"
            f"<td style='{td}'>{r['Gemeinde']}</td>"
            f"<td style='{td_r}'>{tsd(r['Bev_2014'])}</td>"
            f"<td style='{td_r}'>{tsd(r['Bev_2024'])}</td>"
            f"<td style='{td_r}'>{tsd(r['Kontingent'])}</td>"
            f"<td style='{td_r}'>{tsd(r['Verf_Wachstum'])}</td>"
            f"<td style='{td_r}'>{wrate}</td>"
            f"<td style='{td}'>{r['Limit_Jahr']}</td>"
            f"<td style='{td_r}'>{jahre}</td>"
            f"</tr>"
        )

    st.markdown(f"""
    <div style="overflow-x:auto; border:1px solid #d2d2d7; border-radius:10px;
                overflow:hidden; background:#ffffff; max-height:600px; overflow-y:auto;">
      <table style="width:100%; border-collapse:collapse;
                    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                    background:#ffffff;">
        <thead style="position:sticky; top:0; z-index:1;">
          <tr>
            <th style="{th}">Gemeinde</th>
            <th style="{th_r}">Bev. 2014</th>
            <th style="{th_r}">Bev. 2024</th>
            <th style="{th_r}">Kontingent</th>
            <th style="{th_r}">Verf. Wachstum</th>
            <th style="{th_r}">Wachstum p.a.</th>
            <th style="{th}">Limit erreicht</th>
            <th style="{th_r}">Jahre bis Limit</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — CHARTS
# ════════════════════════════════════════════════════════════════════════════
with tab_charts:

    # ── Chart 1: Top 15 schnellstwachsende Gemeinden ────────────────────────
    st.subheader("Top 15 schnellstwachsende Gemeinden (CAGR p.a.)")
    df_w1 = df_roh.nlargest(15, "Wachstumsrate").copy()
    df_w1["farbe_chart"] = df_w1.apply(
        lambda r: zeitfarbe_hex(r["Jahre_bis_Limit"], r["Schrumpfend"]), axis=1)
    fig1 = px.bar(
        df_w1.sort_values("Wachstumsrate"),
        x="Wachstumsrate_Pct", y="Gemeinde", orientation="h",
        color="farbe_chart", color_discrete_map="identity",
        labels={"Wachstumsrate_Pct": "Wachstumsrate p.a. (%)", "Gemeinde": ""},
        text="Wachstumsrate_Pct",
    )
    fig1.update_traces(texttemplate="%{text:.2f} %", textposition="outside")
    fig1.update_layout(
        **PLOTLY_LAYOUT, showlegend=False, height=460,
        margin=dict(l=0, r=90, t=10, b=10),
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ── Chart 2: Kürzester Zeitpuffer ────────────────────────────────────────
    st.subheader("Gemeinden mit dem kürzesten Zeitpuffer bis zum Limit")
    df_puffer = df_roh[~df_roh["Schrumpfend"]].nsmallest(20, "Jahre_bis_Limit").copy()
    df_puffer["farbe_chart"] = df_puffer.apply(
        lambda r: zeitfarbe_hex(r["Jahre_bis_Limit"], r["Schrumpfend"]), axis=1)
    df_puffer["Jahre_int"] = df_puffer["Jahre_bis_Limit"].fillna(0).astype(int)
    fig2 = px.bar(
        df_puffer.sort_values("Jahre_bis_Limit"),
        x="Jahre_int", y="Gemeinde", orientation="h",
        color="farbe_chart", color_discrete_map="identity",
        labels={"Jahre_int": "Jahre bis Limit", "Gemeinde": ""},
        text="Jahre_int",
        custom_data=["Limit_Jahr"],
    )
    fig2.update_traces(
        texttemplate="%{text} J. (%{customdata[0]})", textposition="outside")
    fig2.update_layout(
        **PLOTLY_LAYOUT, showlegend=False, height=510,
        margin=dict(l=0, r=140, t=10, b=10),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Chart 3: Scatter Bevölkerung vs. Spielraum ───────────────────────────
    st.subheader("Bevölkerung vs. verfügbares Wachstum")
    df_sc = df_roh.copy()
    df_sc["Wachstumsrate_abs"] = df_sc["Wachstumsrate"].abs() * 100
    df_sc["Jahre_text"] = df_sc["Jahre_bis_Limit"].apply(
        lambda x: str(int(x)) if pd.notna(x) else "Schrumpfend")
    top3     = df_sc.nlargest(3, "Verf_Wachstum")["Gemeinde"].tolist()
    bottom4  = df_sc[~df_sc["Schrumpfend"]].nsmallest(4, "Jahre_bis_Limit")["Gemeinde"].tolist()
    groesste = df_sc.nlargest(2, "Bev_2024")["Gemeinde"].tolist()
    labels_set = set(top3 + bottom4 + groesste)
    df_sc["label"] = df_sc["Gemeinde"].apply(lambda g: g if g in labels_set else "")

    fig3 = px.scatter(
        df_sc,
        x="Bev_2024", y="Verf_Wachstum",
        color="Region", size="Wachstumsrate_abs", size_max=24,
        hover_name="Gemeinde",
        hover_data={
            "Bev_2014": True, "Bev_2024": True,
            "Verf_Wachstum": True, "Wachstumsrate_Pct": True,
            "Limit_Jahr": True, "Jahre_text": True,
            "Wachstumsrate_abs": False,
        },
        text="label",
        labels={
            "Bev_2024": "Bevölkerung 2024",
            "Verf_Wachstum": "Verfügbares Wachstum (Personen)",
            "Wachstumsrate_Pct": "Wachstumsrate p.a. (%)",
            "Jahre_text": "Jahre bis Limit",
            "Bev_2014": "Bevölkerung 2014",
        },
    )
    fig3.update_traces(textposition="top center", textfont_size=11)
    fig3.update_layout(
        **PLOTLY_LAYOUT, height=520,
        margin=dict(l=0, r=0, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    st.plotly_chart(fig3, use_container_width=True)


# ── JS-Patch: Sidebar-Gap + Map-Lock via window.parent ────────────────────────
st.components.v1.html("""
<script>
(function() {
    function fixAll() {
        try {
            var doc = window.parent.document;

            // ── Sidebar spacing ───────────────────────────────────────────
            var sb = doc.querySelector('[data-testid="stSidebar"]');
            if (sb) {
                ['stSidebarContent','stSidebarUserContent'].forEach(function(tid) {
                    var el = sb.querySelector('[data-testid="' + tid + '"]');
                    if (!el) return;
                    el.style.setProperty('padding','0px','important');
                    el.style.setProperty('margin','0px','important');
                    Array.from(el.children).forEach(function(c) {
                        c.style.setProperty('padding-top','0px','important');
                        c.style.setProperty('margin-top','0px','important');
                        c.style.setProperty('gap','0px','important');
                        c.style.setProperty('row-gap','0px','important');
                        Array.from(c.children).forEach(function(gc) {
                            gc.style.setProperty('padding-top','0px','important');
                            gc.style.setProperty('margin-top','0px','important');
                            gc.style.setProperty('gap','0px','important');
                            gc.style.setProperty('row-gap','0px','important');
                        });
                    });
                });
                sb.querySelectorAll('[data-testid="stVerticalBlock"],[data-testid="stVerticalBlockBorderWrapper"]').forEach(function(el) {
                    el.style.setProperty('gap','0px','important');
                    el.style.setProperty('row-gap','0px','important');
                    el.style.setProperty('padding','0px','important');
                    el.style.setProperty('margin','0px','important');
                });
                sb.querySelectorAll('div[data-testid="stButton"]').forEach(function(el) {
                    el.style.setProperty('margin','0px','important');
                    el.style.setProperty('padding','0px','important');
                });
                // kill margin on the stHtml iframe wrapper (logo)
                sb.querySelectorAll('[data-testid="stHtml"]').forEach(function(el) {
                    el.style.setProperty('margin','0px','important');
                    el.style.setProperty('padding','0px','important');
                });
            }

            // ── Map lock (block zoom + pan, keep hover/tooltip) ───────────
            doc.querySelectorAll('[data-testid="stDeckGlJsonChart"]').forEach(function(chart) {
                if (chart._deckLocked) return;
                chart._deckLocked = true;
                // block scroll zoom
                chart.addEventListener('wheel', function(e) {
                    e.stopPropagation(); e.preventDefault();
                }, {passive: false, capture: true});
                // block drag pan (stop mousedown so deck.gl never starts tracking)
                chart.addEventListener('mousedown', function(e) {
                    e.stopPropagation();
                }, {capture: true});
                // block double-click zoom
                chart.addEventListener('dblclick', function(e) {
                    e.stopPropagation(); e.preventDefault();
                }, {capture: true});
                // block touch pan/zoom
                chart.addEventListener('touchstart', function(e) {
                    e.stopPropagation(); e.preventDefault();
                }, {passive: false, capture: true});
                chart.addEventListener('touchmove', function(e) {
                    e.stopPropagation(); e.preventDefault();
                }, {passive: false, capture: true});
                chart.style.setProperty('cursor','default','important');
            });
        } catch(e) {}
    }
    fixAll();
    setInterval(fixAll, 800);
})();
</script>
""", height=1)


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Bevölkerungsdaten: Bundesamt für Statistik, Bilanz der ständigen Wohnbevölkerung "
    "nach Bezirken und Gemeinden, 1991–2024  ·  "
    "Methodik: Proportionale Zuteilung des nationalen Kontingents  ·  "
    "Gemeindegrenzen: © swisstopo (geo.admin.ch)"
)
