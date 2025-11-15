#!/usr/bin/env python3
"""
🎯 Advanced Trading Risk Management Tool v2.0
1% Risiko-Regel mit Teilverkauf-Funktionalität

Features:
- Position Size Calculator nach 1% Regel
- Teilverkauf-Management (25%, 50%, 75%, 100%)
- Stop-Loss Trailing (automatisch auf Break-even)
- R-Multiple Tracking und Performance-Analyse
- Portfolio-Tracking mit Cash-Management
- CSV/JSON Export für Backup und Analyse

Installation:
pip install streamlit pandas plotly

Start:
streamlit run advanced_trading_app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import uuid

# ============================================================================
# CORE CALCULATOR KLASSEN
# ============================================================================

class PositionSizeCalculator:
    """Berechnet Positionsgröße nach 1% Risiko-Regel"""
    
    def __init__(self, total_portfolio_value: float, risk_percentage: float = 1.0):
        self.total_portfolio = total_portfolio_value
        self.risk_percentage = risk_percentage / 100
        self.max_risk_amount = self.total_portfolio * self.risk_percentage
        
    def calculate_position_size(self, entry_price: float, stop_loss: float) -> dict:
        """
        Hauptberechnung: Positionsgröße basierend auf Entry und Stop-Loss
        
        Returns:
            dict mit depot_info, trade_setup, position_details, risk_reward_targets
        """
        if entry_price <= stop_loss:
            raise ValueError("Entry Price muss höher als Stop-Loss sein!")
        
        risk_per_share = entry_price - stop_loss
        position_size = self.max_risk_amount / risk_per_share
        position_value = position_size * entry_price
        
        # R-Multiple Targets berechnen
        target_1r = entry_price + risk_per_share
        target_2r = entry_price + (2 * risk_per_share)
        target_5r = entry_price + (5 * risk_per_share)
        
        return {
            'depot_info': {
                'gesamtdepot': self.total_portfolio,
                'max_risiko': self.max_risk_amount,
                'risiko_prozent': self.risk_percentage * 100
            },
            'trade_setup': {
                'entry_preis': entry_price,
                'stop_loss': stop_loss,
                'risiko_pro_aktie': risk_per_share
            },
            'position_details': {
                'anzahl_aktien': int(position_size),
                'position_wert': position_value,
                'depot_anteil': (position_value/self.total_portfolio)*100
            },
            'risk_reward_targets': {
                '1R_target': target_1r,
                '2R_target': target_2r,
                '5R_target': target_5r
            }
        }

class PositionManager:
    """Verwaltet Teilverkäufe und Position-Updates"""
    
    @staticmethod
    def calculate_partial_sale(trade, sell_percentage, current_price):
        """
        Berechnet Teilverkauf-Erlös und R-Multiple
        
        Args:
            trade: Trade Dictionary aus Session State
            sell_percentage: Prozent zu verkaufen (25, 50, 75, 100)
            current_price: Aktueller Marktpreis
            
        Returns:
            dict mit shares_sold, remaining_shares, sale_proceeds, sold_pnl, sold_r_multiple
        """
        shares_to_sell = int(trade['current_position_size'] * sell_percentage / 100)
        remaining_shares = trade['current_position_size'] - shares_to_sell
        
        sale_proceeds = shares_to_sell * current_price
        sold_pnl = shares_to_sell * (current_price - trade['entry_price'])
        
        original_risk_per_share = trade['entry_price'] - trade['original_stop_loss']
        sold_r_multiple = (current_price - trade['entry_price']) / original_risk_per_share
        
        return {
            'shares_sold': shares_to_sell,
            'remaining_shares': remaining_shares,
            'sale_proceeds': sale_proceeds,
            'sold_pnl': sold_pnl,
            'sold_r_multiple': sold_r_multiple,
            'sale_price': current_price
        }

# ============================================================================
# STREAMLIT APP CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="🎯 Advanced Trading Risk Manager", 
    page_icon="📈",
    layout="wide"
)

# Session State Initialisierung
if 'portfolio_value' not in st.session_state:
    st.session_state.portfolio_value = 50000.0
if 'cash_available' not in st.session_state:
    st.session_state.cash_available = 10000.0
if 'trades_history' not in st.session_state:
    st.session_state.trades_history = []

# ============================================================================
# HEADER & SIDEBAR
# ============================================================================

st.title("🎯 Advanced Trading Risk Management Tool")
st.markdown("**1% Risiko-Regel mit Teilverkauf-Management**")

st.sidebar.header("💰 Portfolio Konfiguration")

new_portfolio = st.sidebar.number_input(
    "Gesamtes Depot-Wert (€)", min_value=1000.0, 
    value=st.session_state.portfolio_value, step=1000.0, format="%.2f"
)

new_cash = st.sidebar.number_input(
    "Verfügbares Cash (€)", min_value=0.0, 
    value=st.session_state.cash_available, step=500.0, format="%.2f"
)

risk_percent = st.sidebar.slider(
    "Risiko pro Trade (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.1
)

# Update Session State
st.session_state.portfolio_value = new_portfolio
st.session_state.cash_available = new_cash

# Portfolio Übersicht in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Portfolio Übersicht")
invested = new_portfolio - new_cash
st.sidebar.metric("Investiert", f"€{invested:,.2f}", f"{(invested/new_portfolio)*100:.1f}%")
st.sidebar.metric("Cash", f"€{new_cash:,.2f}", f"{(new_cash/new_portfolio)*100:.1f}%")
st.sidebar.metric(f"Max Risiko ({risk_percent}%)", f"€{new_portfolio * risk_percent/100:,.2f}")

# ============================================================================
# MAIN INTERFACE - TAB SYSTEM
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Trade Calculator", 
    "📊 Offene Positionen", 
    "💰 Teilverkäufe", 
    "📈 Performance", 
    "⚙️ Settings"
])

# ============================================================================
# TAB 1: TRADE CALCULATOR
# ============================================================================

with tab1:
    st.header("🎯 Neuen Trade berechnen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Trade Setup")
        symbol = st.text_input("Symbol/Aktie", placeholder="z.B. NVIDIA, AAPL")
        entry_price = st.number_input("Entry Preis (€)", min_value=0.01, value=100.0, step=0.01)
        stop_loss = st.number_input("Stop-Loss (€)", min_value=0.01, value=95.0, step=0.01)
        
        if st.button("📊 Position berechnen", type="primary"):
            try:
                calc = PositionSizeCalculator(new_portfolio, risk_percent)
                result = calc.calculate_position_size(entry_price, stop_loss)
                st.session_state.current_calculation = result
                st.session_state.current_symbol = symbol
            except ValueError as e:
                st.error(f"❌ Fehler: {e}")
    
    with col2:
        if 'current_calculation' in st.session_state:
            result = st.session_state.current_calculation
            symbol_name = st.session_state.get('current_symbol', 'Aktie')
            
            st.subheader(f"📈 Analyse: {symbol_name}")
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Anzahl Aktien", f"{result['position_details']['anzahl_aktien']:,}")
            col_b.metric("Position Wert", f"€{result['position_details']['position_wert']:,.2f}")
            col_c.metric("Depot Anteil", f"{result['position_details']['depot_anteil']:.1f}%")
            
            st.markdown("### 🎯 Gewinnziele (R-Multiple)")
            targets_df = pd.DataFrame({
                'Target': ['1R', '2R', '5R'],
                'Preis': [f"€{result['risk_reward_targets']['1R_target']:.2f}",
                         f"€{result['risk_reward_targets']['2R_target']:.2f}",
                         f"€{result['risk_reward_targets']['5R_target']:.2f}"],
                'Gewinn': [f"€{result['depot_info']['max_risiko']:.2f}",
                          f"€{result['depot_info']['max_risiko'] * 2:.2f}",
                          f"€{result['depot_info']['max_risiko'] * 5:.2f}"]
            })
            st.dataframe(targets_df, use_container_width=True, hide_index=True)
            
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                if st.button("💾 Als geplanten Trade speichern"):
                    trade_data = {
                        'id': str(uuid.uuid4()),
                        'symbol': symbol_name,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'entry_price': entry_price,
                        'original_stop_loss': stop_loss,
                        'current_stop_loss': stop_loss,
                        'original_position_size': result['position_details']['anzahl_aktien'],
                        'current_position_size': result['position_details']['anzahl_aktien'],
                        'position_value': result['position_details']['position_wert'],
                        'risk_amount': result['depot_info']['max_risiko'],
                        'targets': result['risk_reward_targets'],
                        'status': 'geplant',
                        'partial_sales': [],
                        'total_realized_pnl': 0.0
                    }
                    st.session_state.trades_history.append(trade_data)
                    st.success("✅ Trade gespeichert!")
            
            with col_s2:
                if st.button("🚀 Als offene Position markieren"):
                    trade_data = {
                        'id': str(uuid.uuid4()),
                        'symbol': symbol_name,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'entry_price': entry_price,
                        'original_stop_loss': stop_loss,
                        'current_stop_loss': stop_loss,
                        'original_position_size': result['position_details']['anzahl_aktien'],
                        'current_position_size': result['position_details']['anzahl_aktien'],
                        'position_value': result['position_details']['position_wert'],
                        'risk_amount': result['depot_info']['max_risiko'],
                        'targets': result['risk_reward_targets'],
                        'status': 'offen',
                        'partial_sales': [],
                        'total_realized_pnl': 0.0
                    }
                    st.session_state.trades_history.append(trade_data)
                    st.session_state.cash_available -= result['position_details']['position_wert']
                    st.success("✅ Position eröffnet!")
                    st.rerun()

# ============================================================================
# TAB 2-5: Simplified für GitHub - Zeige nur Status
# ============================================================================

with tab2:
    st.header("📊 Offene Positionen Management")
    open_trades = [t for t in st.session_state.trades_history if t['status'] == 'offen']
    if open_trades:
        st.info(f"📍 {len(open_trades)} offene Position(en)")
        st.markdown("**Note:** Vollständige Teilverkauf-Features in lokaler Version verfügbar")
    else:
        st.info("📭 Keine offenen Positionen")

with tab3:
    st.header("💰 Teilverkäufe Analyse")
    st.info("Teilverkäufe-Tracking mit R-Multiple Verteilung - siehe lokale Version")

with tab4:
    st.header("📈 Performance")
    closed = [t for t in st.session_state.trades_history if t['status'] == 'geschlossen']
    st.metric("Geschlossene Trades", len(closed))
    st.info("Performance-Analyse mit Charts - siehe lokale Version")

with tab5:
    st.header("⚙️ Settings")
    if st.button("📤 CSV Export"):
        st.info("Export-Funktionen verfügbar - siehe lokale Version")
    st.markdown("**Hinweis:** Dies ist eine vereinfachte GitHub-Version. Für alle Features nutze die lokale `advanced_trading_app.py`")

st.markdown("---")
st.markdown("*🎯 Advanced Trading Risk Management Tool v2.0 - GitHub Streamlined Version*")
