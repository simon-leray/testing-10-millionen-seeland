import concurrent.futures
import re

import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests
import streamlit as st

st.set_page_config(
    page_title="10-Mio-Initiative: Wachstumspotenzial Seeland/Biel",
    page_icon="🏘️",
    layout="wide",
)

AKTUELLES_JAHR = 2026
FIND_URL = (
    "https://api3.geo.admin.ch/rest/services/api/MapServer/find"
)

# Koordinaten für Fallback-Punktkarte
KOORDINATEN = {
    "Bettlach": (47.202, 7.413), "Grenchen": (47.192, 7.397),
    "Selzach": (47.207, 7.469), "Aegerten": (47.113, 7.258),
    "Bellmund": (47.113, 7.244), "Biel/Bienne": (47.137, 7.247),
    "Brügg": (47.124, 7.244), "Bühl": (47.105, 7.234),
    "Epsach": (47.077, 7.217), "Evilard": (47.148, 7.241),
    "Hagneck": (47.070, 7.220), "Hermrigen": (47.073, 7.178),
    "Ipsach": (47.107, 7.220), "Jens": (47.080, 7.203),
    "Lengnau (BE)": (47.178, 7.369), "Ligerz": (47.086, 7.136),
    "Merzligen": (47.075, 7.198), "Mörigen": (47.088, 7.163),
    "Nidau": (47.124, 7.234), "Orpund": (47.155, 7.312),
    "Port": (47.120, 7.258), "Safnern": (47.168, 7.325),
    "Scheuren": (47.102, 7.251), "Schwadernau": (47.085, 7.233),
    "Studen (BE)": (47.109, 7.278), "Sutz-Lattrigen": (47.095, 7.168),
    "Twann-Tüscherz": (47.093, 7.145), "Worben": (47.095, 7.269),
    "Aarberg": (47.036, 7.278), "Arch": (47.155, 7.469),
    "Bargen (BE)": (47.176, 7.305), "Brüttelen": (47.027, 7.178),
    "Büetigen": (47.127, 7.393), "Büren an der Aare": (47.138, 7.374),
    "Diessbach bei Büren": (47.128, 7.410), "Dotzigen": (47.116, 7.352),
    "Erlach": (47.041, 7.094), "Finsterhennen": (47.030, 7.162),
    "Gals": (47.010, 7.063), "Gampelen": (47.004, 7.058),
    "Grossaffoltern": (47.053, 7.325), "Ins": (46.993, 7.100),
    "Kallnach": (47.049, 7.206), "Kappelen": (47.043, 7.278),
    "Leuzigen": (47.152, 7.438), "Lyss": (47.074, 7.306),
    "Lüscherz": (47.022, 7.112), "Meienried": (47.119, 7.378),
    "Meinisberg": (47.160, 7.340), "Müntschemier": (46.993, 7.073),
    "Oberwil bei Büren": (47.147, 7.386), "Pieterlen": (47.166, 7.356),
    "Radelfingen": (47.047, 7.240), "Rapperswil (BE)": (47.098, 7.316),
    "Rüti bei Büren": (47.127, 7.430), "Schüpfen": (47.032, 7.363),
    "Seedorf (BE)": (47.082, 7.249), "Siselen": (47.033, 7.151),
    "Treiten": (47.016, 7.140), "Tschugg": (47.023, 7.083),
    "Täuffelen": (47.052, 7.175), "Vinelz": (47.031, 7.123),
    "Walperswil": (47.043, 7.165), "Wengi": (47.150, 7.466),
}


# ── Hilfsfunktionen ──────────────────────────────────────────────────────────

def normiere_name(name: str) -> str:
    return re.sub(r"\s*\([^)]+\)", "", name).strip()


def zeitfarbe(jahre, schrumpfend) -> list:
    """RGBA-Farbe nach Jahren bis zum Limit."""
    if schrumpfend or jahre is None:
        return [100, 120, 190, 200]
    if jahre <= 4:
        return [215, 35, 35, 210]
    elif jahre <= 14:
        return [215, 105, 15, 210]
    elif jahre <= 34:
        return [205, 185, 10, 210]
    else:
        return [45, 165, 60, 210]


def zeitfarbe_hex(jahre, schrumpfend) -> str:
    r, g, b, _ = zeitfarbe(jahre, schrumpfend)
    return f"#{r:02x}{g:02x}{b:02x}"


