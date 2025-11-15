#!/usr/bin/env python3
"""
Funktionalitäts-Tests für alle Trading Tools
"""

from position_size_calculator import PositionSizeCalculator
from hebelprodukt_tool import AdvancedPositionSizeCalculator

def test_position_size_calculator():
    """Test Basic Position Size Calculator"""
    print("=" * 70)
    print("🧪 TEST 1: Basic Position Size Calculator")
    print("=" * 70)

    calc = PositionSizeCalculator(50000, risk_percentage=1.0)

    # Test 1: Normale Berechnung
    print("\n✅ Test 1.1: Normale Berechnung (Entry > Stop)")
    result = calc.calculate_position_size(120.00, 115.00)
    print(f"   Anzahl Aktien: {result['position_details']['anzahl_aktien']}")
    print(f"   Max Risiko: {result['depot_info']['max_risiko']}")
    print(f"   Validation: {result['validation']['verlust_check']}")
    assert result['validation']['verlust_check'] == True, "Risiko-Check sollte TRUE sein"

    # Test 2: Fehlerfall Entry <= Stop
    print("\n✅ Test 1.2: Fehlerbehandlung (Entry <= Stop)")
    try:
        calc.calculate_position_size(100.00, 105.00)
        print("   ❌ FEHLER: Exception sollte geworfen werden!")
        return False
    except ValueError as e:
        print(f"   ✅ Korrekt abgefangen: {e}")

    # Test 3: Portfolio-Update
    print("\n✅ Test 1.3: Portfolio Update")
    original_risk = calc.max_risk_amount
    calc.update_portfolio(100000)
    new_risk = calc.max_risk_amount
    print(f"   Original Risiko: €{original_risk:.2f}")
    print(f"   Neues Risiko: €{new_risk:.2f}")
    assert new_risk == 1000.0, f"Neues Risiko sollte €1000 sein, ist aber €{new_risk}"

    # Test 4: Batch-Berechnung
    print("\n✅ Test 1.4: Batch-Berechnung")
    trades = [
        {'symbol': 'TEST1', 'entry': 100.0, 'stop_loss': 95.0},
        {'symbol': 'TEST2', 'entry': 50.0, 'stop_loss': 48.0}
    ]
    results = calc.batch_calculate(trades)
    print(f"   Anzahl Berechnungen: {len(results)}")
    print(f"   Test1 Aktien: {results[0]['position_details']['anzahl_aktien']}")
    assert len(results) == 2, "Sollte 2 Ergebnisse zurückgeben"

    print("\n✅ ALLE TESTS BESTANDEN für PositionSizeCalculator!\n")
    return True

def test_hebelprodukt_calculator():
    """Test Advanced Calculator mit Hebelprodukten"""
    print("=" * 70)
    print("🧪 TEST 2: Advanced Hebelprodukt Calculator")
    print("=" * 70)

    calc = AdvancedPositionSizeCalculator(50000, risk_percentage=1.0)

    # Test 1: Spot Position (wie normal)
    print("\n✅ Test 2.1: Spot Position")
    result = calc.calculate_position_size(100.0, 95.0, product_type="spot")
    print(f"   Product Type: {result['product_info']['product_type']}")
    print(f"   Leverage: {result['product_info']['leverage']}")
    print(f"   Einheiten: {result['position_details']['anzahl_einheiten']}")
    assert result['product_info']['leverage'] == 1.0, "Spot sollte Hebel 1.0 haben"

    # Test 2: CFD Long mit Hebel
    print("\n✅ Test 2.2: CFD Long mit Hebel 5")
    result = calc.calculate_position_size(
        100.0, 95.0,
        product_type="cfd_long",
        leverage=5.0,
        spread_percent=0.2,
        overnight_percent=0.01,
        holding_days=10
    )
    print(f"   Product Type: {result['product_info']['product_type']}")
    print(f"   Actual Investment: €{result['position_details']['actual_investment']:.2f}")
    print(f"   Notional Value: €{result['position_details']['notional_value']:.2f}")
    print(f"   Spread Kosten: €{result['cost_breakdown']['spread_kosten_total']:.2f}")
    print(f"   Overnight Kosten: €{result['cost_breakdown']['overnight_kosten_total']:.2f}")
    assert result['product_info']['is_short'] == False, "CFD Long sollte nicht short sein"

    # Test 3: CFD Short (inverse Logik)
    print("\n✅ Test 2.3: CFD Short Position")
    result = calc.calculate_position_size(
        100.0, 105.0,  # Bei Short: Entry < Stop!
        product_type="cfd_short",
        leverage=5.0
    )
    print(f"   Is Short: {result['product_info']['is_short']}")
    print(f"   1R Target: €{result['risk_reward_targets']['1R_target']:.2f}")
    assert result['product_info']['is_short'] == True, "CFD Short sollte short sein"
    assert result['risk_reward_targets']['1R_target'] < 100.0, "Short Target sollte unter Entry liegen"

    # Test 4: Knockout Long
    print("\n✅ Test 2.4: Knockout Long (kein Overnight)")
    result = calc.calculate_position_size(
        100.0, 95.0,
        product_type="knockout_long",
        leverage=10.0,
        spread_percent=1.0
    )
    print(f"   Overnight Kosten: €{result['cost_breakdown']['overnight_kosten_total']:.2f}")
    assert result['cost_breakdown']['overnight_kosten_total'] == 0, "Knockout sollte keine Overnight-Kosten haben"

    # Test 5: Fehlerfall Short mit falschen Preisen
    print("\n✅ Test 2.5: Fehlerbehandlung Short (Entry > Stop)")
    try:
        calc.calculate_position_size(100.0, 95.0, product_type="cfd_short")
        print("   ❌ FEHLER: Exception sollte geworfen werden!")
        return False
    except ValueError as e:
        print(f"   ✅ Korrekt abgefangen: {e}")

    print("\n✅ ALLE TESTS BESTANDEN für AdvancedCalculator!\n")
    return True

