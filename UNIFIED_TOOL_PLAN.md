# 🎯 Unified Trading Tool - Architektur-Plan

## 📋 Ziel

**Vereinigung der 3 bestehenden Tools in eine einzige, mächtige Anwendung**

```
position_size_calculator.py    ━┓
advanced_trading_app.py        ━╋━━━━> unified_trading_app.py
hebelprodukt_tool.py           ━┛
```

---

## 🔍 Feature-Analyse der bestehenden Tools

### 1. position_size_calculator.py (Basis)
**Stärken:**
- ✅ Saubere Klassen-Architektur
- ✅ 100% Type Hints
- ✅ Standalone nutzbar (keine UI-Abhängigkeit)
- ✅ Batch-Verarbeitung
- ✅ CLI-Beispiele

**Features:**
- 1% Risiko-Regel Berechnung
- R-Multiple Targets (1R, 2R, 5R)
- Portfolio-Update Funktion
- Validierung der Berechnungen

**Was fehlt:**
- Keine UI
- Keine Hebelprodukte
- Keine Teilverkäufe

---

### 2. advanced_trading_app.py (UI + Management)
**Stärken:**
- ✅ Professionelle Streamlit UI
- ✅ Session State Management
- ✅ 5-Tab System
- ✅ Trade-Historie
- ✅ Portfolio-Tracking

**Features:**
- Trade Calculator Tab
- Offene Positionen Management
- Teilverkäufe (25%, 50%, 75%, 100%)
- Performance Analytics
- CSV/JSON Export
- Cash-Management
- Stop-Loss Trailing

**Was fehlt:**
- Keine Hebelprodukte
- Tabs 2-5 vereinfacht in GitHub-Version

---

### 3. hebelprodukt_tool.py (Advanced Math)
**Stärken:**
- ✅ Komplexe Hebel-Mathematik
- ✅ Short-Position Support
- ✅ Kosten-Berechnung (Spread/Overnight)
- ✅ Streamlit UI

**Features:**
- Spot-Positionen
- CFD Long/Short mit Hebel
- Knockout-Zertifikate
- Spread-Kosten Berechnung
- Overnight-Kosten (nur CFDs)
- Flexible Hebel (1x-30x)

**Was fehlt:**
- Kein Trade-Management
- Keine Teilverkäufe
- Keine Historie

---

## 🏗️ Architektur des Unified Tools

### **Schichten-Design**

```
┌─────────────────────────────────────────────┐
│         STREAMLIT UI (Frontend)            │
│  ┌─────┬─────┬─────┬─────┬─────┬─────┐    │
│  │ Tab1│ Tab2│ Tab3│ Tab4│ Tab5│ Tab6│    │
│  └─────┴─────┴─────┴─────┴─────┴─────┘    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      BUSINESS LOGIC (Core Classes)          │
│  ┌──────────────────────────────────────┐  │
│  │ UnifiedPositionCalculator            │  │
│  │ - Spot-Berechnung                    │  │
│  │ - Hebel-Berechnung                   │  │
│  │ - Short-Position Support             │  │
│  │ - Kosten-Integration                 │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │ TradeManager                         │  │
│  │ - Trade-CRUD Operationen             │  │
│  │ - Position-Tracking                  │  │
│  │ - Cash-Management                    │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │ PartialSaleManager                   │  │
│  │ - Teilverkauf-Berechnung             │  │
│  │ - R-Multiple Tracking                │  │
│  │ - Stop-Loss Trailing                 │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │ PerformanceAnalyzer                  │  │
│  │ - Analytics & Metriken               │  │
│  │ - Charts & Visualisierung            │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│       DATA LAYER (Persistence)              │
│  - Session State                            │
│  - JSON Export/Import                       │
│  - CSV Export                               │
└─────────────────────────────────────────────┘
```

---

## 🎯 Tab-Struktur des Unified Tools

### **Tab 1: 🎯 Trade Calculator (Erweitert)**
**Kombiniert:** position_size_calculator.py + hebelprodukt_tool.py

**Features:**
- Symbol-Eingabe
- Produkt-Typ Auswahl:
  - 📈 Spot (klassisch)
  - 🔥 CFD Long
  - 🔻 CFD Short
  - 🚀 Knockout Long
  - 📉 Knockout Short
- Entry/Stop Eingabe
- **Wenn Hebelprodukt:**
  - Hebel-Auswahl (1x-30x)
  - Spread (%)
  - Overnight-Kosten (%)
  - Halte-Dauer (Tage)