# ── Daten laden ───────────────────────────────────────────────────────────────

@st.cache_data
def lade_daten():
    df = pd.read_excel(
        "10Mio_Initiative_Seeland_Biel.xlsx",
        sheet_name="Gemeindeübersicht",
        header=8,
        usecols="A:H",
        nrows=64,
    )
    df.columns = [
        "Gemeinde", "Kt", "Region",
        "Bev_2024", "Kontingent", "Verf_Wachstum",
        "Wachstumsrate", "Limit_Jahr",
    ]
    df = df.dropna(subset=["Gemeinde"])
    df["Gemeinde"] = df["Gemeinde"].str.strip()
    df["Kt"] = df["Kt"].str.strip()
    df["Region"] = df["Region"].str.strip()
    df["Bev_2024"] = pd.to_numeric(df["Bev_2024"], errors="coerce")
    df["Kontingent"] = pd.to_numeric(df["Kontingent"], errors="coerce")
    df["Verf_Wachstum"] = pd.to_numeric(df["Verf_Wachstum"], errors="coerce")
    df["Wachstumsrate"] = pd.to_numeric(df["Wachstumsrate"], errors="coerce")
    df["Limit_Jahr"] = df["Limit_Jahr"].astype(str).str.strip()
    df["Schrumpfend"] = df["Limit_Jahr"].str.contains("schrumpfend|Kein", case=False, na=False)
    df["Wachstumsrate_Pct"] = (df["Wachstumsrate"] * 100).round(2)

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


@st.cache_data(ttl=86400, show_spinner="Lade Gemeindegrenzen von swisstopo …")
def lade_geometrien(gemeinden_mit_kanton: tuple) -> dict:
    """
    Lädt für jede Gemeinde die aktuellen Polygongrenzen über den geo.admin.ch
    find-Endpunkt (parallele Anfragen, einmal täglich gecacht).
    Gibt ein dict {Gemeindename: rings} zurück.
    """
    def hole_eine(gemeinde, kanton):
        suchname = normiere_name(gemeinde)
        params = {
            "layer": "ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill",
            "searchField": "gemname",
            "searchText": suchname,
            "returnGeometry": "true",
            "sr": "4326",
            "f": "json",
        }
        try:
            r = requests.get(FIND_URL, params=params, timeout=20)
            r.raise_for_status()
            results = r.json().get("results", [])
            # Aktuelle Gemeinde, bevorzugt mit passendem Kanton
            aktuell = [x for x in results if x.get("attributes", {}).get("is_current_jahr")]
            if not aktuell:
                # Fallback: neuestes Jahr
                aktuell = sorted(
                    results, key=lambda x: x.get("attributes", {}).get("jahr", 0), reverse=True
                )[:1]
            # Kantonsfilter bei Namenskonflikten
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
    """
    Baut flache Dicts für pydeck PolygonLayer.
    'polygon' enthält die Rings direkt — kein GeoJSON-Nesting nötig.
    """
    rows = []
    for _, row in df_filtered.iterrows():
        rings = geometrien.get(row["Gemeinde"])
        if not rings:
            continue
        jahre = row["Jahre_bis_Limit"]
        farbe = zeitfarbe(jahre, row["Schrumpfend"])
        jahre_text = f"{int(jahre)} Jahre" if pd.notna(jahre) else "Schrumpfend"

        rows.append({
            "polygon": rings,          # PolygonLayer liest rings direkt
            "color": farbe,            # [R, G, B, A] — direkt referenzierbar
            "Gemeinde": row["Gemeinde"],
            "Kt": row["Kt"],
            "Bev_2024": int(row["Bev_2024"]),
            "Kontingent": int(row["Kontingent"]),
            "Verf_Wachstum": int(row["Verf_Wachstum"]),
            "Wachstumsrate_Pct": float(row["Wachstumsrate_Pct"]),
            "Limit_Jahr": row["Limit_Jahr"],
            "Jahre_bis_Limit": jahre_text,
        })
    return rows


# ── App-Initialisierung ───────────────────────────────────────────────────────
df_roh = lade_daten()

gemeinden_tuple = tuple(zip(df_roh["Gemeinde"].tolist(), df_roh["Kt"].tolist()))
geometrien = lade_geometrien(gemeinden_tuple)
api_verfuegbar = len(geometrien) >= 30  # mind. die Hälfte muss geladen sein

