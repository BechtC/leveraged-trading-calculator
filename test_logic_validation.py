#!/usr/bin/env python3
"""
Logik-Validierungs-Tests für komplexe Berechnungen
"""

from position_size_calculator import PositionSizeCalculator
from hebelprodukt_tool import AdvancedPositionSizeCalculator

def test_risk_calculation_accuracy():
    """Teste ob 1% Risiko exakt eingehalten wird"""
    print("="*70)
    print("🧪 TEST: Risiko-Berechnungs-Genauigkeit")
    print("="*70)

    depot = 50000
    risk_pct = 1.0
    expected_risk = 500  # 1% von 50000

    calc = PositionSizeCalculator(depot, risk_pct)

    test_cases = [
        {"entry": 100, "stop": 95, "risk_per_share": 5},
        {"entry": 50, "stop": 49, "risk_per_share": 1},
        {"entry": 200, "stop": 180, "risk_per_share": 20},
        {"entry": 10.50, "stop": 10.00, "risk_per_share": 0.50},
    ]

    all_correct = True

    for i, case in enumerate(test_cases, 1):
        result = calc.calculate_position_size(case['entry'], case['stop'])

        # Parse die formatierten Strings zurück zu Numbers
        anzahl = int(result['position_details']['anzahl_aktien'])
        actual_risk = anzahl * case['risk_per_share']

        print(f"\n✅ Test Case {i}:")
        print(f"   Entry: €{case['entry']}, Stop: €{case['stop']}")
        print(f"   Risiko/Aktie: €{case['risk_per_share']}")
        print(f"   Anzahl Aktien: {anzahl}")
        print(f"   Tatsächliches Risiko: €{actual_risk:.2f}")
        print(f"   Erwartetes Risiko: €{expected_risk:.2f}")
        print(f"   Abweichung: €{abs(actual_risk - expected_risk):.2f}")

        # Toleranz von €0.50 wegen Integer-Rundung
        if abs(actual_risk - expected_risk) < 1.0:
            print(f"   ✅ KORREKT (innerhalb Toleranz)")
        else:
            print(f"   ❌ FEHLER: Zu große Abweichung!")
            all_correct = False

    print(f"\n{'✅ ALLE TESTS BESTANDEN' if all_correct else '❌ FEHLER GEFUNDEN'}\n")
    return all_correct

def test_leverage_calculations():
    """Teste Hebel-Berechnungen"""
    print("="*70)
    print("🧪 TEST: Hebel-Produkt Berechnungen")
    print("="*70)

    depot = 50000
    calc = AdvancedPositionSizeCalculator(depot, risk_percentage=1.0)

    print("\n✅ Test: Vergleich Spot vs. CFD mit Hebel 5")

    # Spot (kein Hebel)
    spot_result = calc.calculate_position_size(100, 95, product_type="spot")

    # CFD mit Hebel 5
    cfd_result = calc.calculate_position_size(
        100, 95,
        product_type="cfd_long",
        leverage=5.0,
        spread_percent=0.0,  # Ohne Kosten für Vergleich
        overnight_percent=0.0
    )

    spot_units = spot_result['position_details']['anzahl_einheiten']
    cfd_units = cfd_result['position_details']['anzahl_einheiten']

    print(f"   Spot Einheiten: {spot_units}")
    print(f"   CFD Einheiten: {cfd_units}")
    print(f"   Verhältnis: {spot_units / cfd_units:.1f}:1")

    # Bei Hebel 5 sollten wir 1/5 der Einheiten brauchen (weil effektives Risiko 5x höher)
    expected_ratio = 5.0
    actual_ratio = spot_units / cfd_units

    print(f"   Erwartetes Verhältnis: {expected_ratio}:1")
    print(f"   Tatsächliches Verhältnis: {actual_ratio:.1f}:1")

    if abs(actual_ratio - expected_ratio) < 0.1:
        print(f"   ✅ Hebel-Berechnung KORREKT")
        return True
    else:
        print(f"   ❌ Hebel-Berechnung FEHLER")
        return False

def test_cost_impact():
    """Teste Einfluss von Spread und Overnight-Kosten"""
    print("\n"+"="*70)
    print("🧪 TEST: Kosten-Impact auf Positionsgröße")
    print("="*70)

    depot = 50000
    calc = AdvancedPositionSizeCalculator(depot, risk_percentage=1.0)

    # Ohne Kosten
    result_no_costs = calc.calculate_position_size(
        100, 95,
        product_type="cfd_long",
        leverage=5.0,
        spread_percent=0.0,
        overnight_percent=0.0
    )

    # Mit Kosten
    result_with_costs = calc.calculate_position_size(
        100, 95,
        product_type="cfd_long",
        leverage=5.0,
        spread_percent=0.5,
        overnight_percent=0.02,
        holding_days=10
    )

    units_no_costs = result_no_costs['position_details']['anzahl_einheiten']
    units_with_costs = result_with_costs['position_details']['anzahl_einheiten']

    print(f"\n✅ Vergleich: Ohne vs. Mit Kosten")
    print(f"   Einheiten OHNE Kosten: {units_no_costs}")
    print(f"   Einheiten MIT Kosten: {units_with_costs}")
    print(f"   Reduzierung: {((1 - units_with_costs/units_no_costs)*100):.1f}%")

    spread_cost = result_with_costs['cost_breakdown']['spread_kosten_total']
    overnight_cost = result_with_costs['cost_breakdown']['overnight_kosten_total']

    print(f"\n   Spread Kosten Total: €{spread_cost:.2f}")
    print(f"   Overnight Kosten Total: €{overnight_cost:.2f}")

    # Kosten sollten Positionsgröße reduzieren
    if units_with_costs < units_no_costs:
        print(f"   ✅ Kosten reduzieren Position wie erwartet")
        return True
    else:
        print(f"   ❌ FEHLER: Kosten sollten Position reduzieren")
        return False

