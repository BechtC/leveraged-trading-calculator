#!/usr/bin/env python3
"""
🎯 Unified Trading App - Complete (Phase 1-6)
Komplette Trading Risk Management Lösung

Features:
- Alle Produkt-Typen (Spot, CFD, Knockout)
- Long/Short Support
- Trade-Management mit Teilverkäufen
- Portfolio-Tracking
- Performance-Analytics
- Export & Backup
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core import UnifiedPositionCalculator, TradeManager, PartialSaleManager
from utils.formatters import (
    format_currency, format_percentage, format_r_multiple,
    get_product_badge, get_product_label, get_status_badge,
    calculate_pnl, calculate_current_r_multiple
)
from utils.export import DataExporter


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
st.markdown("**Alle Produkt-Typen • Teilverkäufe • Performance-Analytics**")


# ============================================================================
# TAB SYSTEM
# ============================================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Trade Calculator",
    "📊 Offene Positionen",
    "💰 Teilverkäufe",
    "📈 Performance",
    "📋 Historie",
    "⚙️ Settings"
])


# ============================================================================
# TAB 1: TRADE CALCULATOR (unchanged from Phase 2)
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
            default_stop = 115.0 if product_type not in ["cfd_short", "knockout_short"] else 125.0
            stop_loss = st.number_input(
                "Stop-Loss (€)",
                min_value=0.01,
                value=default_stop,
                step=0.01,
                format="%.2f"
            )

        # Hebel-Einstellungen
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

            # Exposure
            if result.product_type != "spot":
                st.info(f"💼 **Exposure:** {format_currency(result.notional_value)} (Hebel {result.leverage}x)")

            # Kosten-Breakdown
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
                    st.success(f"✅ Trade gespeichert!")
                    st.rerun()

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
                        st.success(f"✅ Position eröffnet!")
                        st.rerun()
                    else:
                        st.error(f"❌ Nicht genug Cash!")


# ============================================================================
# TAB 2: OFFENE POSITIONEN (mit Teilverkäufen)
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
                    if trade.units != trade.original_units:
                        st.caption(f"Original: {trade.original_units:,}")

                with col_info3:
                    st.markdown("**Investment**")
                    st.write(format_currency(trade.investment))
                    if trade.exposure != trade.investment:
                        st.caption(f"Exposure: {format_currency(trade.exposure)}")

                with col_info4:
                    st.markdown("**Risiko**")
                    st.write(format_currency(trade.risk_amount))
                    if trade.total_realized_pnl != 0:
                        st.caption(f"Realized: {format_currency(trade.total_realized_pnl)}")

                # Preis-Info
                col_price1, col_price2, col_price3 = st.columns(3)

                with col_price1:
                    st.markdown("**Entry**")
                    st.write(format_currency(trade.entry_price))

                with col_price2:
                    st.markdown("**Current Stop**")
                    st.write(format_currency(trade.current_stop))

                with col_price3:
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

                with col_met1:
                    st.metric("Unrealized P&L", format_currency(current_pnl))

                with col_met2:
                    st.metric("R-Multiple", format_r_multiple(current_r))

                with col_met3:
                    total_pnl = trade.total_realized_pnl + current_pnl
                    st.metric("Total P&L", format_currency(total_pnl))

                # Teilverkauf-Buttons
                st.markdown("### 💰 Teilverkäufe")
                col_ps1, col_ps2, col_ps3, col_ps4 = st.columns(4)

                with col_ps1:
                    if st.button("25% verkaufen", key=f"sell25_{trade.id}", use_container_width=True):
                        sale_details = PartialSaleManager.execute_partial_sale(
                            manager, trade.id, 25.0, current_price, auto_update_stop=True
                        )
                        st.session_state.cash_available += sale_details['sale_proceeds']
                        st.success(f"✅ 25% verkauft! P&L: {format_currency(sale_details['pnl'])}")
                        st.rerun()

                with col_ps2:
                    if st.button("50% verkaufen", key=f"sell50_{trade.id}", use_container_width=True):
                        sale_details = PartialSaleManager.execute_partial_sale(
                            manager, trade.id, 50.0, current_price, auto_update_stop=True
                        )
                        st.session_state.cash_available += sale_details['sale_proceeds']
                        st.success(f"✅ 50% verkauft!")
                        st.rerun()

                with col_ps3:
                    if st.button("75% verkaufen", key=f"sell75_{trade.id}", use_container_width=True):
                        sale_details = PartialSaleManager.execute_partial_sale(
                            manager, trade.id, 75.0, current_price, auto_update_stop=True
                        )
                        st.session_state.cash_available += sale_details['sale_proceeds']
                        st.success(f"✅ 75% verkauft!")
                        st.rerun()

                with col_ps4:
                    if st.button("🔴 100% schließen", key=f"sell100_{trade.id}", use_container_width=True, type="primary"):
                        sale_details = PartialSaleManager.execute_partial_sale(
                            manager, trade.id, 100.0, current_price, auto_update_stop=False
                        )
                        st.session_state.cash_available += sale_details['sale_proceeds']
                        st.success(f"✅ Position geschlossen! Total P&L: {format_currency(trade.total_realized_pnl)}")
                        st.rerun()

                # Teilverkauf-Historie
                if trade.partial_sales:
                    st.markdown("**Teilverkauf-Historie:**")
                    sales_df = pd.DataFrame(trade.partial_sales)
                    sales_df['pnl'] = sales_df['pnl'].apply(lambda x: format_currency(x))
                    sales_df['price'] = sales_df['price'].apply(lambda x: format_currency(x))
                    sales_df['r_multiple'] = sales_df['r_multiple'].apply(lambda x: format_r_multiple(x))
                    st.dataframe(sales_df, use_container_width=True, hide_index=True)

                # Weitere Aktionen
                st.markdown("---")
                col_act1, col_act2 = st.columns(2)

                with col_act1:
                    if st.button("Stop zu Break-even", key=f"breakeven_{trade.id}", use_container_width=True):
                        manager.update_trade(trade.id, {'current_stop': trade.entry_price})
                        st.success("✅ Stop auf Break-even!")
                        st.rerun()

                with col_act2:
                    new_stop = st.number_input("Neuer Stop", min_value=0.01, value=trade.current_stop, step=0.01, key=f"new_stop_{trade.id}")
                    if st.button("Stop updaten", key=f"update_stop_{trade.id}", use_container_width=True):
                        manager.update_trade(trade.id, {'current_stop': new_stop})
                        st.success(f"✅ Stop updated!")
                        st.rerun()


# ============================================================================
# TAB 3: TEILVERKÄUFE ANALYTICS
# ============================================================================

with tab3:
    st.header("💰 Teilverkäufe Analytics")

    all_trades = manager.get_all_trades()
    analytics = PartialSaleManager.analyze_partial_sales(all_trades)

    if analytics['total_partial_sales'] == 0:
        st.info("📭 Noch keine Teilverkäufe durchgeführt")
    else:
        # Overview Metriken
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        col_m1.metric("Total Teilverkäufe", analytics['total_partial_sales'])
        col_m2.metric("Total Erlös", format_currency(analytics['total_proceeds']))
        col_m3.metric("Total P&L", format_currency(analytics['total_pnl']))
        col_m4.metric("Avg R-Multiple", format_r_multiple(analytics['avg_r_multiple']))

        # R-Distribution mit Plotly
        st.markdown("### 📊 R-Multiple Verteilung")
        r_dist_df = pd.DataFrame([
            {"Range": k, "Anzahl": v}
            for k, v in analytics['r_distribution'].items()
        ])

        fig_r_dist = px.bar(
            r_dist_df,
            x="Range",
            y="Anzahl",
            title="R-Multiple Verteilung der Teilverkäufe",
            color="Anzahl",
            color_continuous_scale="Blues"
        )
        fig_r_dist.update_layout(height=400)
        st.plotly_chart(fig_r_dist, use_container_width=True)

        # By Percentage
        st.markdown("### 📈 Performance nach Verkaufs-Prozent")
        if analytics['by_percentage']:
            pct_data = []
            for pct, data in analytics['by_percentage'].items():
                pct_data.append({
                    "Prozent": f"{pct}%",
                    "Anzahl": data['count'],
                    "Total P&L": format_currency(data['total_pnl']),
                    "Avg R": format_r_multiple(data['avg_r'])
                })
            pct_df = pd.DataFrame(pct_data)
            st.dataframe(pct_df, use_container_width=True, hide_index=True)

        # Detail-Tabelle
        st.markdown("### 📋 Alle Teilverkäufe")
        if analytics['all_sales']:
            sales_detail_df = pd.DataFrame(analytics['all_sales'])
            sales_detail_df = sales_detail_df[['date', 'symbol', 'product_type', 'percentage', 'units_sold', 'price', 'pnl', 'r_multiple']]
            sales_detail_df['pnl'] = sales_detail_df['pnl'].apply(lambda x: format_currency(x))
            sales_detail_df['price'] = sales_detail_df['price'].apply(lambda x: format_currency(x))
            sales_detail_df['r_multiple'] = sales_detail_df['r_multiple'].apply(lambda x: format_r_multiple(x))
            sales_detail_df['percentage'] = sales_detail_df['percentage'].apply(lambda x: f"{x}%")
            st.dataframe(sales_detail_df, use_container_width=True, hide_index=True)


# ============================================================================
# TAB 4: PERFORMANCE DASHBOARD
# ============================================================================

with tab4:
    st.header("📈 Performance Dashboard")

    closed_trades = manager.get_closed_trades()
    open_trades = manager.get_open_trades()

    if not closed_trades:
        st.info("📭 Noch keine geschlossenen Trades")
    else:
        # Overview Metriken
        total_pnl = sum(t.final_pnl or 0 for t in closed_trades)
        winning_trades = [t for t in closed_trades if (t.final_pnl or 0) > 0]
        win_rate = (len(winning_trades) / len(closed_trades)) * 100 if closed_trades else 0
        avg_r = sum(t.final_r_multiple or 0 for t in closed_trades) / len(closed_trades) if closed_trades else 0

        col_p1, col_p2, col_p3, col_p4 = st.columns(4)

        col_p1.metric("Geschlossene Trades", len(closed_trades))
        col_p2.metric("Total P&L", format_currency(total_pnl))
        col_p3.metric("Win Rate", format_percentage(win_rate))
        col_p4.metric("Avg R-Multiple", format_r_multiple(avg_r))

        # Performance nach Produkt-Typ
        st.markdown("### 📊 Performance nach Produkt-Typ")

        product_performance = {}
        for trade in closed_trades:
            ptype = trade.product_type
            if ptype not in product_performance:
                product_performance[ptype] = {
                    'count': 0,
                    'total_pnl': 0,
                    'wins': 0,
                    'avg_r': []
                }

            product_performance[ptype]['count'] += 1
            product_performance[ptype]['total_pnl'] += (trade.final_pnl or 0)
            if (trade.final_pnl or 0) > 0:
                product_performance[ptype]['wins'] += 1
            if trade.final_r_multiple is not None:
                product_performance[ptype]['avg_r'].append(trade.final_r_multiple)

        if product_performance:
            perf_data = []
            for ptype, data in product_performance.items():
                win_rate_ptype = (data['wins'] / data['count']) * 100 if data['count'] > 0 else 0
                avg_r_ptype = sum(data['avg_r']) / len(data['avg_r']) if data['avg_r'] else 0

                perf_data.append({
                    "Produkt": f"{get_product_badge(ptype)} {get_product_label(ptype)}",
                    "Trades": data['count'],
                    "Win Rate": format_percentage(win_rate_ptype),
                    "Total P&L": format_currency(data['total_pnl']),
                    "Avg R": format_r_multiple(avg_r_ptype)
                })

            perf_df = pd.DataFrame(perf_data)
            st.dataframe(perf_df, use_container_width=True, hide_index=True)

        # R-Multiple Distribution mit Plotly
        st.markdown("### 📊 R-Multiple Verteilung")
        r_multiples = [t.final_r_multiple for t in closed_trades if t.final_r_multiple is not None]

        if r_multiples:
            r_dist = {
                "< 0R": len([r for r in r_multiples if r < 0]),
                "0-1R": len([r for r in r_multiples if 0 <= r < 1]),
                "1-2R": len([r for r in r_multiples if 1 <= r < 2]),
                "2-5R": len([r for r in r_multiples if 2 <= r < 5]),
                "> 5R": len([r for r in r_multiples if r >= 5])
            }

            r_dist_df = pd.DataFrame([
                {"Range": k, "Anzahl": v}
                for k, v in r_dist.items()
            ])

            fig_r_perf = px.bar(
                r_dist_df,
                x="Range",
                y="Anzahl",
                title="R-Multiple Verteilung geschlossener Trades",
                color="Anzahl",
                color_continuous_scale="Greens"
            )
            fig_r_perf.update_layout(height=400)
            st.plotly_chart(fig_r_perf, use_container_width=True)

        # Additional Charts
        st.markdown("### 📊 Zusätzliche Analytics")

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            # Product Distribution Pie Chart
            product_counts = {}
            for trade in closed_trades:
                ptype = get_product_label(trade.product_type)
                product_counts[ptype] = product_counts.get(ptype, 0) + 1

            fig_pie = px.pie(
                values=list(product_counts.values()),
                names=list(product_counts.keys()),
                title="Trades nach Produkt-Typ"
            )
            fig_pie.update_layout(height=350)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_chart2:
            # Win Rate Gauge Chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=win_rate,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Win Rate"},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen" if win_rate >= 50 else "darkred"},
                    'steps': [
                        {'range': [0, 33], 'color': "lightgray"},
                        {'range': [33, 66], 'color': "gray"},
                        {'range': [66, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            ))
            fig_gauge.update_layout(height=350)
            st.plotly_chart(fig_gauge, use_container_width=True)

        # Cumulative P&L Line Chart
        st.markdown("### 📈 Kumulative P&L Entwicklung")

        # Sort trades by close date
        sorted_trades = sorted(
            [t for t in closed_trades if t.close_date],
            key=lambda t: t.close_date
        )

        if sorted_trades:
            cumulative_pnl = []
            cumsum = 0
            dates = []

            for trade in sorted_trades:
                cumsum += (trade.final_pnl or 0)
                cumulative_pnl.append(cumsum)
                dates.append(trade.close_date)

            fig_cumulative = go.Figure()

            fig_cumulative.add_trace(go.Scatter(
                x=dates,
                y=cumulative_pnl,
                mode='lines+markers',
                name='Kumulative P&L',
                line=dict(color='royalblue', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(65, 105, 225, 0.1)'
            ))

            fig_cumulative.update_layout(
                title="Kumulative P&L über Zeit",
                xaxis_title="Datum",
                yaxis_title="P&L (€)",
                hovermode='x unified',
                height=400
            )

            st.plotly_chart(fig_cumulative, use_container_width=True)

        # Best/Worst Trades
        st.markdown("### 🏆 Best & Worst Trades")

        col_best, col_worst = st.columns(2)

        with col_best:
            st.markdown("**🥇 Best Trades (Top 3)**")
            best_trades = sorted(closed_trades, key=lambda t: t.final_pnl or 0, reverse=True)[:3]
            for i, trade in enumerate(best_trades, 1):
                st.write(f"{i}. {trade.symbol}: {format_currency(trade.final_pnl or 0)} ({format_r_multiple(trade.final_r_multiple or 0)})")

        with col_worst:
            st.markdown("**💔 Worst Trades (Bottom 3)**")
            worst_trades = sorted(closed_trades, key=lambda t: t.final_pnl or 0)[:3]
            for i, trade in enumerate(worst_trades, 1):
                st.write(f"{i}. {trade.symbol}: {format_currency(trade.final_pnl or 0)} ({format_r_multiple(trade.final_r_multiple or 0)})")


# ============================================================================
# TAB 5: TRADE-HISTORIE
# ============================================================================

with tab5:
    st.header("📋 Trade-Historie")

    all_trades = manager.get_all_trades()

    if not all_trades:
        st.info("📭 Noch keine Trades vorhanden")
    else:
        # Filter
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            status_filter = st.multiselect(
                "Status Filter",
                options=["planned", "open", "closed"],
                default=["planned", "open", "closed"],
                format_func=lambda x: f"{get_status_badge(x)} {x.title()}"
            )

        with col_f2:
            product_filter = st.multiselect(
                "Produkt Filter",
                options=["spot", "cfd_long", "cfd_short", "knockout_long", "knockout_short"],
                default=["spot", "cfd_long", "cfd_short", "knockout_long", "knockout_short"],
                format_func=lambda x: f"{get_product_badge(x)} {get_product_label(x)}"
            )

        # Filtern
        filtered_trades = [
            t for t in all_trades
            if t.status in status_filter and t.product_type in product_filter
        ]

        st.write(f"**{len(filtered_trades)} Trade(s) gefunden**")

        if filtered_trades:
            # Trade-Tabelle
            trades_data = []
            for trade in filtered_trades:
                trades_data.append({
                    "Status": f"{get_status_badge(trade.status)} {trade.status}",
                    "Symbol": f"{get_product_badge(trade.product_type)} {trade.symbol}",
                    "Entry": format_currency(trade.entry_price),
                    "Stop": format_currency(trade.current_stop),
                    "Units": f"{trade.units:,}",
                    "Investment": format_currency(trade.investment),
                    "R-Amount": format_currency(trade.risk_amount),
                    "Close Price": format_currency(trade.close_price) if trade.close_price else "-",
                    "P&L": format_currency(trade.final_pnl) if trade.final_pnl is not None else "-",
                    "R-Multiple": format_r_multiple(trade.final_r_multiple) if trade.final_r_multiple is not None else "-",
                    "Date": trade.created_at
                })

            trades_df = pd.DataFrame(trades_data)
            st.dataframe(trades_df, use_container_width=True, hide_index=True)


# ============================================================================
# TAB 6: SETTINGS & EXPORT
# ============================================================================

with tab6:
    st.header("⚙️ Settings & Export")

    # ========================================================================
    # EXPORT SECTION
    # ========================================================================

    st.subheader("📤 Export")

    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        st.markdown("**📊 CSV Export**")
        st.markdown("*Exportiere Trade-History als CSV*")

        if st.button("📥 Export All Trades (CSV)", use_container_width=True):
            all_trades = manager.get_all_trades()
            if all_trades:
                csv_data = DataExporter.export_trades_to_csv(all_trades)
                st.download_button(
                    label="💾 Download CSV",
                    data=csv_data,
                    file_name=f"trades_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success(f"✅ {len(all_trades)} Trades exportiert")
            else:
                st.warning("⚠️ Keine Trades zum Exportieren")

        # Performance CSV
        if st.button("📥 Export Performance (CSV)", use_container_width=True):
            closed_trades = [t for t in manager.get_all_trades() if t.status == "closed"]
            if closed_trades:
                csv_data = DataExporter.export_performance_to_csv(closed_trades)
                st.download_button(
                    label="💾 Download Performance CSV",
                    data=csv_data,
                    file_name=f"performance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success(f"✅ {len(closed_trades)} geschlossene Trades exportiert")
            else:
                st.warning("⚠️ Keine geschlossenen Trades")

    with col_e2:
        st.markdown("**💾 JSON Backup**")
        st.markdown("*Vollständiges Backup (inkl. Teilverkäufe)*")

        if st.button("📥 Create Backup (JSON)", use_container_width=True):
            json_data = DataExporter.export_trades_to_json(manager)
            st.download_button(
                label="💾 Download Backup",
                data=json_data,
                file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
            st.success("✅ Backup erstellt")

    with col_e3:
        st.markdown("**💰 Teilverkäufe CSV**")
        st.markdown("*Exportiere alle Teilverkäufe*")

        if st.button("📥 Export Partial Sales (CSV)", use_container_width=True):
            analytics_data = PartialSaleManager.analyze_partial_sales(manager.get_all_trades())
            if analytics_data['total_partial_sales'] > 0:
                csv_data = DataExporter.export_partial_sales_to_csv(analytics_data)
                st.download_button(
                    label="💾 Download Partial Sales CSV",
                    data=csv_data,
                    file_name=f"partial_sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success(f"✅ {analytics_data['total_partial_sales']} Teilverkäufe exportiert")
            else:
                st.warning("⚠️ Keine Teilverkäufe vorhanden")

    st.markdown("---")

    # ========================================================================
    # IMPORT SECTION
    # ========================================================================

    st.subheader("📥 Import & Restore")

    st.warning("⚠️ **Achtung**: Import überschreibt alle bestehenden Trades!")

    uploaded_file = st.file_uploader(
        "JSON Backup hochladen",
        type=['json'],
        help="Lade ein JSON Backup hoch um deine Trades wiederherzustellen"
    )

    if uploaded_file is not None:
        col_i1, col_i2 = st.columns([3, 1])

        with col_i1:
            st.info(f"📁 Datei: {uploaded_file.name} ({uploaded_file.size} bytes)")

        with col_i2:
            if st.button("🔄 Restore", type="primary", use_container_width=True):
                try:
                    json_string = uploaded_file.read().decode('utf-8')
                    success = DataExporter.import_trades_from_json(manager, json_string)

                    if success:
                        st.success("✅ Backup erfolgreich wiederhergestellt!")
                        st.rerun()
                    else:
                        st.error("❌ Import fehlgeschlagen - ungültiges Format")
                except Exception as e:
                    st.error(f"❌ Fehler beim Import: {str(e)}")

    st.markdown("---")

    # ========================================================================
    # DATA MANAGEMENT
    # ========================================================================

    st.subheader("🗑️ Daten-Verwaltung")

    col_d1, col_d2, col_d3 = st.columns(3)

    with col_d1:
        st.metric("Total Trades", len(manager.get_all_trades()))

    with col_d2:
        planned = len([t for t in manager.get_all_trades() if t.status == "planned"])
        st.metric("Geplante Trades", planned)

    with col_d3:
        open_trades = len([t for t in manager.get_all_trades() if t.status == "open"])
        st.metric("Offene Trades", open_trades)

    st.markdown("---")

    # Danger Zone
    st.markdown("### ⚠️ Danger Zone")

    col_danger1, col_danger2 = st.columns([3, 1])

    with col_danger1:
        st.warning("**Alle Trades löschen** - Diese Aktion kann nicht rückgängig gemacht werden!")

    with col_danger2:
        if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
            # Confirm dialog
            if 'confirm_clear' not in st.session_state:
                st.session_state.confirm_clear = False

            st.session_state.confirm_clear = True

    if st.session_state.get('confirm_clear', False):
        st.error("🚨 **Bist du sicher?** Diese Aktion löscht ALLE Trades unwiderruflich!")

        col_confirm1, col_confirm2, col_confirm3 = st.columns([1, 1, 1])

        with col_confirm1:
            if st.button("❌ Abbrechen", use_container_width=True):
                st.session_state.confirm_clear = False
                st.rerun()

        with col_confirm2:
            pass  # Spacer

        with col_confirm3:
            if st.button("✅ JA, ALLES LÖSCHEN", type="primary", use_container_width=True):
                # Clear all trades
                st.session_state.trade_manager = TradeManager()
                st.session_state.confirm_clear = False
                st.success("✅ Alle Daten gelöscht")
                st.rerun()

    st.markdown("---")

    # ========================================================================
    # PORTFOLIO SETTINGS
    # ========================================================================

    st.subheader("💼 Portfolio Settings")

    st.info("💡 Diese Einstellungen sind für zukünftige Features geplant (Auto-Berechnung, Alerts, etc.)")

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        portfolio_value = st.number_input(
            "Portfolio Value (€)",
            min_value=1000.0,
            value=st.session_state.get('portfolio_value', 50000.0),
            step=1000.0,
            help="Dein Gesamt-Portfolio Wert"
        )
        st.session_state.portfolio_value = portfolio_value

    with col_s2:
        risk_percentage = st.number_input(
            "Risk per Trade (%)",
            min_value=0.1,
            max_value=5.0,
            value=st.session_state.get('risk_percentage', 1.0),
            step=0.1,
            help="Max Risiko pro Trade in % vom Portfolio"
        )
        st.session_state.risk_percentage = risk_percentage

    st.markdown("---")

    # App Info
    st.subheader("ℹ️ App Info")

    info_data = {
        "Version": "1.0.0",
        "Phase": "5 & 6 Complete",
        "Features": "Calculator, Trade Management, Partial Sales, Analytics, Export/Import",
        "Supported Products": "Spot, CFD Long/Short, Knockout Long/Short"
    }

    for key, value in info_data.items():
        st.text(f"{key}: {value}")


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("*🎯 Unified Trading Risk Management v1.0 - Phase 5 & 6 Complete*")
