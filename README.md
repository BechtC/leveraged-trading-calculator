# 🎯 Advanced Trading Risk Management Tool v2.0

Ein professionelles Streamlit-basiertes Tool für die **1% Risiko-Regel** mit erweiterten **Teilverkauf-Funktionen** nach dem Tiedje CROC System.

## 📋 Inhaltsverzeichnis

- [Features](#-features)
- [Installation](#-installation)
- [Verwendung](#-verwendung)
- [Tool-Übersicht](#-tool-übersicht)
- [Beispiel-Workflow](#-beispiel-workflow)
- [Daten-Management](#-daten-management)
- [Tipps & Tricks](#-tipps--tricks)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Features

### ✅ **Kern-Funktionen**
- **1% Risiko-Regel Berechnung** - Automatische Positionsgrößen-Bestimmung
- **R-Multiple Tracking** - Präzise Performance-Messung (1R, 2R, 5R)
- **Teilverkauf-Management** - Professionelle Gewinnmitnahme-Strategien
- **Portfolio-Tracking** - Cash- und Depot-Verwaltung in Echtzeit
- **Stop-Loss Trailing** - Automatisches Nachziehen auf Break-even

### 📊 **Analytics & Reporting**
- Performance-Vergleich: Teilverkäufe vs. Komplettverkauf
- R-Multiple Verteilungs-Charts
- Gewinn-Rate und Durchschnitts-Performance
- Detaillierte Trade-Historie mit Export-Funktionen

### 💾 **Daten-Management**
- **CSV-Export** für Excel-Analysen
- **JSON-Backup** für komplette Datensicherung
- **Persistent Storage** - Daten bleiben während Browser-Session erhalten

---

## 🛠️ Installation

### **Voraussetzungen**
- Python 3.7 oder höher
- Internetverbindung für Package-Installation

### **1. Python-Packages installieren**
Öffne **Command Prompt** oder **Terminal** und führe aus:

```bash
pip install streamlit pandas plotly uuid
```

### **2. Tool-Dateien**
Das Tool besteht aus einer einzigen Datei:
- `trading_app_advanced.py` - Hauptanwendung

### **3. Verzeichnis-Struktur**
```
C:\Users\Becht\Python-Projecte\Risiko-Calculator\
├── trading_app_advanced.py
└── README.md
```

---

## 🎮 Verwendung

### **🚀 Tool starten**

1. **Command Prompt öffnen**
   - `Windows + R` → `cmd` → Enter
   - Oder: Windows-Taste → "Command Prompt" eingeben

2. **In das Tool-Verzeichnis navigieren**
   ```cmd
   cd C:\Users\Becht\Python-Projecte\Risiko-Calculator
   ```

3. **Streamlit-App starten**
   ```cmd
   streamlit run trading_app_advanced.py
   ```

4. **Browser öffnet automatisch**
   - Standard-URL: `http://localhost:8501`
   - Falls nicht automatisch: URL in Browser eingeben

### **⏹️ Tool beenden**

**Option 1: Über Browser**
- Browser-Tab schließen

**Option 2: Über Command Prompt**
- Im Command Prompt: `Ctrl + C` drücken
- Bestätigen mit `Y` oder `J`

**Option 3: Complete Shutdown**
- Command Prompt komplett schließen

### **🔄 Tool neu starten**
Nach Code-Änderungen:
1. `Ctrl + C` im Command Prompt
2. `streamlit run trading_app_advanced.py` erneut ausführen

---

## 📱 Tool-Übersicht

### **Sidebar - Portfolio Konfiguration**
- **Gesamtes Depot-Wert**: Dein komplettes Portfolio
- **Verfügbares Cash**: Liquide Mittel für neue Trades
- **Risiko pro Trade**: Standard 1%, anpassbar 0.5% - 5%

### **Tab 1: 🎯 Trade Calculator**
**Zweck**: Neue Trades berechnen und planen

**Eingaben**:
- Symbol/Aktie (z.B. "NVIDIA", "AAPL")
- Entry Preis (Stopp-Buy Level)
- Stop-Loss (Risiko-Level)

**Ausgaben**:
- Anzahl Aktien (bei 1% Risiko)
- Position Wert & Depot-Anteil
- R-Multiple Targets (1R, 2R, 5R)

**Aktionen**:
- Als geplanten Trade speichern
- Als offene Position markieren (Cash wird abgezogen)

### **Tab 2: 📊 Offene Positionen**
**Zweck**: Aktive Trades verwalten

**Pro Position**:
- **Aktueller Preis eingeben** → Live P&L Berechnung
- **Teilverkäufe** (25%, 50%, 75%, 100%)
- **Stop-Loss Management** (Break-even, Trailing)
- **R-Multiple Tracking** in Echtzeit

**Automatik-Features**:
- Bei profitablem Teilverkauf → Stop automatisch auf Einstand
- Cash-Update bei Verkäufen
- Komplette Trade-Historie

### **Tab 3: 💰 Teilverkäufe**
**Zweck**: Analyse aller Teilverkäufe

**Metriken**:
- Teilverkäufe Gesamt & P&L
- Durchschnitts R-Multiple
- Gewinn-Rate bei Teilverkäufen

**Visualisierung**:
- R-Multiple Histogram
- Detaillierte Teilverkäufe-Tabelle

### **Tab 4: 📈 Performance**
**Zweck**: Trading-Performance analysieren

**Vergleichs-Analysen**:
- Trades mit vs. ohne Teilverkäufe
- R-Multiple Verteilungen
- Gewinn-Raten und Durchschnitte

**Charts**:
- Performance-Vergleich Balkendiagramm
- R-Multiple Histogramm

### **Tab 5: ⚙️ Settings**
**Zweck**: Daten-Management

**Export-Optionen**:
- CSV-Export (für Excel)
- JSON-Backup (komplette Wiederherstellung)

**Daten löschen**:
- Sicherheitsabfrage vor Löschung
- Portfolio-Reset

---

## 🎯 Beispiel-Workflow

### **Szenario: NVIDIA Trade mit Teilverkauf**

1. **Trade planen** (Tab 1)
   ```
   Symbol: NVIDIA
   Entry: €120.00
   Stop-Loss: €115.00
   
   → Berechnung: 100 Aktien bei €50k Depot
   → 1R Target: €125.00 (€500 Gewinn)
   ```

2. **Position eröffnen**
   - "Als offene Position markieren"
   - Cash reduziert sich um €12,000

3. **Kurs entwickelt sich positiv** (Tab 2)
   ```
   Aktueller Preis: €125.00 (1R erreicht!)
   
   → 50% Teilverkauf bei €125.00
   → 50 Aktien verkauft = €6,250 Erlös
   → Stop automatisch auf €120.00 (Break-even)
   → Verbleibende 50 Aktien laufen weiter
   ```

4. **Weitere Entwicklung**
   ```
   Aktueller Preis: €130.00 (2R erreicht!)
   
   → Weitere 25% (25 Aktien) verkaufen
   → Stop manuell auf €125.00 nachziehen
   → 25 Aktien als "Moonshot" laufen lassen
   ```

5. **Performance-Analyse** (Tab 4)
   ```
   Ergebnis: 2.5R Gesamt-Performance
   
   Teilverkauf 1: 50 Aktien @ €125 = 1.0R
   Teilverkauf 2: 25 Aktien @ €130 = 2.0R  
   Rest: 25 Aktien @ Ziel oder Stop
   ```

---

## 💾 Daten-Management

### **Automatische Speicherung**
- Alle Daten werden in der **Browser-Session** gespeichert
- Solange Browser-Tab geöffnet bleibt → Daten erhalten
- Bei Tab-Schließung → Daten verloren

### **Backup erstellen**
1. Tab 5 "Settings" öffnen
2. "Vollständiges Backup (JSON)" klicken
3. Datei automatisch heruntergeladen
4. Datei sicher speichern (z.B. OneDrive, Dropbox)

### **Backup wiederherstellen**
1. JSON-Backup-Datei hochladen
2. "Backup wiederherstellen" klicken
3. Alle Trades und Portfolio-Daten werden wiederhergestellt

### **CSV-Export für Analyse**
- **Trades-Export**: Für Excel-Pivot-Tabellen
- **Teilverkäufe-Export**: Für detaillierte R-Multiple Analysen

---

## 💡 Tipps & Tricks

### **🎯 Trading-Tipps**
1. **Immer 1% Risiko einhalten** - Tool berechnet automatisch
2. **Bei 1R erreicht**: 50% verkaufen + Stop auf Break-even
3. **Bei 2R erreicht**: Weitere 25% verkaufen + Stop nachziehen
4. **Rest laufen lassen**: Für größere Gewinne (5R+)

### **🔧 Tool-Tipps**
1. **Regelmäßige Backups**: Wöchentlich JSON-Backup erstellen
2. **Portfolio aktuell halten**: Depot-Wert bei Gewinnen/Verlusten anpassen
3. **Cash-Management**: Nach Trades Cash-Bestand überprüfen
4. **Performance-Review**: Monatlich Tab 4 für Analyse nutzen

### **📊 Analyse-Tipps**
1. **R-Multiple Verteilung**: Sollte überwiegend positiv sein
2. **Teilverkäufe vs. Komplettverkauf**: Vergleich der Performance
3. **Gewinn-Rate**: >50% bei guter Strategie
4. **Durchschnitts-R**: >1.0R für profitables Trading

---

## 🔧 Troubleshooting

### **Problem: App startet nicht**
**Lösung**:
```cmd
pip install --upgrade streamlit pandas plotly
streamlit run trading_app_advanced.py
```

### **Problem: Browser öffnet nicht automatisch**
**Lösung**:
- Manuell `http://localhost:8501` in Browser eingeben
- Oder anderen Port versuchen: `http://localhost:8502`

### **Problem: "Module not found" Fehler**
**Lösung**:
```cmd
pip install streamlit pandas plotly uuid datetime json
```

### **Problem: Daten verschwunden**
**Lösung**:
- JSON-Backup wiederherstellen (falls vorhanden)
- Oder: Trades manuell neu eingeben

### **Problem: App läuft langsam**
**Lösung**:
- Browser-Cache leeren (Ctrl + F5)
- App neu starten (Ctrl + C → neu starten)
- Nur einen Browser-Tab mit der App offen haben

### **Problem: Berechnungen falsch**
**Lösung**:
- Portfolio-Wert in Sidebar überprüfen
- Entry-Preis > Stop-Loss sicherstellen
- Bei Problemen: App neu starten

---

## 🚀 Erweiterte Nutzung

### **Für Power-User**
- **Mehrere Zeitrahmen**: Verschiedene Browser-Tabs für verschiedene Strategien
- **Backtest-Modus**: Historische Trades zur Performance-Analyse eingeben
- **Excel-Integration**: CSV-Exports für erweiterte Pivot-Analysen

### **Für Teams**
- **Backup-Sharing**: JSON-Backups im Team teilen
- **Screen-Sharing**: Live-Trading Sessions über Teams/Zoom
- **Performance-Vergleich**: Verschiedene Trader-Performances vergleichen

---

## 📞 Support & Weiterentwicklung

### **Bei Fragen oder Problemen**
- README.md durchlesen
- Troubleshooting-Sektion checken
- Code-Kommentare in `trading_app_advanced.py` studieren

### **Feature-Wünsche**
Das Tool ist modular aufgebaut und kann erweitert werden um:
- Live-Kurse API Integration
- Automatische Order-Placement
- Mobile App Version
- Crypto/Forex Support
- Machine Learning Features

---

**🎯 Viel Erfolg mit deinem professionellen Risk Management!**

*Entwickelt für disziplinierte Trader, die Kapitalerhalt über schnelle Gewinne stellen.*

---