def test_short_position_logic():
    """Teste Short-Position Logik"""
    print("\n"+"="*70)
    print("🧪 TEST: Short-Position Logik")
    print("="*70)

    depot = 50000
    calc = AdvancedPositionSizeCalculator(depot, risk_percentage=1.0)

    # Long Position
    long_result = calc.calculate_position_size(
        100, 95,
        product_type="cfd_long",
        leverage=5.0
    )

    # Short Position (Entry < Stop!)
    short_result = calc.calculate_position_size(
        100, 105,  # Bei Short: Entry niedriger als Stop
        product_type="cfd_short",
        leverage=5.0
    )

    print(f"\n✅ Long Position:")
    print(f"   Entry: €100, Stop: €95")
    print(f"   1R Target: €{long_result['risk_reward_targets']['1R_target']:.2f}")
    print(f"   Is Short: {long_result['product_info']['is_short']}")

    print(f"\n✅ Short Position:")
    print(f"   Entry: €100, Stop: €105")
    print(f"   1R Target: €{short_result['risk_reward_targets']['1R_target']:.2f}")
    print(f"   Is Short: {short_result['product_info']['is_short']}")

    # Validierungen
    checks = []

    # Long: 1R sollte über Entry liegen
    if long_result['risk_reward_targets']['1R_target'] > 100:
        checks.append("✅ Long 1R Target über Entry")
    else:
        checks.append("❌ Long 1R Target falsch")

    # Short: 1R sollte unter Entry liegen
    if short_result['risk_reward_targets']['1R_target'] < 100:
        checks.append("✅ Short 1R Target unter Entry")
    else:
        checks.append("❌ Short 1R Target falsch")

    # Short Flag korrekt gesetzt
    if not long_result['product_info']['is_short'] and short_result['product_info']['is_short']:
        checks.append("✅ Short Flags korrekt gesetzt")
    else:
        checks.append("❌ Short Flags falsch")

    print("\n📊 Validierungen:")
    for check in checks:
        print(f"   {check}")

    return all("✅" in c for c in checks)

def test_r_multiple_consistency():
    """Teste R-Multiple Konsistenz zwischen allen Tools"""
    print("\n"+"="*70)
    print("🧪 TEST: R-Multiple Konsistenz")
    print("="*70)

    depot = 50000
    entry = 120
    stop = 115
    risk_per_share = entry - stop  # 5

    # Basic Calculator
    basic_calc = PositionSizeCalculator(depot, risk_percentage=1.0)
    basic_result = basic_calc.calculate_position_size(entry, stop)

    # Advanced Calculator (Spot Mode)
    advanced_calc = AdvancedPositionSizeCalculator(depot, risk_percentage=1.0)
    advanced_result = advanced_calc.calculate_position_size(entry, stop, product_type="spot")

    print(f"\n✅ Test Setup: Entry €{entry}, Stop €{stop}, Risk/Share €{risk_per_share}")

    # Parse results
    basic_1r = float(basic_result['risk_reward_targets']['1R_target'].replace('€', ''))
    advanced_1r = advanced_result['risk_reward_targets']['1R_target']

    print(f"\n   Basic Calculator 1R: €{basic_1r:.2f}")
    print(f"   Advanced Calculator 1R: €{advanced_1r:.2f}")

    expected_1r = entry + risk_per_share  # 125

    print(f"   Erwarteter 1R: €{expected_1r:.2f}")

    # Beide sollten gleich sein
    if basic_1r == advanced_1r == expected_1r:
        print(f"\n   ✅ R-Multiple Berechnungen KONSISTENT")
        return True
    else:
        print(f"\n   ❌ R-Multiple Berechnungen INKONSISTENT")
        return False

# Main Test Runner
if __name__ == "__main__":
    print("\n" + "🎯"*35)
    print("🚀 LOGIK-VALIDIERUNGS-TESTS")
    print("🎯"*35 + "\n")

    results = []

    try:
        results.append(("Risiko-Genauigkeit", test_risk_calculation_accuracy()))
        results.append(("Hebel-Berechnungen", test_leverage_calculations()))
        results.append(("Kosten-Impact", test_cost_impact()))
        results.append(("Short-Position Logik", test_short_position_logic()))
        results.append(("R-Multiple Konsistenz", test_r_multiple_consistency()))

        print("\n" + "="*70)
        print("📊 TEST-ZUSAMMENFASSUNG")
        print("="*70)

        for test_name, result in results:
            status = "✅ BESTANDEN" if result else "❌ FEHLER"
            print(f"   {test_name}: {status}")

        all_passed = all(r[1] for r in results)

        print("\n" + "="*70)
        if all_passed:
            print("✅✅✅ ALLE LOGIK-TESTS BESTANDEN! ✅✅✅")
        else:
            print("❌ EINIGE TESTS FEHLGESCHLAGEN")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ KRITISCHER FEHLER: {e}")
        import traceback
        traceback.print_exc()