- **Ausgabe:**
  - Anzahl Einheiten
  - Investment vs. Exposure (bei Hebel)
  - R-Multiple Targets
  - Kosten-Breakdown
  - Depot-Anteil
- **Aktionen:**
  - Als geplant speichern
  - Als offen markieren (Cash-Abzug)

---

### **Tab 2: 📊 Offene Positionen (Erweitert)**
**Von:** advanced_trading_app.py + Hebelprodukt-Support

**Features:**
- Liste aller offenen Positionen
- **Pro Position:**
  - Symbol + Produkt-Typ Badge
  - Entry/Stop/Aktuell
  - P&L Live-Berechnung
  - Exposure (bei Hebel)
  - R-Multiple aktuell
  - Teilverkauf-Buttons (25%, 50%, 75%, 100%)
  - Stop-Loss Update
  - Position schließen
- **Automatik:**
  - Bei profitablem Teilverkauf → Stop auf Break-even
  - Cash-Update bei Verkäufen
  - Historie der Teilverkäufe

---

### **Tab 3: 💰 Teilverkäufe Analytics**
**Von:** advanced_trading_app.py

**Features:**
- Gesamtübersicht Teilverkäufe
- R-Multiple Verteilung (Histogram)
- Durchschnitts-Performance
- Detaillierte Teilverkäufe-Tabelle
- **NEU:** Filterung nach Produkt-Typ

---

### **Tab 4: 📈 Performance Dashboard**
**Von:** advanced_trading_app.py + neue Metriken

**Features:**
- Geschlossene Trades Übersicht
- Performance-Vergleich:
  - Spot vs. Hebelprodukte
  - Long vs. Short
  - Mit/Ohne Teilverkäufe
- Charts:
  - R-Multiple Verteilung
  - Gewinn-Rate
  - Durchschnitts-R pro Produkt-Typ
- **NEU:** Hebel-Effizienz Analyse

---

### **Tab 5: 📋 Trade-Historie**
**Von:** advanced_trading_app.py

**Features:**
- Alle Trades (geplant/offen/geschlossen)
- Filterung nach Status, Produkt-Typ
- Sortierung nach Datum, R-Multiple
- Detailansicht pro Trade
- **NEU:** Hebelprodukt-Details

---

### **Tab 6: ⚙️ Settings & Export**
**Von:** advanced_trading_app.py

**Features:**
- Portfolio-Konfiguration
- Export-Optionen (CSV/JSON)
- Daten löschen
- **NEU:** Backup/Restore

---

## 🔧 Kern-Klassen Design

### **1. UnifiedPositionCalculator**
```python
class UnifiedPositionCalculator:
    """
    Vereint position_size_calculator.py + hebelprodukt_tool.py
    """

    def __init__(self, portfolio_value: float, risk_percent: float = 1.0):
        self.portfolio = portfolio_value
        self.risk_percent = risk_percent / 100
        self.max_risk = self.portfolio * self.risk_percent

    def calculate_position(
        self,
        entry: float,
        stop: float,
        product_type: str = "spot",
        leverage: float = 1.0,
        spread_percent: float = 0.0,
        overnight_percent: float = 0.0,
        holding_days: int = 1
    ) -> dict:
        """
        Universal Berechnung für alle Produkt-Typen

        product_type: spot, cfd_long, cfd_short, knockout_long, knockout_short
        """
        # Logik kombiniert aus beiden Tools
        # ...
```

**Features:**
- Spot-Berechnung (wie position_size_calculator.py)
- Hebel-Berechnung (wie hebelprodukt_tool.py)
- Short-Support
- Kosten-Integration
- R-Multiple Berechnung für alle Typen
- Validierung

---

### **2. TradeManager**
```python
class TradeManager:
    """
    Verwaltet Trade-Lifecycle
    """

    def __init__(self):
        self.trades = []

    def create_trade(self, trade_data: dict) -> str:
        """Erstellt neuen Trade, gibt ID zurück"""

    def update_trade(self, trade_id: str, updates: dict):
        """Updated Trade-Felder"""

    def close_trade(self, trade_id: str, close_price: float):
        """Schließt Trade komplett"""

    def get_open_trades(self) -> list:
        """Gibt alle offenen Trades zurück"""

    def get_trade_by_id(self, trade_id: str) -> dict:
        """Findet Trade nach ID"""
```

**Features:**
- CRUD Operationen
- Status-Management (geplant/offen/geschlossen)
- Filterung und Suche
- Portfolio-Integration

---