jahre_vals = df_roh["Jahre_bis_Limit"].dropna()
jahre_min = int(jahre_vals.min())
jahre_max = int(jahre_vals.max())

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏘️ 10-Millionen-Initiative: Wachstumspotenzial im Seeland/Biel")
st.markdown(
    """
    Die **10-Millionen-Initiative** will die Einwohnerzahl der Schweiz bei **10 Millionen** deckeln.
    Ende 2024 leben **9'051'029** Personen in der Schweiz — es bleiben noch **948'971** Plätze übrig (+10,5 %).
    Dieses Kontingent wird proportional auf alle Gemeinden verteilt.
    Die Farben zeigen, **wie viele Jahre** jede Gemeinde bei aktuellem Wachstum noch hat,
    bis sie ihr Kontingent ausschöpft.
    """
)
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filter")

    suche = st.text_input("🔍 Gemeinde suchen", "")

    jahre_range = st.slider(
        "Jahre bis Limit (ab 2026)",
        min_value=jahre_min,
        max_value=jahre_max,
        value=(jahre_min, jahre_max),
        help=(
            "Filtert nach der geschätzten Restzeit bis das Bevölkerungskontingent "
            "ausgeschöpft wird. Schrumpfende Gemeinden über den Toggle steuerbar."
        ),
    )

    schrumpfend_zeigen = st.toggle("Schrumpfende Gemeinden anzeigen", value=True)

    st.divider()
    st.markdown("**Legende — Jahre bis Limit**")
    st.markdown("🔴 Weniger als 5 Jahre (bis 2030)")
    st.markdown("🟠 5–14 Jahre (2031–2040)")
    st.markdown("🟡 15–34 Jahre (2041–2060)")
    st.markdown("🟢 Mehr als 34 Jahre (ab 2061)")
    st.markdown("🔵 Schrumpfend — kein Limit in Sicht")
    if not api_verfuegbar:
        st.divider()
        st.caption("⚠️ Gemeindegrenzen nicht verfügbar — Punktkarte aktiv")

# ── Filter anwenden ───────────────────────────────────────────────────────────
df = df_roh.copy()
if suche:
    df = df[df["Gemeinde"].str.contains(suche, case=False, na=False)]

