#!/usr/bin/env python3
"""
Unified Position Size Calculator
Kombiniert Spot, CFD und Knockout Berechnung in einer Klasse
"""

from typing import Dict, Literal
from dataclasses import dataclass

ProductType = Literal["spot", "cfd_long", "cfd_short", "knockout_long", "knockout_short"]


@dataclass
class CalculationResult:
    """Ergebnis einer Position Size Berechnung"""

    # Depot Info
    portfolio_value: float
    max_risk: float
    risk_percent: float

    # Product Info
    product_type: str
    leverage: float
    is_short: bool

    # Trade Setup
    entry_price: float
    stop_loss: float
    basis_risk_per_unit: float
    total_risk_per_unit: float

    # Position Details
    units: int
    actual_investment: float
    notional_value: float
    portfolio_percentage: float

    # Risk/Reward Targets
    target_1r: float
    target_2r: float
    target_5r: float

    # Cost Breakdown
    basis_risk_total: float
    spread_cost_total: float
    overnight_cost_total: float
    total_cost: float


class UnifiedPositionCalculator:
    """
    Universaler Position Size Calculator

    Unterstützt:
    - Spot-Positionen (klassisch)
    - CFD Long/Short (mit Hebel, Spread, Overnight)
    - Knockout Long/Short (mit Hebel, Spread, kein Overnight)

    Basiert auf 1% Risiko-Regel (konfigurierbar)
    """

    def __init__(self, portfolio_value: float, risk_percentage: float = 1.0):
        """
        Initialize Calculator

        Args:
            portfolio_value: Gesamter Depot-Wert in EUR
            risk_percentage: Risiko pro Trade in Prozent (Standard: 1.0%)
        """
        if portfolio_value <= 0:
            raise ValueError("Portfolio value muss positiv sein")
        if risk_percentage <= 0 or risk_percentage > 100:
            raise ValueError("Risk percentage muss zwischen 0 und 100 liegen")

        self.portfolio_value = portfolio_value
        self.risk_percentage = risk_percentage / 100  # Convert to decimal
        self.max_risk = self.portfolio_value * self.risk_percentage

    def calculate_position(
        self,
        entry_price: float,
        stop_loss: float,
        product_type: ProductType = "spot",
        leverage: float = 1.0,
        spread_percent: float = 0.0,
        overnight_percent: float = 0.0,
        holding_days: int = 1
    ) -> CalculationResult:
        """
        Berechne Positionsgröße für alle Produkt-Typen

        Args:
            entry_price: Einstiegskurs
            stop_loss: Stop-Loss Kurs
            product_type: Art des Produkts
            leverage: Hebel (nur für CFD/Knockout)
            spread_percent: Spread in Prozent
            overnight_percent: Overnight-Kosten in Prozent (nur CFD)
            holding_days: Geplante Haltedauer in Tagen

        Returns:
            CalculationResult mit allen berechneten Werten

        Raises:
            ValueError: Bei ungültigen Inputs
        """
        # Validierung
        self._validate_inputs(entry_price, stop_loss, product_type, leverage)

        # Short-Position Erkennung
        is_short = product_type in ["cfd_short", "knockout_short"]

        # Basis-Risiko berechnen
        if is_short:
            if entry_price >= stop_loss:
                raise ValueError("Bei Short-Positionen muss Entry < Stop-Loss sein!")
            basis_risk = stop_loss - entry_price
        else:
            if entry_price <= stop_loss:
                raise ValueError("Bei Long-Positionen muss Entry > Stop-Loss sein!")
            basis_risk = entry_price - stop_loss

        # Hebel und Kosten berücksichtigen
        if product_type == "spot":
            # Spot: Kein Hebel, keine Kosten
            effective_risk = basis_risk
            spread_cost_per_unit = 0
            overnight_cost_per_unit = 0
            leverage_used = 1.0
        else:
            # Hebelprodukte
            leverage_used = leverage
            effective_risk = basis_risk * leverage
            spread_cost_per_unit = entry_price * (spread_percent / 100)

            # Overnight nur bei CFDs
            if product_type.startswith("cfd"):
                overnight_cost_per_unit = entry_price * (overnight_percent / 100) * holding_days
            else:
                overnight_cost_per_unit = 0

        # Gesamt-Risiko pro Einheit
        total_risk_per_unit = effective_risk + spread_cost_per_unit + overnight_cost_per_unit

        # Positionsgröße berechnen
        position_size = self.max_risk / total_risk_per_unit
        units = int(position_size)  # Auf ganze Einheiten abrunden

        # Investment vs. Exposure
        if product_type == "spot":
            actual_investment = units * entry_price
            notional_value = actual_investment
        else:
            # Bei Hebelprodukten
            actual_investment = units * entry_price
            notional_value = units * entry_price * leverage_used

        # R-Multiple Targets
        if is_short:
            target_1r = entry_price - basis_risk
            target_2r = entry_price - (2 * basis_risk)
            target_5r = entry_price - (5 * basis_risk)
        else:
            target_1r = entry_price + basis_risk
            target_2r = entry_price + (2 * basis_risk)
            target_5r = entry_price + (5 * basis_risk)

        # Cost Breakdown
        basis_risk_total = units * basis_risk
        spread_cost_total = units * spread_cost_per_unit
        overnight_cost_total = units * overnight_cost_per_unit
        total_cost = basis_risk_total + spread_cost_total + overnight_cost_total

        # Portfolio Percentage
        portfolio_percentage = (actual_investment / self.portfolio_value) * 100

        return CalculationResult(
            # Depot Info
            portfolio_value=self.portfolio_value,
            max_risk=self.max_risk,
            risk_percent=self.risk_percentage * 100,

            # Product Info
            product_type=product_type,
            leverage=leverage_used,
            is_short=is_short,

            # Trade Setup
            entry_price=entry_price,
            stop_loss=stop_loss,
            basis_risk_per_unit=basis_risk,
            total_risk_per_unit=total_risk_per_unit,

            # Position Details
            units=units,
            actual_investment=actual_investment,
            notional_value=notional_value,
            portfolio_percentage=portfolio_percentage,

            # Risk/Reward Targets
            target_1r=target_1r,
            target_2r=target_2r,
            target_5r=target_5r,

            # Cost Breakdown
            basis_risk_total=basis_risk_total,
            spread_cost_total=spread_cost_total,
            overnight_cost_total=overnight_cost_total,
            total_cost=total_cost
        )

    def update_portfolio(self, new_value: float):
        """
        Update Portfolio-Wert und berechne neues max Risiko

        Args:
            new_value: Neuer Portfolio-Wert in EUR
        """
        if new_value <= 0:
            raise ValueError("Portfolio value muss positiv sein")

        self.portfolio_value = new_value
        self.max_risk = self.portfolio_value * self.risk_percentage

    def _validate_inputs(
        self,
        entry_price: float,
        stop_loss: float,
        product_type: str,
        leverage: float
    ):
        """Validiere Input-Parameter"""

        if entry_price <= 0:
            raise ValueError("Entry price muss positiv sein")
        if stop_loss <= 0:
            raise ValueError("Stop loss muss positiv sein")
        if leverage < 1:
            raise ValueError("Leverage muss >= 1 sein")

        valid_products = ["spot", "cfd_long", "cfd_short", "knockout_long", "knockout_short"]
        if product_type not in valid_products:
            raise ValueError(f"Ungültiger product_type. Muss einer von {valid_products} sein")