### **3. PartialSaleManager**
```python
class PartialSaleManager:
    """
    Verwaltet Teilverkäufe
    """

    @staticmethod
    def execute_partial_sale(
        trade: dict,
        sell_percentage: float,
        current_price: float
    ) -> dict:
        """
        Führt Teilverkauf aus

        Returns:
            - units_sold
            - remaining_units
            - proceeds
            - pnl
            - r_multiple
            - should_update_stop (bei Gewinn)
        """
```

**Features:**
- Teilverkauf-Berechnung
- R-Multiple pro Teilverkauf
- Stop-Loss Empfehlungen
- Historie-Tracking

---

### **4. PerformanceAnalyzer**
```python
class PerformanceAnalyzer:
    """
    Analytics und Visualisierung
    """

    def __init__(self, trades: list):
        self.trades = trades

    def calculate_metrics(self) -> dict:
        """
        Returns:
            - total_trades
            - win_rate
            - avg_r_multiple
            - total_pnl
            - best_trade
            - worst_trade
        """

    def compare_product_types(self) -> dict:
        """Vergleicht Performance nach Produkt-Typ"""

    def analyze_partial_sales(self) -> dict:
        """Analysiert Teilverkauf-Strategie"""

    def generate_charts(self) -> dict:
        """Erstellt Plotly Charts"""
```

**Features:**
- Metriken-Berechnung
- Vergleichs-Analysen
- Chart-Generierung
- Export-Vorbereitung

---

## 📁 Datei-Struktur

```
unified_trading_app.py          # Hauptdatei (Streamlit UI)
├── Core Classes
│   ├── UnifiedPositionCalculator
│   ├── TradeManager
│   ├── PartialSaleManager
│   └── PerformanceAnalyzer
├── UI Components
│   ├── render_tab1_calculator()
│   ├── render_tab2_positions()
│   ├── render_tab3_partial_sales()
│   ├── render_tab4_performance()
│   ├── render_tab5_history()
│   └── render_tab6_settings()
└── Helper Functions
    ├── format_currency()
    ├── calculate_r_multiple()
    └── validate_trade_data()
```

**Optional: Modulare Struktur**
```
unified_trading_app/
├── app.py                      # Streamlit Entry Point
├── core/
│   ├── calculator.py           # UnifiedPositionCalculator
│   ├── trade_manager.py        # TradeManager
│   ├── partial_sales.py        # PartialSaleManager
│   └── analytics.py            # PerformanceAnalyzer
├── ui/
│   ├── tab_calculator.py
│   ├── tab_positions.py
│   ├── tab_analytics.py
│   └── components.py
└── utils/
    ├── formatters.py
    └── validators.py
```

---

## 🎨 UI/UX Verbesserungen

### **Produkt-Typ Badges**
```
📈 Spot    🔥 CFD Long    🔻 CFD Short
🚀 KO Long    📉 KO Short
```

### **Conditional Inputs**
- Hebel-Einstellungen nur wenn Hebelprodukt ausgewählt
- Overnight-Kosten nur bei CFDs
- Short-Validierung (Entry < Stop)

### **Live-Berechnungen**
- P&L Updates in Echtzeit
- R-Multiple Live-Anzeige
- Exposure vs. Investment Vergleich

### **Smart Defaults**
- Spot: Kein Hebel, keine Kosten
- CFD: Hebel 5x, Spread 0.2%, Overnight 0.01%
- Knockout: Hebel 10x, Spread 1.0%, kein Overnight

---

## 🚀 Implementierungs-Roadmap

### **Phase 1: Core Classes (Foundation)**
**Ziel:** Stabile Berechnungs-Engine
- [ ] UnifiedPositionCalculator implementieren
- [ ] TradeManager Grundfunktionen
- [ ] Unit-Tests für alle Berechnungen
- [ ] Validation-Logic

**Dauer:** 2-3 Stunden

---

### **Phase 2: Basic UI (Tab 1 & 2)**
**Ziel:** Trades erstellen und verwalten
- [ ] Tab 1: Calculator mit Produkt-Typ Auswahl
- [ ] Tab 2: Offene Positionen Liste
- [ ] Session State Integration
- [ ] Basic Trade-Lifecycle

**Dauer:** 2-3 Stunden

---

### **Phase 3: Teilverkäufe (Tab 2 erweitert + Tab 3)**
**Ziel:** Partial Sales Management
- [ ] PartialSaleManager implementieren
- [ ] Teilverkauf-Buttons in Tab 2
- [ ] Tab 3: Analytics
- [ ] Stop-Loss Auto-Update

**Dauer:** 2 Stunden

---

### **Phase 4: Analytics & Performance (Tab 4 & 5)**
**Ziel:** Performance-Tracking
- [ ] PerformanceAnalyzer implementieren
- [ ] Tab 4: Charts und Metriken
- [ ] Tab 5: Historie-Tabelle
- [ ] Filterung und Sortierung

