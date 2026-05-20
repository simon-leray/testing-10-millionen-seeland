# 10-Millionen-Initiative: Wachstumspotenzial Seeland/Biel

Interaktive Streamlit-App, die zeigt, wie viel Bevölkerungswachstum jede Gemeinde im Seeland/Biel noch zulassen kann, falls die **10-Millionen-Initiative** angenommen wird.

## Hintergrund

Die Initiative will die Einwohnerzahl der Schweiz bei 10 Millionen deckeln. Ende 2024 leben 9'051'029 Personen in der Schweiz — es verbleiben +10,5 % Spielraum. Dieser wird proportional auf alle Gemeinden verteilt.

## Lokal ausführen

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2. App starten
streamlit run app.py
```

Die Datei `10Mio_Initiative_Seeland_Biel.xlsx` muss im gleichen Verzeichnis wie `app.py` liegen.

## Datenquellen

- Bevölkerungsdaten: Bieler Tagblatt / kant. Statistikämter
- CH-Gesamtbevölkerung: BFS, Ende 2024 (9'051'029)
- Methodik: Proportionale Zuteilung des nationalen Kontingents
