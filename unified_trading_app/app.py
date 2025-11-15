#!/usr/bin/env python3
"""
🎯 Unified Trading App
Komplette Trading Risk Management Lösung

Features:
- Alle Produkt-Typen (Spot, CFD, Knockout)
- Long/Short Support
- Trade-Management
- Portfolio-Tracking
- Performance-Analytics
"""

import streamlit as st
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core import UnifiedPositionCalculator, TradeManager
from utils.formatters import (
    format_currency, format_percentage, format_r_multiple,
    get_product_badge, get_product_label, get_status_badge,
    calculate_pnl, calculate_current_r_multiple
)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="🎯 Unified Trading App",
    page_icon="📈",
    layout="wide"
)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialisiere Session State"""
    if 'portfolio_value' not in st.session_state:
        st.session_state.portfolio_value = 50000.0
    if 'cash_available' not in st.session_state:
        st.session_state.cash_available = 10000.0
    if 'trade_manager' not in st.session_state:
        st.session_state.trade_manager = TradeManager()
    if 'risk_percentage' not in st.session_state:
        st.session_state.risk_percentage = 1.0


init_session_state()


# ============================================================================
# SIDEBAR - PORTFOLIO CONFIGURATION
# ============================================================================

st.sidebar.header("💰 Portfolio Konfiguration")

portfolio_value = st.sidebar.number_input(
    "Gesamtes Depot-Wert (€)",
    min_value=1000.0,
    value=st.session_state.portfolio_value,
    step=1000.0,
    format="%.2f"
)

cash_available = st.sidebar.number_input(
    "Verfügbares Cash (€)",
    min_value=0.0,
    value=st.session_state.cash_available,
    step=500.0,
    format="%.2f"
)

risk_percentage = st.sidebar.slider(
    "Risiko pro Trade (%)",
    min_value=0.5,
    max_value=5.0,
    value=st.session_state.risk_percentage,
    step=0.1
)

# Update Session State
st.session_state.portfolio_value = portfolio_value
st.session_state.cash_available = cash_available
st.session_state.risk_percentage = risk_percentage

# Portfolio Übersicht
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Portfolio Übersicht")

manager = st.session_state.trade_manager
metrics = manager.calculate_portfolio_metrics()

invested = portfolio_value - cash_available
invested_pct = (invested / portfolio_value) * 100
cash_pct = (cash_available / portfolio_value) * 100
max_risk = portfolio_value * (risk_percentage / 100)

st.sidebar.metric("Investiert", format_currency(invested), f"{invested_pct:.1f}%")
st.sidebar.metric("Cash", format_currency(cash_available), f"{cash_pct:.1f}%")
st.sidebar.metric(f"Max Risiko ({risk_percentage}%)", format_currency(max_risk))
st.sidebar.metric("Offene Positionen", metrics['open_trades'])

if metrics['total_exposure'] > 0:
    st.sidebar.metric("Total Exposure", format_currency(metrics['total_exposure']))


# ============================================================================
# HEADER
# ============================================================================

st.title("🎯 Unified Trading Risk Management")
st.markdown("**Alle Produkt-Typen • Trade-Management • Performance-Analytics**")


# ============================================================================
# TAB SYSTEM
# ============================================================================

tab1, tab2 = st.tabs([
    "🎯 Trade Calculator",
    "📊 Offene Positionen"
])


# ============================================================================
# TAB 1: TRADE CALCULATOR
# ============================================================================

with tab1:
    st.header("🎯 Trade Calculator")
    st.markdown("Berechne Positionsgröße für alle Produkt-Typen")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Trade Setup")

        # Symbol
        symbol = st.text_input("Symbol/Aktie", placeholder="z.B. NVIDIA, AAPL")

        # Produkt-Typ
        product_type = st.selectbox(
            "Produkt-Typ",
            options=["spot", "cfd_long", "cfd_short", "knockout_long", "knockout_short"],
            format_func=lambda x: f"{get_product_badge(x)} {get_product_label(x)}"
        )

        # Entry & Stop
        col_entry, col_stop = st.columns(2)

        with col_entry:
            entry_price = st.number_input(
                "Entry Preis (€)",
                min_value=0.01,
                value=120.0,
                step=0.01,
                format="%.2f"
            )

        with col_stop:
            # Default Stop basierend auf Produkt-Typ
            default_stop = 115.0 if product_type not in ["cfd_short", "knockout_short"] else 125.0
            stop_loss = st.number_input(
                "Stop-Loss (€)",
                min_value=0.01,
                value=default_stop,
                step=0.01,
                format="%.2f"
            )

        # Hebel-Einstellungen (nur für Hebelprodukte)
        if product_type != "spot":
            st.markdown("### 🔧 Hebel-Einstellungen")

            col_lev, col_days = st.columns(2)

            with col_lev:
                leverage_options = [1, 2, 3, 5, 10, 20, 30]
                default_leverage = 5 if product_type.startswith("cfd") else 10
                leverage = st.selectbox(
                    "Hebel",
                    options=leverage_options,
                    index=leverage_options.index(default_leverage),
                    format_func=lambda x: f"1:{x}"
                )

            with col_days:
                holding_days = st.number_input("Halte-Dauer (Tage)", min_value=1, max_value=365, value=10)

            col_spread, col_overnight = st.columns(2)

            with col_spread:
                default_spread = 0.2 if product_type.startswith("cfd") else 1.0
                spread_percent = st.number_input(
                    "Spread (%)",
                    min_value=0.0,
                    value=default_spread,
                    step=0.05,
                    format="%.2f"
                )

            with col_overnight:
                default_overnight = 0.01 if product_type.startswith("cfd") else 0.0
                overnight_percent = st.number_input(
                    "Overnight (%)",
                    min_value=0.0,
                    value=default_overnight,
                    step=0.001,
                    format="%.3f",
                    disabled=not product_type.startswith("cfd")
                )
        else:
            leverage = 1.0
            holding_days = 1
            spread_percent = 0.0
            overnight_percent = 0.0

        # Berechnen Button
        if st.button("📊 Position berechnen", type="primary", use_container_width=True):
            try:
                calc = UnifiedPositionCalculator(portfolio_value, risk_percentage)
                result = calc.calculate_position(
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    product_type=product_type,
                    leverage=leverage,
                    spread_percent=spread_percent,
                    overnight_percent=overnight_percent,
                    holding_days=holding_days
                )
                st.session_state.current_calculation = result
                st.session_state.current_symbol = symbol
                st.rerun()

            except ValueError as e:
                st.error(f"❌ Fehler: {e}")

    with col2:
        if 'current_calculation' in st.session_state:
            result = st.session_state.current_calculation
            calc_symbol = st.session_state.get('current_symbol', 'Asset')

            st.subheader(f"{get_product_badge(result.product_type)} {calc_symbol}")

            # Position Details
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Einheiten", f"{result.units:,}")
            col_b.metric("Investment", format_currency(result.actual_investment))
            col_c.metric("Depot %", format_percentage(result.portfolio_percentage))

            # Exposure (bei Hebel)
            if result.product_type != "spot":
                st.info(f"💼 **Exposure:** {format_currency(result.notional_value)} (Hebel {result.leverage}x)")

            # Kosten-Breakdown (bei Hebel)
            if result.product_type != "spot":
                st.markdown("### 💰 Kosten-Breakdown")
                cost_data = {
                    "Typ": ["Basis-Risiko", "Spread", "Overnight", "**Gesamt**"],
                    "Total": [
                        format_currency(result.basis_risk_total),
                        format_currency(result.spread_cost_total),
                        format_currency(result.overnight_cost_total),
                        f"**{format_currency(result.total_cost)}**"
                    ]
                }
                st.table(cost_data)

            # R-Multiple Targets
            st.markdown("### 🎯 Gewinnziele (R-Multiple)")
            targets_data = {
                "Target": ["1R", "2R", "5R"],
                "Preis": [
                    format_currency(result.target_1r),
                    format_currency(result.target_2r),
                    format_currency(result.target_5r)
                ],
                "Gewinn": [
                    format_currency(result.max_risk),
                    format_currency(result.max_risk * 2),
                    format_currency(result.max_risk * 5)
                ]
            }
            st.table(targets_data)

            # Aktionen
            st.markdown("### 💾 Trade speichern")
            col_s1, col_s2 = st.columns(2)

            with col_s1:
                if st.button("📋 Als geplant speichern", use_container_width=True):
                    trade_id = manager.create_trade(
                        symbol=calc_symbol,
                        product_type=result.product_type,
                        entry_price=result.entry_price,
                        stop_loss=result.stop_loss,
                        units=result.units,
                        investment=result.actual_investment,
                        exposure=result.notional_value,
                        risk_amount=result.max_risk,
                        target_1r=result.target_1r,
                        target_2r=result.target_2r,
                        target_5r=result.target_5r,
                        leverage=result.leverage,
                        spread_percent=spread_percent,
                        overnight_percent=overnight_percent,
                        holding_days=holding_days,
                        status="planned"
                    )
                    st.success(f"✅ Trade gespeichert (ID: {trade_id[:8]}...)")

            with col_s2:
                if st.button("🚀 Als offen markieren", use_container_width=True, type="primary"):
                    if cash_available >= result.actual_investment:
                        trade_id = manager.create_trade(
                            symbol=calc_symbol,
                            product_type=result.product_type,
                            entry_price=result.entry_price,
                            stop_loss=result.stop_loss,
                            units=result.units,
                            investment=result.actual_investment,
                            exposure=result.notional_value,
                            risk_amount=result.max_risk,
                            target_1r=result.target_1r,
                            target_2r=result.target_2r,
                            target_5r=result.target_5r,
                            leverage=result.leverage,
                            spread_percent=spread_percent,
                            overnight_percent=overnight_percent,
                            holding_days=holding_days,
                            status="open"
                        )
                        st.session_state.cash_available -= result.actual_investment
                        st.success(f"✅ Position eröffnet! (Cash: {format_currency(st.session_state.cash_available)})")
                        st.rerun()
                    else:
                        st.error(f"❌ Nicht genug Cash! (Benötigt: {format_currency(result.actual_investment)}, Verfügbar: {format_currency(cash_available)})")


# ============================================================================
# TAB 2: OFFENE POSITIONEN
# ============================================================================

with tab2:
    st.header("📊 Offene Positionen Management")

    open_trades = manager.get_open_trades()

    if not open_trades:
        st.info("📭 Keine offenen Positionen vorhanden")
    else:
        st.success(f"📍 {len(open_trades)} offene Position(en)")

        for trade in open_trades:
            with st.expander(f"{get_product_badge(trade.product_type)} {trade.symbol} - {format_currency(trade.entry_price)}", expanded=True):
                # Trade Info
                col_info1, col_info2, col_info3, col_info4 = st.columns(4)

                with col_info1:
                    st.markdown("**Produkt**")
                    st.write(f"{get_product_label(trade.product_type)}")
                    if trade.leverage > 1:
                        st.caption(f"Hebel: {trade.leverage}x")

                with col_info2:
                    st.markdown("**Einheiten**")
                    st.write(f"{trade.units:,}")
                    st.caption(f"Original: {trade.original_units:,}")

                with col_info3:
                    st.markdown("**Investment**")
                    st.write(format_currency(trade.investment))
                    if trade.exposure != trade.investment:
                        st.caption(f"Exposure: {format_currency(trade.exposure)}")

                with col_info4:
                    st.markdown("**Risiko**")
                    st.write(format_currency(trade.risk_amount))
                    st.caption(f"{risk_percentage}% Depot")

                # Preis-Info
                col_price1, col_price2, col_price3 = st.columns(3)

                with col_price1:
                    st.markdown("**Entry**")
                    st.write(format_currency(trade.entry_price))

                with col_price2:
                    st.markdown("**Current Stop**")
                    st.write(format_currency(trade.current_stop))

                with col_price3:
                    # Aktueller Preis Input
                    current_price = st.number_input(
                        "Aktueller Preis",
                        min_value=0.01,
                        value=trade.entry_price,
                        step=0.01,
                        format="%.2f",
                        key=f"current_price_{trade.id}"
                    )

                # P&L Berechnung
                is_short = trade.product_type in ["cfd_short", "knockout_short"]
                current_pnl = calculate_pnl(current_price, trade.entry_price, trade.units, is_short)
                current_r = calculate_current_r_multiple(current_price, trade.entry_price, trade.stop_loss, is_short)

                # Live Metriken
                col_met1, col_met2, col_met3 = st.columns(3)

                pnl_color = "normal"
                if current_pnl > 0:
                    pnl_color = "inverse"
                elif current_pnl < 0:
                    pnl_color = "off"

                with col_met1:
                    st.metric("Aktueller P&L", format_currency(current_pnl), delta=format_percentage((current_pnl/trade.investment)*100) if trade.investment > 0 else "0%")

                with col_met2:
                    st.metric("R-Multiple", format_r_multiple(current_r))

                with col_met3:
                    total_pnl = trade.total_realized_pnl + current_pnl
                    st.metric("Total P&L", format_currency(total_pnl))

                # R-Targets Fortschritt
                st.markdown("**🎯 Target Fortschritt**")
                progress_text = f"Entry: {format_currency(trade.entry_price)} → Aktuell: {format_currency(current_price)}"

                if not is_short:
                    if current_price >= trade.target_5r:
                        st.success(f"✅ 5R Target erreicht! {progress_text}")
                    elif current_price >= trade.target_2r:
                        st.success(f"✅ 2R Target erreicht! {progress_text}")
                    elif current_price >= trade.target_1r:
                        st.info(f"✅ 1R Target erreicht! {progress_text}")
                    else:
                        st.warning(f"⏳ Noch kein Target erreicht. {progress_text}")
                else:
                    if current_price <= trade.target_5r:
                        st.success(f"✅ 5R Target erreicht! {progress_text}")
                    elif current_price <= trade.target_2r:
                        st.success(f"✅ 2R Target erreicht! {progress_text}")
                    elif current_price <= trade.target_1r:
                        st.info(f"✅ 1R Target erreicht! {progress_text}")
                    else:
                        st.warning(f"⏳ Noch kein Target erreicht. {progress_text}")

                # Aktionen
                st.markdown("---")
                col_act1, col_act2, col_act3, col_act4 = st.columns(4)

                with col_act1:
                    if st.button("Stop zu Break-even", key=f"breakeven_{trade.id}", use_container_width=True):
                        manager.update_trade(trade.id, {'current_stop': trade.entry_price})
                        st.success("✅ Stop auf Break-even gesetzt!")
                        st.rerun()

                with col_act2:
                    new_stop = st.number_input("Neuer Stop", min_value=0.01, value=trade.current_stop, step=0.01, key=f"new_stop_{trade.id}")
                    if st.button("Stop updaten", key=f"update_stop_{trade.id}", use_container_width=True):
                        manager.update_trade(trade.id, {'current_stop': new_stop})
                        st.success(f"✅ Stop updated auf {format_currency(new_stop)}")
                        st.rerun()

                with col_act3:
                    if st.button("🔴 Position schließen", key=f"close_{trade.id}", use_container_width=True, type="primary"):
                        manager.close_trade(trade.id, close_price=current_price)
                        st.session_state.cash_available += trade.investment + current_pnl
                        st.success(f"✅ Position geschlossen! P&L: {format_currency(current_pnl)}")
                        st.rerun()

                with col_act4:
                    if st.button("🗑️ Löschen", key=f"delete_{trade.id}", use_container_width=True):
                        if st.button("⚠️ Wirklich löschen?", key=f"confirm_delete_{trade.id}"):
                            manager.delete_trade(trade.id)
                            st.session_state.cash_available += trade.investment  # Cash zurück
                            st.warning("⚠️ Trade gelöscht")
                            st.rerun()


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("*🎯 Unified Trading Risk Management v1.0 - Phase 2*")