df_wachsend = df[~df["Schrumpfend"]].copy()
df_wachsend = df_wachsend[
    (df_wachsend["Jahre_bis_Limit"] >= jahre_range[0])
    & (df_wachsend["Jahre_bis_Limit"] <= jahre_range[1])
]
df_schrumpf = df[df["Schrumpfend"]].copy() if schrumpfend_zeigen else pd.DataFrame()
df = pd.concat([df_wachsend, df_schrumpf], ignore_index=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_karte, tab_tabelle, tab_charts = st.tabs(["🗺️ Karte", "📋 Tabelle", "📊 Charts"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1: KARTE
# ════════════════════════════════════════════════════════════════════════════
with tab_karte:
    if df.empty:
        st.warning("Keine Gemeinden mit den aktuellen Filtereinstellungen.")
    elif not api_verfuegbar:
        # ── Fallback: Punktkarte ─────────────────────────────────────────
        st.info("Gemeindegrenzen konnten nicht geladen werden — Darstellung als Punkte.")
        df["farbe"] = df.apply(lambda r: zeitfarbe(r["Jahre_bis_Limit"], r["Schrumpfend"]), axis=1)
        max_bev = df_roh["Bev_2024"].max()
        df["radius"] = (df["Bev_2024"] / max_bev * 2200 + 300).round(0)
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position="[lon, lat]",
            get_fill_color="farbe",
            get_radius="radius",
            pickable=True,
            opacity=0.85,
        )
        view = pdk.ViewState(latitude=df["lat"].mean(), longitude=df["lon"].mean(), zoom=10)
        st.pydeck_chart(
            pdk.Deck(
                layers=[layer], initial_view_state=view,
                map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            ),
            use_container_width=True,
        )
    else:
        # ── Hauptkarte: Polygone ─────────────────────────────────────────
        features = erstelle_polygon_features(df, geometrien)

        if not features:
            st.warning("Keine Polygone für die gewählten Gemeinden verfügbar.")
        else:
            tooltip = {
                "html": """
                <div style='font-family:sans-serif;font-size:13px;min-width:210px'>
                <b style='font-size:15px'>{Gemeinde}</b>&nbsp;({Kt})<br/>
                <hr style='margin:5px 0;border-color:#ddd'/>
                Bevölkerung 2024: <b>{Bev_2024}</b><br/>
                Kontingent (10 Mio): <b>{Kontingent}</b><br/>
                Verfügbares Wachstum: <b>{Verf_Wachstum}&nbsp;Pers.</b><br/>
                Wachstumsrate p.a.: <b>{Wachstumsrate_Pct}&nbsp;%</b><br/>
                Limit erreicht: <b>{Limit_Jahr}</b><br/>
                Verbleibende Zeit: <b>{Jahre_bis_Limit}</b>
                </div>""",
                "style": {
                    "backgroundColor": "white",
                    "color": "#222",
                    "border": "1px solid #ddd",
                    "borderRadius": "5px",
                    "padding": "10px",
                    "boxShadow": "2px 2px 6px rgba(0,0,0,0.15)",
                },
            }

            layer = pdk.Layer(
                "PolygonLayer",
                data=features,
                get_polygon="polygon",
                get_fill_color="color",
                get_line_color=[60, 60, 60, 160],
                line_width_min_pixels=1,
                pickable=True,
                filled=True,
                stroked=True,
                opacity=0.85,
            )

            st.pydeck_chart(
                pdk.Deck(
                    layers=[layer],
                    initial_view_state=pdk.ViewState(
                        latitude=47.09, longitude=7.24, zoom=10, pitch=0
                    ),
                    tooltip=tooltip,
                    map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
                ),
                use_container_width=True,
            )

    # ── Metriken ─────────────────────────────────────────────────────────
    st.divider()
    df_w = df[~df["Schrumpfend"]]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🔴 Bis 2030",       len(df_w[df_w["Jahre_bis_Limit"] <= 4]))
    c2.metric("🟠 2031–2040",      len(df_w[(df_w["Jahre_bis_Limit"] > 4)  & (df_w["Jahre_bis_Limit"] <= 14)]))
    c3.metric("🟡 2041–2060",      len(df_w[(df_w["Jahre_bis_Limit"] > 14) & (df_w["Jahre_bis_Limit"] <= 34)]))
    c4.metric("🟢 Ab 2061",        len(df_w[df_w["Jahre_bis_Limit"] > 34]))
    c5.metric("🔵 Schrumpfend",    len(df[df["Schrumpfend"]]))


# ════════════════════════════════════════════════════════════════════════════
# TAB 2: TABELLE
# ════════════════════════════════════════════════════════════════════════════
with tab_tabelle:
    c1, c2, c3 = st.columns(3)
    c1.metric("Gemeinden (gefiltert)", len(df))
    c2.metric("Gesamtbevölkerung", f"{df['Bev_2024'].sum():,.0f}".replace(",", "'"))
    c3.metric("Gesamtspielraum",
              f"{df['Verf_Wachstum'].sum():,.0f}".replace(",", "'") + " Pers.")
    st.divider()

    df_anz = df[[
        "Gemeinde", "Kt", "Region", "Bev_2024", "Kontingent",
        "Verf_Wachstum", "Wachstumsrate_Pct", "Limit_Jahr", "Jahre_bis_Limit",
    ]].copy()
    df_anz["Jahre_Anzeige"] = df_anz["Jahre_bis_Limit"].apply(
        lambda x: str(int(x)) if pd.notna(x) else "—"
    )

    st.dataframe(
        df_anz.drop(columns=["Jahre_bis_Limit"]),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Gemeinde":         st.column_config.TextColumn("Gemeinde"),
            "Kt":               st.column_config.TextColumn("Kt.", width="small"),
            "Region":           st.column_config.TextColumn("Region / VK"),
            "Bev_2024":         st.column_config.NumberColumn("Bev. 2024", format="%d"),
            "Kontingent":       st.column_config.NumberColumn("Kontingent", format="%d"),
            "Verf_Wachstum":    st.column_config.ProgressColumn(
                "Verf. Wachstum",
                format="%d Pers.",
                min_value=int(df_roh["Verf_Wachstum"].min()),
                max_value=int(df_roh["Verf_Wachstum"].max()),
            ),
            "Wachstumsrate_Pct": st.column_config.NumberColumn(
                "Wachstumsrate p.a. (%)", format="%.2f %%"
            ),
            "Limit_Jahr":       st.column_config.TextColumn("Limit erreicht"),
            "Jahre_Anzeige":    st.column_config.TextColumn("Jahre bis Limit"),
        },
        height=600,
    )


# ════════════════════════════════════════════════════════════════════════════
# TAB 3: CHARTS
# ════════════════════════════════════════════════════════════════════════════
with tab_charts:

    # ── Chart 1: Top 15 schnellstwachsende Gemeinden ────────────────────────
    st.subheader("Top 15 schnellstwachsende Gemeinden (CAGR p.a.)")

    df_w1 = df.nlargest(15, "Wachstumsrate").copy()
    df_w1["farbe_chart"] = df_w1.apply(
        lambda r: zeitfarbe_hex(r["Jahre_bis_Limit"], r["Schrumpfend"]), axis=1
    )
    fig1 = px.bar(
        df_w1.sort_values("Wachstumsrate"),
        x="Wachstumsrate_Pct", y="Gemeinde", orientation="h",
        color="farbe_chart", color_discrete_map="identity",
        labels={"Wachstumsrate_Pct": "Wachstumsrate p.a. (%)", "Gemeinde": ""},
        text="Wachstumsrate_Pct",
    )
    fig1.update_traces(texttemplate="%{text:.2f} %", textposition="outside")
    fig1.update_layout(
        showlegend=False, height=450,
        margin=dict(l=0, r=80, t=20, b=20),
        xaxis_title="Wachstumsrate p.a. (%)",
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ── Chart 2: Kürzester Zeitpuffer ────────────────────────────────────────
    st.subheader("Gemeinden mit dem kürzesten Zeitpuffer bis zum Limit")

    df_puffer = df[~df["Schrumpfend"]].nsmallest(20, "Jahre_bis_Limit").copy()
    df_puffer["farbe_chart"] = df_puffer.apply(
        lambda r: zeitfarbe_hex(r["Jahre_bis_Limit"], r["Schrumpfend"]), axis=1
    )
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
        texttemplate="%{text} J. (%{customdata[0]})",
        textposition="outside",
    )
    fig2.update_layout(
        showlegend=False, height=500,
        margin=dict(l=0, r=130, t=20, b=20),
        xaxis_title="Jahre bis Limit",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Chart 3: Scatter Bevölkerung vs. Spielraum ───────────────────────────
    st.subheader("Bevölkerung vs. verfügbares Wachstum")

    df_sc = df.copy()
    df_sc["Wachstumsrate_abs"] = df_sc["Wachstumsrate"].abs() * 100
    df_sc["Jahre_text"] = df_sc["Jahre_bis_Limit"].apply(
        lambda x: str(int(x)) if pd.notna(x) else "Schrumpfend"
    )
    top3 = df_sc.nlargest(3, "Verf_Wachstum")["Gemeinde"].tolist()
    bottom4 = df_sc[~df_sc["Schrumpfend"]].nsmallest(4, "Jahre_bis_Limit")["Gemeinde"].tolist()
    groesste = df_sc.nlargest(2, "Bev_2024")["Gemeinde"].tolist()
    labels_set = set(top3 + bottom4 + groesste)
    df_sc["label"] = df_sc["Gemeinde"].apply(lambda g: g if g in labels_set else "")

    fig3 = px.scatter(
        df_sc,
        x="Bev_2024", y="Verf_Wachstum",
        color="Region", size="Wachstumsrate_abs", size_max=25,
        hover_name="Gemeinde",
        hover_data={
            "Bev_2024": True,
            "Verf_Wachstum": True,
            "Wachstumsrate_Pct": True,
            "Limit_Jahr": True,
            "Jahre_text": True,
            "Wachstumsrate_abs": False,
        },
        text="label",
        labels={
            "Bev_2024": "Bevölkerung 2024",
            "Verf_Wachstum": "Verfügbares Wachstum (Personen)",
            "Wachstumsrate_Pct": "Wachstumsrate p.a. (%)",
            "Jahre_text": "Jahre bis Limit",
        },
    )
    fig3.update_traces(textposition="top center", textfont_size=11)
    fig3.update_layout(
        height=520,
        margin=dict(l=0, r=0, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
    )
    st.plotly_chart(fig3, use_container_width=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Bevölkerungsdaten: Bieler Tagblatt / kant. Statistikämter | "
    "CH-Gesamtbevölkerung: BFS, Ende 2024 (9'051'029) | "
    "Methodik: Proportionale Zuteilung des nationalen Kontingents | "
    "Gemeindegrenzen: © swisstopo (geo.admin.ch)"
)