def test_r_multiple_calculations():
    """Test R-Multiple Berechnungen"""
    print("=" * 70)
    print("🧪 TEST 3: R-Multiple Target Berechnungen")
    print("=" * 70)

    calc = PositionSizeCalculator(50000, risk_percentage=1.0)

    # Test mit bekannten Werten
    entry = 100.0
    stop = 95.0
    risk_per_share = entry - stop  # 5.0

    result = calc.calculate_position_size(entry, stop)

    # Erwartete Targets:
    # 1R = Entry + (1 * risk) = 100 + 5 = 105
    # 2R = Entry + (2 * risk) = 100 + 10 = 110
    # 5R = Entry + (5 * risk) = 100 + 25 = 125

    print(f"\n✅ Entry: €{entry}, Stop: €{stop}, Risk/Share: €{risk_per_share}")
    print(f"   1R Target: {result['risk_reward_targets']['1R_target']} (erwartet: €105.00)")
    print(f"   2R Target: {result['risk_reward_targets']['2R_target']} (erwartet: €110.00)")
    print(f"   5R Target: {result['risk_reward_targets']['5R_target']} (erwartet: €125.00)")

    assert result['risk_reward_targets']['1R_target'] == "€105.00", "1R Target falsch"
    assert result['risk_reward_targets']['2R_target'] == "€110.00", "2R Target falsch"
    assert result['risk_reward_targets']['5R_target'] == "€125.00", "5R Target falsch"

    print("\n✅ R-Multiple Berechnungen KORREKT!\n")
    return True

def test_edge_cases():
    """Test Edge Cases und Grenzwerte"""
    print("=" * 70)
    print("🧪 TEST 4: Edge Cases & Grenzwerte")
    print("=" * 70)

    # Test 1: Sehr kleines Risiko
    print("\n✅ Test 4.1: Sehr kleines Risiko (0.01%)")
    calc = PositionSizeCalculator(50000, risk_percentage=0.01)
    result = calc.calculate_position_size(100.0, 99.0)
    print(f"   Max Risiko: {result['depot_info']['max_risiko']}")
    print(f"   Anzahl Aktien: {result['position_details']['anzahl_aktien']}")

    # Test 2: Sehr großes Risiko
    print("\n✅ Test 4.2: Großes Risiko (5%)")
    calc = PositionSizeCalculator(50000, risk_percentage=5.0)
    result = calc.calculate_position_size(100.0, 95.0)
    print(f"   Max Risiko: {result['depot_info']['max_risiko']}")
    print(f"   Position Wert: {result['position_details']['position_wert']}")

    # Test 3: Sehr enger Stop
    print("\n✅ Test 4.3: Sehr enger Stop (€0.10)")
    calc = PositionSizeCalculator(50000, risk_percentage=1.0)
    result = calc.calculate_position_size(100.0, 99.90)
    print(f"   Risiko pro Aktie: {result['trade_setup']['risiko_pro_aktie']}")
    print(f"   Anzahl Aktien: {result['position_details']['anzahl_aktien']}")

    # Test 4: Sehr weiter Stop
    print("\n✅ Test 4.4: Sehr weiter Stop (€50)")
    result = calc.calculate_position_size(100.0, 50.0)
    print(f"   Risiko pro Aktie: {result['trade_setup']['risiko_pro_aktie']}")
    print(f"   Anzahl Aktien: {result['position_details']['anzahl_aktien']}")

    print("\n✅ ALLE EDGE CASES GETESTET!\n")
    return True

# Main Test Runner
if __name__ == "__main__":
    print("\n" + "🎯" * 35)
    print("🚀 STARTE VOLLSTÄNDIGE FUNKTIONALITÄTS-TESTS")
    print("🎯" * 35 + "\n")

    all_passed = True

    try:
        all_passed &= test_position_size_calculator()
        all_passed &= test_hebelprodukt_calculator()
        all_passed &= test_r_multiple_calculations()
        all_passed &= test_edge_cases()

        print("\n" + "=" * 70)
        if all_passed:
            print("✅✅✅ ALLE TESTS ERFOLGREICH BESTANDEN! ✅✅✅")
        else:
            print("❌ EINIGE TESTS FEHLGESCHLAGEN")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ KRITISCHER FEHLER: {e}")
        import traceback
        traceback.print_exc()