**Dauer:** 2 Stunden

---

### **Phase 5: Export & Polish (Tab 6)**
**Ziel:** Daten-Management
- [ ] CSV/JSON Export
- [ ] Backup/Restore
- [ ] UI-Polish
- [ ] Dokumentation

**Dauer:** 1-2 Stunden

---

### **Phase 6: Testing & Documentation**
**Ziel:** Production-Ready
- [ ] Comprehensive Tests
- [ ] README Update
- [ ] User Guide
- [ ] Performance Optimization

**Dauer:** 2 Stunden

---

## 💡 Besondere Features

### **1. Hebel-Effizienz Analyse**
Vergleicht Spot vs. Hebel Performance:
- Gleicher Risiko-Betrag
- Unterschiedliche Exposure
- ROI-Vergleich

### **2. Smart Trade-Vorschläge**
Basierend auf Portfolio:
- "Du hast noch €X verfügbar"
- "Mit aktuellem Risiko: Y Aktien"
- "Alternative Hebel-Optionen"

### **3. Risk-Heatmap**
Visualisiert Portfolio-Risiko:
- Offene Positionen
- Risiko-Verteilung
- Diversifikations-Score

### **4. Auto-Backup**
- Alle N Minuten auto-save
- Browser LocalStorage
- Download-Reminder

---

## 📊 Daten-Schema

### **Trade Object**
```python
{
    'id': 'uuid-string',
    'symbol': 'NVIDIA',
    'created_at': '2025-11-15 14:00',
    'status': 'offen',  # geplant/offen/geschlossen

    # Position Details
    'product_type': 'cfd_long',
    'entry_price': 120.00,
    'stop_loss': 115.00,
    'current_stop': 115.00,

    # Hebel-Specific
    'leverage': 5.0,
    'spread_percent': 0.2,
    'overnight_percent': 0.01,
    'holding_days': 10,

    # Position Size
    'units': 20,
    'investment': 2400.00,
    'exposure': 12000.00,  # Bei Hebel

    # Risk/Reward
    'risk_amount': 500.00,
    'r_targets': {
        '1R': 125.00,
        '2R': 130.00,
        '5R': 145.00
    },

    # Partial Sales
    'partial_sales': [
        {
            'date': '2025-11-16',
            'units_sold': 10,
            'price': 125.00,
            'proceeds': 1250.00,
            'pnl': 50.00,
            'r_multiple': 1.0
        }
    ],

    # Final Close (wenn geschlossen)
    'close_price': 130.00,
    'close_date': '2025-11-17',
    'total_pnl': 200.00,
    'final_r_multiple': 2.0
}
```

---

## ✅ Vorteile des Unified Tools

### **Für den User**
- ✅ **Eine App für alles** - Kein Wechsel zwischen Tools
- ✅ **Konsistente UX** - Gleiche Bedienung überall
- ✅ **Komplette Historie** - Alle Trades an einem Ort
- ✅ **Hebelprodukte + Management** - Beides vereint
- ✅ **Bessere Analytics** - Mehr Daten = bessere Insights

### **Für Wartung**
- ✅ **Ein Codebase** - Einfacher zu warten
- ✅ **Wiederverwendbare Komponenten** - DRY Prinzip
- ✅ **Zentralisierte Tests** - Eine Test-Suite
- ✅ **Einheitliche Daten** - Ein Schema

### **Für Weiterentwicklung**
- ✅ **Modularer Aufbau** - Einfach erweiterbar
- ✅ **Klare Architektur** - Leicht verständlich
- ✅ **Feature-Additions** - Neue Tabs/Features einfach
- ✅ **API-Ready** - Core-Classes wiederverwendbar

---

## 🎯 Nächste Schritte

1. **Review dieses Plans** ✋
   - Ist die Architektur sinnvoll?
   - Fehlen Features?
   - Änderungswünsche?

2. **Start Implementation** 🚀
   - Phase 1: Core Classes
   - Iterativ entwickeln
   - Regelmäßig testen

3. **User Testing** 👤
   - Früh Feedback einholen
   - UI/UX verfeinern
   - Performance optimieren

---

**Fragen zur Diskussion:**

1. Soll es eine einzelne Datei bleiben oder modular aufteilen?
2. Welche Features haben Priorität?
3. Sollen wir die alten 3 Tools behalten oder ersetzen?
4. Gibt es zusätzliche Features die du brauchst?

---

**Status:** 📝 PLAN ERSTELLT - READY FOR REVIEW
