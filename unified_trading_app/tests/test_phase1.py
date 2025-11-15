#!/usr/bin/env python3
"""
Phase 1 Tests: UnifiedPositionCalculator & TradeManager

Testet:
- Alle Produkt-Typen (Spot, CFD, Knockout)
- Long/Short Logik
- Hebel-Berechnungen
- Kosten-Integration
- Trade-Lifecycle Management
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import UnifiedPositionCalculator, TradeManager, Trade


def test_calculator_spot():
    """Test 1: Spot-Position Berechnung"""
    print("\n" + "="*70)
    print("🧪 TEST 1: Spot-Position Berechnung")
    print("="*70)

    calc = UnifiedPositionCalculator(portfolio_value=50000, risk_percentage=1.0)
    result = calc.calculate_position(
        entry_price=120.0,
        stop_loss=115.0,
        product_type="spot"
    )

    # Assertions
    assert result.product_type == "spot", "Product type sollte 'spot' sein"
    assert result.leverage == 1.0, "Spot sollte Hebel 1.0 haben"
    assert result.is_short == False, "Spot Long sollte nicht short sein"
    assert result.units == 100, f"Sollte 100 Einheiten sein, ist {result.units}"
    assert result.max_risk == 500.0, "Max Risiko sollte €500 sein"
    assert result.target_1r == 125.0, "1R Target sollte €125 sein"
    assert result.overnight_cost_total == 0, "Spot sollte keine Overnight-Kosten haben"

    # Risiko-Validierung
    actual_risk = result.units * result.basis_risk_per_unit
    assert abs(actual_risk - 500.0) < 1.0, f"Risiko sollte ~€500 sein, ist €{actual_risk}"

    print(f"✅ Product: {result.product_type}")
    print(f"✅ Einheiten: {result.units}")
    print(f"✅ Investment: €{result.actual_investment:,.2f}")
    print(f"✅ Max Risiko: €{result.max_risk:.2f}")
    print(f"✅ 1R Target: €{result.target_1r:.2f}")
    print("✅ BESTANDEN")

    return True


def test_calculator_cfd_long():
    """Test 2: CFD Long mit Hebel"""
    print("\n" + "="*70)
    print("🧪 TEST 2: CFD Long mit Hebel 5x")
    print("="*70)

    calc = UnifiedPositionCalculator(portfolio_value=50000, risk_percentage=1.0)
    result = calc.calculate_position(
        entry_price=120.0,
        stop_loss=115.0,
        product_type="cfd_long",
        leverage=5.0,
        spread_percent=0.2,
        overnight_percent=0.01,
        holding_days=10
    )

    # Assertions
    assert result.product_type == "cfd_long", "Product type sollte 'cfd_long' sein"
    assert result.leverage == 5.0, "Hebel sollte 5.0 sein"
    assert result.is_short == False, "CFD Long sollte nicht short sein"
    assert result.units < 100, "Mit Hebel sollten weniger Einheiten nötig sein"
    assert result.spread_cost_total > 0, "Spread-Kosten sollten > 0 sein"
    assert result.overnight_cost_total > 0, "Overnight-Kosten sollten > 0 sein"
    assert result.notional_value > result.actual_investment, "Exposure sollte größer als Investment sein"

    # Hebel-Ratio prüfen
    expected_exposure = result.actual_investment * 5.0
    assert abs(result.notional_value - expected_exposure) < 1.0, "Exposure sollte Investment * Hebel sein"

    print(f"✅ Product: {result.product_type} (Hebel {result.leverage}x)")
    print(f"✅ Einheiten: {result.units}")
    print(f"✅ Investment: €{result.actual_investment:,.2f}")
    print(f"✅ Exposure: €{result.notional_value:,.2f}")
    print(f"✅ Spread: €{result.spread_cost_total:.2f}")
    print(f"✅ Overnight: €{result.overnight_cost_total:.2f}")
    print("✅ BESTANDEN")

    return True


def test_calculator_cfd_short():
    """Test 3: CFD Short Position"""
    print("\n" + "="*70)
    print("🧪 TEST 3: CFD Short Position")
    print("="*70)

    calc = UnifiedPositionCalculator(portfolio_value=50000, risk_percentage=1.0)
    result = calc.calculate_position(
        entry_price=120.0,
        stop_loss=125.0,  # Bei Short: Stop > Entry
        product_type="cfd_short",
        leverage=5.0
    )

    # Assertions
    assert result.product_type == "cfd_short", "Product type sollte 'cfd_short' sein"
    assert result.is_short == True, "CFD Short sollte short sein"
    assert result.target_1r < result.entry_price, "Bei Short sollte 1R Target unter Entry liegen"
    assert result.target_2r < result.target_1r, "Targets sollten absteigend sein"

    print(f"✅ Product: {result.product_type} (Short: {result.is_short})")
    print(f"✅ Entry: €{result.entry_price:.2f}")
    print(f"✅ Stop: €{result.stop_loss:.2f}")
    print(f"✅ 1R Target: €{result.target_1r:.2f} (unter Entry = Gewinn)")
    print("✅ BESTANDEN")

    return True


def test_calculator_knockout():
    """Test 4: Knockout ohne Overnight"""
    print("\n" + "="*70)
    print("🧪 TEST 4: Knockout Long (kein Overnight)")
    print("="*70)

    calc = UnifiedPositionCalculator(portfolio_value=50000, risk_percentage=1.0)
    result = calc.calculate_position(
        entry_price=120.0,
        stop_loss=115.0,
        product_type="knockout_long",
        leverage=10.0,
        spread_percent=1.0
    )

    # Assertions
    assert result.product_type == "knockout_long", "Product type sollte 'knockout_long' sein"
    assert result.leverage == 10.0, "Hebel sollte 10.0 sein"
    assert result.overnight_cost_total == 0, "Knockout sollte keine Overnight-Kosten haben"
    assert result.spread_cost_total > 0, "Spread-Kosten sollten vorhanden sein"

    print(f"✅ Product: {result.product_type} (Hebel {result.leverage}x)")
    print(f"✅ Overnight: €{result.overnight_cost_total:.2f} (sollte 0 sein)")
    print(f"✅ Spread: €{result.spread_cost_total:.2f}")
    print("✅ BESTANDEN")

    return True


def test_calculator_risk_accuracy():
    """Test 5: Risiko-Genauigkeit über verschiedene Szenarien"""
    print("\n" + "="*70)
    print("🧪 TEST 5: Risiko-Genauigkeit (1% Regel)")
    print("="*70)

    depot = 50000
    expected_risk = 500  # 1% von 50000
    calc = UnifiedPositionCalculator(portfolio_value=depot, risk_percentage=1.0)

    test_cases = [
        {"entry": 100, "stop": 95, "type": "spot"},
        {"entry": 50, "stop": 49, "type": "spot"},
        {"entry": 200, "stop": 180, "type": "spot"},
    ]

    all_ok = True
    for i, case in enumerate(test_cases, 1):
        result = calc.calculate_position(
            entry_price=case['entry'],
            stop_loss=case['stop'],
            product_type=case['type']
        )

        actual_risk = result.units * result.basis_risk_per_unit
        deviation = abs(actual_risk - expected_risk)

        print(f"  Case {i}: Entry €{case['entry']}, Stop €{case['stop']}")
        print(f"    Risiko: €{actual_risk:.2f} (Abweichung: €{deviation:.2f})")

        if deviation < 1.0:
            print(f"    ✅ OK")
        else:
            print(f"    ❌ Zu große Abweichung!")
            all_ok = False

    assert all_ok, "Risiko-Berechnungen sollten exakt sein"
    print("✅ BESTANDEN")

    return True


def test_calculator_validation():
    """Test 6: Input Validierung"""
    print("\n" + "="*70)
    print("🧪 TEST 6: Input Validierung")
    print("="*70)

    calc = UnifiedPositionCalculator(portfolio_value=50000, risk_percentage=1.0)

    # Test 1: Long Entry <= Stop sollte fehlschlagen
    print("  Test: Long Entry <= Stop (sollte fehlschlagen)")
    try:
        calc.calculate_position(100, 105, product_type="spot")
        print("    ❌ Sollte Exception werfen!")
        return False
    except ValueError as e:
        print(f"    ✅ Korrekt abgefangen: {e}")

    # Test 2: Short Entry >= Stop sollte fehlschlagen
    print("  Test: Short Entry >= Stop (sollte fehlschlagen)")
    try:
        calc.calculate_position(100, 95, product_type="cfd_short")
        print("    ❌ Sollte Exception werfen!")
        return False
    except ValueError as e:
        print(f"    ✅ Korrekt abgefangen: {e}")

    print("✅ BESTANDEN")
    return True


def test_trade_manager_crud():
    """Test 7: TradeManager CRUD Operationen"""
    print("\n" + "="*70)
    print("🧪 TEST 7: TradeManager CRUD")
    print("="*70)

    manager = TradeManager()

    # Create
    print("  Test: Trade erstellen")
    trade_id = manager.create_trade(
        symbol="NVIDIA",
        product_type="spot",
        entry_price=120.0,
        stop_loss=115.0,
        units=100,
        investment=12000.0,
        exposure=12000.0,
        risk_amount=500.0,
        target_1r=125.0,
        target_2r=130.0,
        target_5r=145.0,
        status="planned"
    )
    assert trade_id is not None, "Trade ID sollte nicht None sein"
    print(f"    ✅ Trade erstellt: {trade_id[:8]}...")

    # Read
    print("  Test: Trade abrufen")
    trade = manager.get_trade(trade_id)
    assert trade is not None, "Trade sollte existieren"
    assert trade.symbol == "NVIDIA", "Symbol sollte NVIDIA sein"
    assert trade.status == "planned", "Status sollte 'planned' sein"
    print(f"    ✅ Trade gefunden: {trade.symbol}")

    # Update
    print("  Test: Trade updaten")
    success = manager.update_trade(trade_id, {'status': 'open', 'current_stop': 117.0})
    assert success == True, "Update sollte erfolgreich sein"
    trade = manager.get_trade(trade_id)
    assert trade.status == "open", "Status sollte jetzt 'open' sein"
    assert trade.current_stop == 117.0, "Stop sollte updated sein"
    print(f"    ✅ Trade updated: Status={trade.status}, Stop=€{trade.current_stop}")

    # Close
    print("  Test: Trade schließen")
    success = manager.close_trade(trade_id, close_price=130.0)
    assert success == True, "Close sollte erfolgreich sein"
    trade = manager.get_trade(trade_id)
    assert trade.status == "closed", "Status sollte 'closed' sein"
    assert trade.close_price == 130.0, "Close price sollte €130 sein"
    assert trade.final_pnl is not None, "P&L sollte berechnet sein"
    print(f"    ✅ Trade geschlossen: P&L=€{trade.final_pnl:.2f}, R={trade.final_r_multiple:.2f}")

    # Delete
    print("  Test: Trade löschen")
    success = manager.delete_trade(trade_id)
    assert success == True, "Delete sollte erfolgreich sein"
    trade = manager.get_trade(trade_id)
    assert trade is None, "Trade sollte nicht mehr existieren"
    print(f"    ✅ Trade gelöscht")

    print("✅ BESTANDEN")
    return True


def test_trade_manager_filtering():
    """Test 8: TradeManager Filterung"""
    print("\n" + "="*70)
    print("🧪 TEST 8: TradeManager Filterung")
    print("="*70)

    manager = TradeManager()

    # Erstelle verschiedene Trades
    id1 = manager.create_trade(
        symbol="AAPL", product_type="spot", entry_price=180, stop_loss=175,
        units=50, investment=9000, exposure=9000, risk_amount=250,
        target_1r=185, target_2r=190, target_5r=205, status="planned"
    )
    id2 = manager.create_trade(
        symbol="TSLA", product_type="cfd_long", entry_price=250, stop_loss=240,
        units=25, investment=6250, exposure=31250, risk_amount=250,
        target_1r=260, target_2r=270, target_5r=300, leverage=5.0, status="open"
    )
    id3 = manager.create_trade(
        symbol="MSFT", product_type="spot", entry_price=380, stop_loss=370,
        units=25, investment=9500, exposure=9500, risk_amount=250,
        target_1r=390, target_2r=400, target_5r=430, status="open"
    )

    manager.close_trade(id1, close_price=185.0)

    # Test Filterung
    print("  Test: Filter nach Status")
    planned = manager.get_planned_trades()
    open_trades = manager.get_open_trades()
    closed = manager.get_closed_trades()

    assert len(planned) == 0, f"Sollte 0 geplante Trades haben, hat {len(planned)}"
    assert len(open_trades) == 2, f"Sollte 2 offene Trades haben, hat {len(open_trades)}"
    assert len(closed) == 1, f"Sollte 1 geschlossenen Trade haben, hat {len(closed)}"
    print(f"    ✅ Planned: {len(planned)}, Open: {len(open_trades)}, Closed: {len(closed)}")

    # Test Produkt-Typ Filter
    print("  Test: Filter nach Produkt-Typ")
    spot_trades = manager.get_trades_by_product_type("spot")
    cfd_trades = manager.get_trades_by_product_type("cfd_long")

    assert len(spot_trades) == 2, f"Sollte 2 Spot-Trades haben"
    assert len(cfd_trades) == 1, f"Sollte 1 CFD-Trade haben"
    print(f"    ✅ Spot: {len(spot_trades)}, CFD: {len(cfd_trades)}")

    print("✅ BESTANDEN")
    return True


def test_trade_manager_metrics():
    """Test 9: Portfolio Metriken"""
    print("\n" + "="*70)
    print("🧪 TEST 9: Portfolio Metriken")
    print("="*70)

    manager = TradeManager()

    # Erstelle und schließe Trades
    id1 = manager.create_trade(
        symbol="WIN", product_type="spot", entry_price=100, stop_loss=95,
        units=100, investment=10000, exposure=10000, risk_amount=500,
        target_1r=105, target_2r=110, target_5r=125, status="open"
    )
    manager.close_trade(id1, close_price=110.0)  # Gewinn-Trade

    id2 = manager.create_trade(
        symbol="LOSS", product_type="spot", entry_price=100, stop_loss=95,
        units=100, investment=10000, exposure=10000, risk_amount=500,
        target_1r=105, target_2r=110, target_5r=125, status="open"
    )
    manager.close_trade(id2, close_price=95.0)  # Verlust-Trade

    id3 = manager.create_trade(
        symbol="OPEN", product_type="cfd_long", entry_price=100, stop_loss=95,
        units=50, investment=5000, exposure=25000, risk_amount=500,
        target_1r=105, target_2r=110, target_5r=125, leverage=5.0, status="open"
    )

    # Metriken abrufen
    metrics = manager.calculate_portfolio_metrics()

    print(f"  Total Trades: {metrics['total_trades']}")
    print(f"  Open Trades: {metrics['open_trades']}")
    print(f"  Closed Trades: {metrics['closed_trades']}")
    print(f"  Total Investment: €{metrics['total_investment']:,.2f}")
    print(f"  Total Exposure: €{metrics['total_exposure']:,.2f}")
    print(f"  Realized P&L: €{metrics['realized_pnl']:,.2f}")
    print(f"  Win Rate: {metrics['win_rate']:.1f}%")
    print(f"  Avg R-Multiple: {metrics['avg_r_multiple']:.2f}R")

    # Assertions
    assert metrics['total_trades'] == 3, "Sollte 3 Total Trades haben"
    assert metrics['open_trades'] == 1, "Sollte 1 offenen Trade haben"
    assert metrics['closed_trades'] == 2, "Sollte 2 geschlossene Trades haben"
    assert metrics['win_rate'] == 50.0, "Win Rate sollte 50% sein (1 von 2)"
    assert metrics['total_investment'] > 0, "Investment sollte > 0 sein"
    assert metrics['total_exposure'] > metrics['total_investment'], "Exposure sollte > Investment sein (wegen Hebel)"

    print("✅ BESTANDEN")
    return True


# Test Runner
if __name__ == "__main__":
    print("\n" + "🎯"*35)
    print("🚀 PHASE 1 TESTS - UnifiedPositionCalculator & TradeManager")
    print("🎯"*35)

    tests = [
        ("Spot-Position", test_calculator_spot),
        ("CFD Long mit Hebel", test_calculator_cfd_long),
        ("CFD Short", test_calculator_cfd_short),
        ("Knockout", test_calculator_knockout),
        ("Risiko-Genauigkeit", test_calculator_risk_accuracy),
        ("Input Validierung", test_calculator_validation),
        ("TradeManager CRUD", test_trade_manager_crud),
        ("TradeManager Filterung", test_trade_manager_filtering),
        ("Portfolio Metriken", test_trade_manager_metrics),
    ]

    results = []
    failed = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            if not success:
                failed.append(test_name)
        except AssertionError as e:
            print(f"\n❌ FEHLER: {e}")
            results.append((test_name, False))
            failed.append(test_name)
        except Exception as e:
            print(f"\n❌ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
            failed.append(test_name)

    # Zusammenfassung
    print("\n" + "="*70)
    print("📊 TEST-ZUSAMMENFASSUNG")
    print("="*70)

    for test_name, success in results:
        status = "✅ BESTANDEN" if success else "❌ FEHLER"
        print(f"  {test_name}: {status}")

    passed = len([r for r in results if r[1]])
    total = len(results)

    print("\n" + "="*70)
    if failed:
        print(f"❌ {len(failed)} von {total} Tests fehlgeschlagen:")
        for name in failed:
            print(f"   - {name}")
    else:
        print(f"✅✅✅ ALLE {total} TESTS BESTANDEN! ✅✅✅")
    print("="*70 + "\n")
