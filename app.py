import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk

st.set_page_config(
    page_title="10-Mio-Initiative: Wachstumspotenzial Seeland/Biel",
    page_icon="🏘️",
    layout="wide",
)

# ── Koordinaten ─────────────────────────────────────────────────────────────
KOORDINATEN = {
    "Bettlach":              (47.202, 7.413),
    "Grenchen":              (47.192, 7.397),
    "Selzach":               (47.207, 7.469),
    "Aegerten":              (47.113, 7.258),
    "Bellmund":              (47.113, 7.244),
    "Biel/Bienne":           (47.137, 7.247),
    "Brügg":                 (47.124, 7.244),
    "Bühl":                  (47.105, 7.234),
    "Epsach":                (47.077, 7.217),
    "Evilard":               (47.148, 7.241),
    "Hagneck":               (47.070, 7.220),
    "Hermrigen":             (47.073, 7.178),
    "Ipsach":                (47.107, 7.220),
    "Jens":                  (47.080, 7.203),
    "Lengnau (BE)":          (47.178, 7.369),
    "Ligerz":                (47.086, 7.136),
    "Merzligen":             (47.075, 7.198),
    "Mörigen":               (47.088, 7.163),
    "Nidau":                 (47.124, 7.234),
    "Orpund":                (47.155, 7.312),
    "Port":                  (47.120, 7.258),
    "Safnern":               (47.168, 7.325),
    "Scheuren":              (47.102, 7.251),
    "Schwadernau":           (47.085, 7.233),
    "Studen (BE)":           (47.109, 7.278),
    "Sutz-Lattrigen":        (47.095, 7.168),
    "Twann-Tüscherz":        (47.093, 7.145),
    "Worben":                (47.095, 7.269),
    "Aarberg":               (47.036, 7.278),
    "Arch":                  (47.155, 7.469),
    "Bargen (BE)":           (47.176, 7.305),
    "Brüttelen":             (47.027, 7.178),
    "Büetigen":              (47.127, 7.393),
    "Büren an der Aare":     (47.138, 7.374),
    "Diessbach bei Büren":   (47.128, 7.410),
    "Dotzigen":              (47.116, 7.352),
    "Erlach":                (47.041, 7.094),
    "Finsterhennen":         (47.030, 7.162),
    "Gals":                  (47.010, 7.063),
    "Gampelen":              (47.004, 7.058),
    "Grossaffoltern":        (47.053, 7.325),
    "Ins":                   (46.993, 7.100),
    "Kallnach":              (47.049, 7.206),
    "Kappelen":              (47.043, 7.278),
    "Leuzigen":              (47.152, 7.438),
    "Lyss":                  (47.074, 7.306),
    "Lüscherz":              (47.022, 7.112),
    "Meienried":             (47.119, 7.378),
    "Meinisberg":            (47.160, 7.340),
    "Müntschemier":          (46.993, 7.073),
    "Oberwil bei Büren":     (47.147, 7.386),
    "Pieterlen":             (47.166, 7.356),
    "Radelfingen":           (47.047, 7.240),
    "Rapperswil (BE)":       (47.098, 7.316),
    "Rüti bei Büren":        (47.127, 7.430),
    "Schüpfen":              (47.032, 7.363),
    "Seedorf (BE)":          (47.082, 7.249),
    "Siselen":               (47.033, 7.151),
    "Treiten":               (47.016, 7.140),
    "Tschugg":               (47.023, 7.083),
    "Täuffelen":             (47.052, 7.175),
    "Vinelz":                (47.031, 7.123),
    "Walperswil":            (47.043, 7.165),
    "Wengi":                 (47.150, 7.466),
}

