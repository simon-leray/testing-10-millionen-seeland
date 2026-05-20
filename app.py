import colorsys
import concurrent.futures
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

/* App background */
.stApp { background-color: #ffffff; }

/* Main content area */
.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
}

/* Title */
h1 {
    font-size: 1.75rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.3px;
    color: #1d1d1f !important;
    line-height: 1.25 !important;
    padding-bottom: 0.25rem;
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
    border-bottom: 2px solid transparent;
}
.stTabs [data-baseweb="tab"]:hover { color: #1d1d1f; }
.stTabs [aria-selected="true"] {
    color: #1d1d1f !important;
    border-bottom: 2px solid #1d1d1f !important;
    background: transparent !important;
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

/* Sidebar — Gemeinde-Listenbuttons */
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
    padding: 0.45rem 0.25rem !important;
    box-shadow: none !important;
    min-height: 0 !important;
    transition: background 0.15s ease, border-radius 0.15s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #e8e8ed !important;
    border-radius: 6px !important;
    border-bottom-color: transparent !important;
    color: #1d1d1f !important;
}
</style>
""", unsafe_allow_html=True)

# ── Konstanten ────────────────────────────────────────────────────────────────
AKTUELLES_JAHR = 2026
_FARB_CAP      = 40
FIND_URL = "https://api3.geo.admin.ch/rest/services/api/MapServer/find"

PLOTLY_LAYOUT = dict(
    font_family="-apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif",
    font_color="#1d1d1f",
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    xaxis=dict(gridcolor="#f0f0f0", linecolor="#d2d2d7", tickcolor="#d2d2d7"),
    yaxis=dict(gridcolor="#f0f0f0", linecolor="#d2d2d7", tickcolor="#d2d2d7"),
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
        return str(n)


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


# ── Header ────────────────────────────────────────────────────────────────────
st.title("10-Millionen-Initiative — Wachstumspotenzial Seeland/Biel")
st.markdown(
    "Die **10-Millionen-Initiative** will die Einwohnerzahl der Schweiz bei **10 Millionen** deckeln. "
    "Ende 2024 lebten **9'051'029** Personen in der Schweiz — es bleiben noch **948'971** Plätze übrig (+10,5 %). "
    "Dieses Kontingent wird proportional auf alle Gemeinden verteilt. "
    "Die Farben zeigen, wie viele Jahre jede Gemeinde bei aktuellem Wachstum noch hat, "
    "bis sie ihr Kontingent ausschöpft."
)
st.divider()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filter")

    suche = st.text_input("Gemeinde", placeholder="Name suchen …")

    if not api_verfuegbar:
        st.divider()
        st.caption("Gemeindegrenzen nicht verfügbar — Darstellung als Punkte")

    st.divider()
    st.header("Gemeinden")

    gemeinden_iter = df_roh.sort_values("Gemeinde")
    if suche:
        gemeinden_iter = gemeinden_iter[
            gemeinden_iter["Gemeinde"].str.contains(suche, case=False, na=False)
        ]
    for _, row in gemeinden_iter.iterrows():
        name       = row["Gemeinde"]
        is_selected = st.session_state.selected_gemeinde == name
        label      = f"› {name}" if is_selected else name
        if st.button(label, key=f"gem_{name}", use_container_width=True):
            st.session_state.selected_gemeinde = None if is_selected else name

    # ── Details-Panel (kein st.rerun() nötig — session_state wird oben in der
    #    Schleife sofort gesetzt, danach liest dieses Panel den aktuellen Wert)
    sel = st.session_state.selected_gemeinde
    if sel:
        sel_row = df_roh[df_roh["Gemeinde"] == sel]
        if not sel_row.empty:
            r     = sel_row.iloc[0]
            wrate = f"{r['Wachstumsrate_Pct']:.2f} %" if pd.notna(r["Wachstumsrate_Pct"]) else "—"
            val   = "color:#1d1d1f; text-align:right; font-weight:500; white-space:nowrap"
            lbl   = "color:#6e6e73"
            st.divider()
            st.markdown(f"""
            <div style='font-family:-apple-system,BlinkMacSystemFont,
                        "Helvetica Neue",Arial,sans-serif;'>
              <div style='font-size:0.8125rem; font-weight:600; color:#1d1d1f;
                          margin-bottom:8px'>{sel}</div>
              <div style='background:#eaeaec; border-radius:8px;
                          padding:9px 12px; font-size:0.78rem;'>
                <table style='width:100%; border-collapse:collapse; line-height:1.9;'>
                  <tr><td style='{lbl}'>Bevölkerung 2014</td>
                      <td style='{val}'>{tsd(r["Bev_2014"])}</td></tr>
                  <tr><td style='{lbl}'>Bevölkerung 2024</td>
                      <td style='{val}'>{tsd(r["Bev_2024"])}</td></tr>
                  <tr><td style='{lbl}'>Wachstum in % p. a.</td>
                      <td style='{val}'>{wrate}</td></tr>
                  <tr><td style='{lbl}'>Kontingent</td>
                      <td style='{val}'>{tsd(r["Kontingent"])}</td></tr>
                  <tr><td style='{lbl}'>Verfügbares Wachstum</td>
                      <td style='{val}'>{tsd(r["Verf_Wachstum"])}</td></tr>
                  <tr><td style='{lbl}'>Limite erreicht</td>
                      <td style='{val}'>{r["Limit_Jahr"]}</td></tr>
                </table>
              </div>
            </div>
            """, unsafe_allow_html=True)


# ── Filter ────────────────────────────────────────────────────────────────────
df = df_roh.copy()
if suche:
    df = df[df["Gemeinde"].str.contains(suche, case=False, na=False)]

df = df.copy()


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_karte, tab_tabelle, tab_charts = st.tabs(["Karte", "Tabelle", "Charts"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — KARTE
# ════════════════════════════════════════════════════════════════════════════
with tab_karte:
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
        # Sicherstellen: ausgewählte Gemeinde ist immer im Layer,
        # auch wenn sie durch den Filter nicht in df enthalten ist
        sel_name = st.session_state.selected_gemeinde
        df_map = df.copy()
        if sel_name and sel_name not in df_map["Gemeinde"].values:
            sel_row = df_roh[df_roh["Gemeinde"] == sel_name]
            if not sel_row.empty:
                df_map = pd.concat([df_map, sel_row], ignore_index=True)

        features = erstelle_polygon_features(df_map, geometrien)

        # Highlight-Ring für die ausgewählte Gemeinde
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

            # Kamera: Sidebar-Auswahl hat Vorrang, dann Suche, dann Standardansicht
            zoom_name  = None
            zoom_level = 10

            if st.session_state.selected_gemeinde:
                zoom_name  = st.session_state.selected_gemeinde
                zoom_level = 13
            elif suche and not df.empty:
                zoom_name  = df.iloc[0]["Gemeinde"]
                zoom_level = 13 if len(df) == 1 else 11

            if zoom_name:
                if zoom_name in geometrien:
                    clat, clon = polygon_zentrum(geometrien[zoom_name])
                    zoom_level = berechne_zoom(geometrien[zoom_name])
                else:
                    zrow = df_roh[df_roh["Gemeinde"] == zoom_name]
                    clat = zrow.iloc[0]["lat"] if not zrow.empty else 47.09
                    clon = zrow.iloc[0]["lon"] if not zrow.empty else 7.24
                view_state = pdk.ViewState(
                    latitude=clat, longitude=clon,
                    zoom=zoom_level, pitch=0,
                    transition_duration=1200,
                )
            else:
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
                get_fill_color=[0, 0, 0, 0],       # transparent fill
                get_line_color=[30, 30, 30, 255],   # dunkler Rand
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

    st.markdown("""
    <div style='display:flex; align-items:center; gap:10px; margin:14px 0 6px;'>
      <span style='font-size:0.72rem; color:#6e6e73;
                   white-space:nowrap'>Limit bald</span>
      <div style='flex:1; height:6px; border-radius:3px;
                  background:linear-gradient(to right,
                    #be1717 0%, #bebe17 50%, #17be17 100%)'></div>
      <span style='font-size:0.72rem; color:#6e6e73;
                   white-space:nowrap'>Langfristig / schrumpfend</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    df_w = df_roh[~df_roh["Schrumpfend"]]

    def kachel(col, label, wert):
        col.markdown(f"""
        <div style='background:#f5f5f7; border-radius:10px;
                    padding:1rem 1.1rem 0.9rem;'>
          <div style='font-size:0.6875rem; font-weight:600;
                      text-transform:uppercase; letter-spacing:0.06em;
                      color:#6e6e73; margin-bottom:0.3rem'>{label}</div>
          <div>
            <span style='font-size:1.4rem; font-weight:600;
                         color:#1d1d1f; letter-spacing:-0.3px'>{wert}</span>
            <span style='font-size:0.8125rem; font-weight:400;
                         color:#6e6e73; margin-left:5px'>Gemeinden</span>
          </div>
        </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    kachel(c1, "Limit bis 2030",   len(df_w[df_w["Jahre_bis_Limit"] <= 4]))
    kachel(c2, "Limit 2031–2040",  len(df_w[(df_w["Jahre_bis_Limit"] > 4) & (df_w["Jahre_bis_Limit"] <= 14)]))
    kachel(c3, "Limit ab 2041",    len(df_w[df_w["Jahre_bis_Limit"] > 14]))
    kachel(c4, "Schrumpfend",      len(df_roh[df_roh["Schrumpfend"]]))


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — TABELLE
# ════════════════════════════════════════════════════════════════════════════
with tab_tabelle:
    c1, c2, c3 = st.columns(3)
    c1.metric("Gemeinden", len(df_roh))
    c2.metric("Gesamtbevölkerung 2024",
              f"{int(df_roh['Bev_2024'].sum()):,}".replace(",", "'"))
    c3.metric("Gesamtspielraum",
              f"{int(df_roh['Verf_Wachstum'].sum()):,}".replace(",", "'") + " Pers.")
    st.divider()

    df_anz = df_roh[[
        "Gemeinde", "Kt", "Region",
        "Bev_2014", "Bev_2024", "Kontingent",
        "Verf_Wachstum", "Wachstumsrate_Pct", "Limit_Jahr", "Jahre_bis_Limit",
    ]].copy()
    df_anz["Bev_2014_fmt"]  = df_anz["Bev_2014"].apply(tsd)
    df_anz["Bev_2024_fmt"]  = df_anz["Bev_2024"].apply(tsd)
    df_anz["Kont_fmt"]      = df_anz["Kontingent"].apply(tsd)
    df_anz["Wachst_fmt"]    = df_anz["Verf_Wachstum"].apply(tsd)
    df_anz["Jahre_Anzeige"] = df_anz["Jahre_bis_Limit"].apply(
        lambda x: str(int(x)) if pd.notna(x) else "—"
    )

    st.dataframe(
        df_anz[[
            "Gemeinde", "Kt", "Region",
            "Bev_2014_fmt", "Bev_2024_fmt", "Kont_fmt",
            "Wachst_fmt", "Wachstumsrate_Pct", "Limit_Jahr", "Jahre_Anzeige",
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Gemeinde":        st.column_config.TextColumn("Gemeinde"),
            "Kt":              st.column_config.TextColumn("Kt.", width="small"),
            "Region":          st.column_config.TextColumn("Region / VK"),
            "Bev_2014_fmt":    st.column_config.TextColumn("Bev. 2014"),
            "Bev_2024_fmt":    st.column_config.TextColumn("Bev. 2024"),
            "Kont_fmt":        st.column_config.TextColumn("Kontingent"),
            "Wachst_fmt":      st.column_config.TextColumn("Verf. Wachstum"),
            "Wachstumsrate_Pct": st.column_config.NumberColumn(
                "Wachstumsrate p.a. (%)", format="%.2f %%"),
            "Limit_Jahr":      st.column_config.TextColumn("Limit erreicht"),
            "Jahre_Anzeige":   st.column_config.TextColumn("Jahre bis Limit"),
        },
        height=600,
    )


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


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Bevölkerungsdaten: Bundesamt für Statistik, Bilanz der ständigen Wohnbevölkerung "
    "nach Bezirken und Gemeinden, 1991–2024  ·  "
    "Methodik: Proportionale Zuteilung des nationalen Kontingents  ·  "
    "Gemeindegrenzen: © swisstopo (geo.admin.ch)"
)
