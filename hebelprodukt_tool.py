#!/usr/bin/env python3
"""
🎯 Advanced Trading Risk Management Tool v3.0
1% Risiko-Regel + Hebelprodukte Support

Unterstützt:
- Spot Aktien (normale 1% Regel)
- CFD Long/Short (mit Hebel, Spread, Overnight-Kosten)
- Knock-Out Zertifikate (mit Hebel, Spread, keine Overnight)

Installation:
pip install streamlit pandas plotly

Start:
streamlit run hebelprodukt_tool.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime

class AdvancedPositionSizeCalculator:
    """Calculator mit Hebelprodukt-Support: CFDs und Knock-Outs"""
    
    def __init__(self, total_portfolio_value: float, risk_percentage: float = 1.0):
        self.total_portfolio = total_portfolio_value
        self.risk_percentage = risk_percentage / 100
        self.max_risk_amount = self.total_portfolio * self.risk_percentage
        
    def calculate_position_size(self, entry_price: float, stop_loss: float, 
                              product_type: str = "spot", leverage: float = 1.0,
                              spread_percent: float = 0.0, overnight_percent: float = 0.0,
                              holding_days: int = 10) -> dict:
        """
        Berechnung mit Hebelprodukt-Support
        product_type: spot, cfd_long, cfd_short, knockout_long, knockout_short
        """
        is_short = product_type in ["cfd_short", "knockout_short"]
        
        if is_short:
            if entry_price >= stop_loss:
                raise ValueError("Bei Short: Entry < Stop-Loss!")
            basis_risiko = stop_loss - entry_price
        else:
            if entry_price <= stop_loss:
                raise ValueError("Bei Long: Entry > Stop-Loss!")
            basis_risiko = entry_price - stop_loss
        
        if product_type == "spot":
            effektiv_risiko = basis_risiko
            spread_kosten = overnight_kosten = 0
            leverage_used = 1.0
        else:
            leverage_used = leverage
            effektiv_risiko = basis_risiko * leverage
            spread_kosten = entry_price * (spread_percent / 100)
            overnight_kosten = entry_price * (overnight_percent / 100) * holding_days
        
        gesamt_risiko_per_unit = effektiv_risiko + spread_kosten + overnight_kosten
        position_size = self.max_risk_amount / gesamt_risiko_per_unit
        
        if product_type == "spot":
            notional_value = actual_investment = position_size * entry_price
        else:
            notional_value = position_size * entry_price * leverage_used
            actual_investment = position_size * entry_price
        
        target_1r = entry_price + (basis_risiko if not is_short else -basis_risiko)
        target_2r = entry_price + ((2 * basis_risiko) if not is_short else -(2 * basis_risiko))
        target_5r = entry_price + ((5 * basis_risiko) if not is_short else -(5 * basis_risiko))
        
        return {
            'depot_info': {'gesamtdepot': self.total_portfolio, 'max_risiko': self.max_risk_amount},
            'product_info': {'product_type': product_type, 'leverage': leverage_used, 'is_short': is_short},
            'trade_setup': {'entry_preis': entry_price, 'stop_loss': stop_loss, 
                           'basis_risiko_per_unit': basis_risiko, 'gesamt_risiko_per_unit': gesamt_risiko_per_unit},
            'position_details': {'anzahl_einheiten': int(position_size), 
                               'actual_investment': actual_investment, 'notional_value': notional_value,
                               'depot_anteil': (actual_investment/self.total_portfolio)*100},
            'risk_reward_targets': {'1R_target': target_1r, '2R_target': target_2r, '5R_target': target_5r},
            'cost_breakdown': {'basis_risiko_total': position_size * basis_risiko,
                              'spread_kosten_total': position_size * spread_kosten,
                              'overnight_kosten_total': position_size * overnight_kosten}
        }

st.set_page_config(page_title="🎯 Trading Risk Manager v3.0", page_icon="📈", layout="wide")
st.title("🎯 Trading Risk Management Tool v3.0")
st.markdown("**1% Risiko-Regel + Hebelprodukte Support**")
st.success("🚀 NEU: CFDs, Knock-Outs, Short-Positionen")

st.sidebar.header("💰 Portfolio")
portfolio = st.sidebar.number_input("Depot (€)", min_value=1000.0, value=50000.0, step=1000.0)
cash = st.sidebar.number_input("Cash (€)", min_value=0.0, value=10000.0, step=500.0)
risk_pct = st.sidebar.slider("Risiko (%)", 0.5, 5.0, 1.0, 0.1)

st.header("🎯 Calculator")
col1, col2 = st.columns(2)

with col1:
    symbol = st.text_input("Symbol", placeholder="z.B. NVIDIA")
    product = st.selectbox("Produkt", ["spot", "cfd_long", "cfd_short", "knockout_long", "knockout_short"],
                          format_func=lambda x: {"spot":"📈 Spot", "cfd_long":"🔥 CFD Long", 
                                                "cfd_short":"🔻 CFD Short", "knockout_long":"🚀 KO Long",
                                                "knockout_short":"📉 KO Short"}[x])
    
    c1, c2 = st.columns(2)
    entry = c1.number_input("Entry (€)", 0.01, value=100.0, step=0.01)
    stop = c2.number_input("Stop (€)", 0.01, value=95.0 if product not in ["cfd_short","knockout_short"] else 105.0, step=0.01)
    
    if product != "spot":
        st.markdown("### 🔧 Hebel-Einstellungen")
        c3, c4 = st.columns(2)
        leverage = c3.selectbox("Hebel", [1,2,3,5,10,20,30], index=3, format_func=lambda x: f"1:{x}")
        days = c4.number_input("Tage", 1, 365, 10)
        c5, c6 = st.columns(2)
        spread = c5.number_input("Spread (%)", 0.0, value=0.2 if product.startswith("cfd") else 1.0, step=0.05)
        overnight = c6.number_input("Overnight (%)", 0.0, value=0.01 if product.startswith("cfd") else 0.0, step=0.001, format="%.3f")
    else:
        leverage, days, spread, overnight = 1.0, 1, 0.0, 0.0
    
    if st.button("📊 Berechnen", type="primary"):
        try:
            calc = AdvancedPositionSizeCalculator(portfolio, risk_pct)
            result = calc.calculate_position_size(entry, stop, product, leverage, spread, overnight, days)
            st.session_state.result = result
            st.session_state.symbol = symbol
        except ValueError as e:
            st.error(f"❌ {e}")

with col2:
    if 'result' in st.session_state:
        r = st.session_state.result
        sym = st.session_state.get('symbol', 'Asset')
        
        pi = r['product_info']
        st.subheader(f"{'📈' if pi['product_type']=='spot' else '🔥'} {sym}")
        
        pd_det = r['position_details']
        c1, c2, c3 = st.columns(3)
        c1.metric("Einheiten", f"{pd_det['anzahl_einheiten']:,}")
        c2.metric("Investment", f"€{pd_det['actual_investment']:,.0f}")
        c3.metric("Depot %", f"{pd_det['depot_anteil']:.1f}%")
        
        if pi['product_type'] != 'spot':
            st.caption(f"Exposure: €{pd_det['notional_value']:,.0f}")
            
            st.markdown("### 💰 Kosten")
            cb = r['cost_breakdown']
            df = pd.DataFrame({
                'Art': ['Basis', 'Spread', 'Overnight', 'Gesamt'],
                'Total': [f"€{cb['basis_risiko_total']:.2f}", f"€{cb['spread_kosten_total']:.2f}",
                         f"€{cb['overnight_kosten_total']:.2f}", 
                         f"€{sum(cb.values()):.2f}"]
            })
            st.dataframe(df, hide_index=True)
        
        st.markdown("### 🎯 Targets")
        tgt = r['risk_reward_targets']
        tdf = pd.DataFrame({
            'Target': ['1R', '2R', '5R'],
            'Preis': [f"€{tgt['1R_target']:.2f}", f"€{tgt['2R_target']:.2f}", f"€{tgt['5R_target']:.2f}"]
        })
        st.dataframe(tdf, hide_index=True)

st.markdown("---")
st.markdown("*🎯 v3.0 - Hebelprodukte Edition*")