# ── Daten laden ──────────────────────────────────────────────────────────────
@st.cache_data
def lade_daten():
    df = pd.read_excel(
        "10Mio_Initiative_Seeland_Biel.xlsx",
        sheet_name="Gemeindeübersicht",
        header=8,          # Zeile 9 (0-basiert: 8) als Header
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

    # Koordinaten
    df["lat"] = df["Gemeinde"].map(lambda g: KOORDINATEN.get(g, (47.10, 7.25))[0])
    df["lon"] = df["Gemeinde"].map(lambda g: KOORDINATEN.get(g, (47.10, 7.25))[1])

    # Farbe nach Dringlichkeit (RGBA)
    def farbe(row):
        if row["Schrumpfend"] or row["Verf_Wachstum"] < 50:
            return [220, 50, 50, 200]    # rot
        elif row["Verf_Wachstum"] < 200:
            return [230, 120, 30, 200]   # orange
        elif row["Verf_Wachstum"] < 500:
            return [230, 200, 30, 200]   # gelb
        else:
            return [60, 180, 80, 200]    # grün

    df["farbe"] = df.apply(farbe, axis=1)

    # Radius proportional zur Bevölkerung (min 300, max 2500)
    max_bev = df["Bev_2024"].max()
    df["radius"] = (df["Bev_2024"] / max_bev * 2200 + 300).round(0)

    # Wachstumsrate in Prozent für Anzeige
    df["Wachstumsrate_Pct"] = (df["Wachstumsrate"] * 100).round(2)

    return df


df_roh = lade_daten()

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🏘️ 10-Millionen-Initiative: Wachstumspotenzial im Seeland/Biel")
st.markdown(
    """
    Die **10-Millionen-Initiative** will die Einwohnerzahl der Schweiz bei **10 Millionen** deckeln.
    Ende 2024 leben **9'051'029** Personen in der Schweiz — es blieben noch **948'971** Plätze übrig (+10,5 %).
    Dieses verbleibende Kontingent wird proportional auf alle Gemeinden verteilt.
    Die Karte und Grafiken zeigen, wie viel Spielraum jede Seeländer Gemeinde noch hat.
    """
)
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filter")

    suche = st.text_input("🔍 Gemeinde suchen", "")

    alle_regionen = sorted(df_roh["Region"].unique().tolist())
    ausgewaehlte_regionen = st.multiselect(
        "Region / VK", alle_regionen, default=alle_regionen
    )

    wachstum_min = int(df_roh["Verf_Wachstum"].min())
    wachstum_max = int(df_roh["Verf_Wachstum"].max())
    wachstum_range = st.slider(
        "Verfügbares Wachstum (Personen)",
        min_value=wachstum_min,
        max_value=wachstum_max,
        value=(wachstum_min, wachstum_max),
    )

    schrumpfend_zeigen = st.toggle("Schrumpfende Gemeinden anzeigen", value=True)

    st.divider()
    st.markdown("**Legende Dringlichkeit**")
    st.markdown("🟢 > 500 Personen Spielraum")
    st.markdown("🟡 200–500 Personen")
    st.markdown("🟠 50–200 Personen")
    st.markdown("🔴 < 50 oder schrumpfend")

# ── Filter anwenden ───────────────────────────────────────────────────────────
df = df_roh.copy()

if suche:
    df = df[df["Gemeinde"].str.contains(suche, case=False, na=False)]

if ausgewaehlte_regionen:
    df = df[df["Region"].isin(ausgewaehlte_regionen)]

df = df[
    (df["Verf_Wachstum"] >= wachstum_range[0]) &
    (df["Verf_Wachstum"] <= wachstum_range[1])
]

if not schrumpfend_zeigen:
    df = df[~df["Schrumpfend"]]

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_karte, tab_tabelle, tab_charts = st.tabs(["🗺️ Karte", "📋 Tabelle", "📊 Charts"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1: KARTE
# ════════════════════════════════════════════════════════════════════════════
with tab_karte:
    if df.empty:
        st.warning("Keine Gemeinden mit den aktuellen Filtereinstellungen.")
    else:
        tooltip = {
            "html": """
            <b>{Gemeinde}</b> ({Kt})<br/>
            Bevölkerung 2024: <b>{Bev_2024}</b><br/>
            Kontingent (10 Mio): <b>{Kontingent}</b><br/>
            Verfügbares Wachstum: <b>{Verf_Wachstum}</b> Pers.<br/>
            Wachstumsrate p.a.: <b>{Wachstumsrate_Pct} %</b><br/>
            Limit erreicht: <b>{Limit_Jahr}</b>
            """,
            "style": {
                "backgroundColor": "white",
                "color": "black",
                "fontSize": "13px",
                "padding": "8px",
                "border": "1px solid #ccc",
            },
        }

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position="[lon, lat]",
            get_fill_color="farbe",
            get_radius="radius",
            pickable=True,
            opacity=0.85,
        )

        view_state = pdk.ViewState(
            latitude=df["lat"].mean(),
            longitude=df["lon"].mean(),
            zoom=10,
            pitch=0,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        )
        st.pydeck_chart(deck, use_container_width=True)

        # Legende
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🟢 Viel Spielraum (>500)", len(df[df["Verf_Wachstum"] >= 500]))
        col2.metric("🟡 Mittel (200–500)", len(df[(df["Verf_Wachstum"] >= 200) & (df["Verf_Wachstum"] < 500)]))
        col3.metric("🟠 Wenig (50–200)", len(df[(df["Verf_Wachstum"] >= 50) & (df["Verf_Wachstum"] < 200) & ~df["Schrumpfend"]]))
        col4.metric("🔴 Kritisch (<50 / schrumpfend)", len(df[(df["Verf_Wachstum"] < 50) | df["Schrumpfend"]]))


# ════════════════════════════════════════════════════════════════════════════
# TAB 2: TABELLE
# ════════════════════════════════════════════════════════════════════════════
with tab_tabelle:
    # Zusammenfassung
    c1, c2, c3 = st.columns(3)
    c1.metric("Gemeinden (gefiltert)", len(df))
    c2.metric("Gesamtbevölkerung", f"{df['Bev_2024'].sum():,.0f}".replace(",", "'"))
    c3.metric("Gesamtspielraum", f"{df['Verf_Wachstum'].sum():,.0f}".replace(",", "'") + " Pers.")

    st.divider()

    df_anzeige = df[[
        "Gemeinde", "Kt", "Region", "Bev_2024", "Kontingent",
        "Verf_Wachstum", "Wachstumsrate_Pct", "Limit_Jahr",
    ]].copy()

    st.dataframe(
        df_anzeige,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Gemeinde":         st.column_config.TextColumn("Gemeinde"),
            "Kt":               st.column_config.TextColumn("Kt.", width="small"),
            "Region":           st.column_config.TextColumn("Region / VK"),
            "Bev_2024":         st.column_config.NumberColumn("Bev. 2024", format="%d"),
            "Kontingent":       st.column_config.NumberColumn("Kontingent", format="%d"),
            "Verf_Wachstum":    st.column_config.ProgressColumn(
                "Verfügbares Wachstum",
                format="%d Pers.",
                min_value=int(df_roh["Verf_Wachstum"].min()),
                max_value=int(df_roh["Verf_Wachstum"].max()),
            ),
            "Wachstumsrate_Pct": st.column_config.NumberColumn(
                "Wachstumsrate p.a. (%)",
                format="%.2f %%",
            ),
            "Limit_Jahr":       st.column_config.TextColumn("Limit erreicht"),
        },
        height=600,
    )


# ════════════════════════════════════════════════════════════════════════════
# TAB 3: CHARTS
# ════════════════════════════════════════════════════════════════════════════
with tab_charts:

    def dringlichkeit_farbe(limit_jahr, schrumpfend, verf_wachstum):
        if schrumpfend or verf_wachstum < 50:
            return "#DC3232"
        try:
            jahr = int(limit_jahr)
            if jahr <= 2035:
                return "#E07820"
            elif jahr <= 2050:
                return "#E0C820"
            else:
                return "#3CB450"
        except (ValueError, TypeError):
            return "#3CB450"

    # ── Chart 1: Top 15 schnellstwachsende Gemeinden ────────────────────────
    st.subheader("Top 15 schnellstwachsende Gemeinden (CAGR p.a.)")

    df_wachstum = df.nlargest(15, "Wachstumsrate").copy()
    df_wachstum["farbe_chart"] = df_wachstum.apply(
        lambda r: dringlichkeit_farbe(r["Limit_Jahr"], r["Schrumpfend"], r["Verf_Wachstum"]), axis=1
    )

    fig1 = px.bar(
        df_wachstum.sort_values("Wachstumsrate"),
        x="Wachstumsrate_Pct",
        y="Gemeinde",
        orientation="h",
        color="farbe_chart",
        color_discrete_map="identity",
        labels={"Wachstumsrate_Pct": "Wachstumsrate p.a. (%)", "Gemeinde": ""},
        text="Wachstumsrate_Pct",
    )
    fig1.update_traces(texttemplate="%{text:.2f} %", textposition="outside")
    fig1.update_layout(
        showlegend=False,
        height=450,
        margin=dict(l=0, r=80, t=20, b=20),
        xaxis_title="Wachstumsrate p.a. (%)",
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ── Chart 2: Wenigster Spielraum ─────────────────────────────────────────
    st.subheader("Gemeinden mit geringstem verfügbarem Wachstum")

    df_spielraum = df.nsmallest(20, "Verf_Wachstum").copy()
    df_spielraum["farbe_chart"] = df_spielraum.apply(
        lambda r: dringlichkeit_farbe(r["Limit_Jahr"], r["Schrumpfend"], r["Verf_Wachstum"]), axis=1
    )

    fig2 = px.bar(
        df_spielraum.sort_values("Verf_Wachstum"),
        x="Verf_Wachstum",
        y="Gemeinde",
        orientation="h",
        color="farbe_chart",
        color_discrete_map="identity",
        labels={"Verf_Wachstum": "Verfügbares Wachstum (Personen)", "Gemeinde": ""},
        text="Verf_Wachstum",
    )
    fig2.update_traces(texttemplate="%{text} Pers.", textposition="outside")
    fig2.update_layout(
        showlegend=False,
        height=500,
        margin=dict(l=0, r=100, t=20, b=20),
        xaxis_title="Verfügbares Wachstum (Personen)",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Chart 3: Scatter Bevölkerung vs. Spielraum ───────────────────────────
    st.subheader("Bevölkerung vs. verfügbares Wachstum")

    df_scatter = df.copy()
    df_scatter["Wachstumsrate_abs"] = df_scatter["Wachstumsrate"].abs() * 100

    # Outlier-Labels: Biel/Bienne + wer am meisten/wenigsten Spielraum hat
    top_spielraum = df_scatter.nlargest(3, "Verf_Wachstum")["Gemeinde"].tolist()
    bottom_spielraum = df_scatter.nsmallest(4, "Verf_Wachstum")["Gemeinde"].tolist()
    groesste = df_scatter.nlargest(2, "Bev_2024")["Gemeinde"].tolist()
    labels_set = set(top_spielraum + bottom_spielraum + groesste)
    df_scatter["label"] = df_scatter["Gemeinde"].apply(lambda g: g if g in labels_set else "")

    fig3 = px.scatter(
        df_scatter,
        x="Bev_2024",
        y="Verf_Wachstum",
        color="Region",
        size="Wachstumsrate_abs",
        size_max=25,
        hover_name="Gemeinde",
        hover_data={
            "Bev_2024": True,
            "Verf_Wachstum": True,
            "Wachstumsrate_Pct": True,
            "Limit_Jahr": True,
            "Wachstumsrate_abs": False,
            "Region": False,
        },
        text="label",
        labels={
            "Bev_2024": "Bevölkerung 2024",
            "Verf_Wachstum": "Verfügbares Wachstum (Personen)",
            "Wachstumsrate_Pct": "Wachstumsrate p.a. (%)",
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
    "Methodik: Proportionale Zuteilung des nationalen Kontingents"
)