# Beispiel-Verwendung
if __name__ == "__main__":
    print("="*70)
    print("🎯 UNIFIED POSITION CALCULATOR - Test Examples")
    print("="*70)

    # Setup
    portfolio = 50000
    calc = UnifiedPositionCalculator(portfolio, risk_percentage=1.0)

    # Test 1: Spot Position
    print("\n📈 Test 1: SPOT Position (NVIDIA)")
    print("-" * 70)
    result = calc.calculate_position(
        entry_price=120.0,
        stop_loss=115.0,
        product_type="spot"
    )
    print(f"Produkt: {result.product_type}")
    print(f"Einheiten: {result.units}")
    print(f"Investment: €{result.actual_investment:,.2f}")
    print(f"Max Risiko: €{result.max_risk:,.2f}")
    print(f"1R Target: €{result.target_1r:.2f}")
    print(f"Portfolio Anteil: {result.portfolio_percentage:.1f}%")

    # Test 2: CFD Long mit Hebel
    print("\n🔥 Test 2: CFD LONG mit Hebel 5x")
    print("-" * 70)
    result = calc.calculate_position(
        entry_price=120.0,
        stop_loss=115.0,
        product_type="cfd_long",
        leverage=5.0,
        spread_percent=0.2,
        overnight_percent=0.01,
        holding_days=10
    )
    print(f"Produkt: {result.product_type} (Hebel {result.leverage}x)")
    print(f"Einheiten: {result.units}")
    print(f"Investment: €{result.actual_investment:,.2f}")
    print(f"Exposure: €{result.notional_value:,.2f}")
    print(f"Spread Kosten: €{result.spread_cost_total:.2f}")
    print(f"Overnight Kosten: €{result.overnight_cost_total:.2f}")
    print(f"Total Kosten: €{result.total_cost:.2f}")
    print(f"1R Target: €{result.target_1r:.2f}")

    # Test 3: CFD Short
    print("\n🔻 Test 3: CFD SHORT Position")
    print("-" * 70)
    result = calc.calculate_position(
        entry_price=120.0,
        stop_loss=125.0,  # Bei Short: Stop > Entry
        product_type="cfd_short",
        leverage=5.0,
        spread_percent=0.2
    )
    print(f"Produkt: {result.product_type} (Short: {result.is_short})")
    print(f"Einheiten: {result.units}")
    print(f"Investment: €{result.actual_investment:,.2f}")
    print(f"1R Target: €{result.target_1r:.2f} (unter Entry = Gewinn)")

    # Test 4: Knockout Long
    print("\n🚀 Test 4: KNOCKOUT LONG (kein Overnight)")
    print("-" * 70)
    result = calc.calculate_position(
        entry_price=120.0,
        stop_loss=115.0,
        product_type="knockout_long",
        leverage=10.0,
        spread_percent=1.0
    )
    print(f"Produkt: {result.product_type} (Hebel {result.leverage}x)")
    print(f"Einheiten: {result.units}")
    print(f"Investment: €{result.actual_investment:,.2f}")
    print(f"Exposure: €{result.notional_value:,.2f}")
    print(f"Overnight Kosten: €{result.overnight_cost_total:.2f} (sollte 0 sein)")

    print("\n" + "="*70)
    print("✅ Alle Test-Beispiele abgeschlossen!")
    print("="*70)
