#!/usr/bin/env python3
"""
Partial Sale Manager
Verwaltet Teilverkäufe von Positionen
"""

from typing import Dict, Optional
from datetime import datetime


class PartialSaleManager:
    """
    Verwaltet Teilverkäufe

    Features:
    - Teilverkauf-Berechnung (25%, 50%, 75%, 100%)
    - R-Multiple pro Teilverkauf
    - Stop-Loss Empfehlungen
    - Historie-Tracking
    """

    @staticmethod
    def calculate_partial_sale(
        trade: Dict,
        sell_percentage: float,
        current_price: float
    ) -> Dict:
        """
        Berechnet Teilverkauf

        Args:
            trade: Trade Dictionary (aus TradeManager)
            sell_percentage: Prozent zu verkaufen (z.B. 25.0 für 25%)
            current_price: Aktueller Verkaufspreis

        Returns:
            Dictionary mit Teilverkauf-Details:
            - units_sold: Verkaufte Einheiten
            - units_remaining: Verbleibende Einheiten
            - sale_proceeds: Verkaufserlös
            - pnl: Gewinn/Verlust dieses Verkaufs
            - r_multiple: R-Multiple dieses Verkaufs
            - sale_price: Verkaufspreis
            - percentage: Prozent verkauft
            - should_move_stop: Empfehlung Stop zu bewegen
            - recommended_stop: Empfohlener neuer Stop
        """
        # Aktuelle Position
        current_units = trade['units']
        entry_price = trade['entry_price']
        original_stop = trade['stop_loss']
        is_short = trade['product_type'] in ['cfd_short', 'knockout_short']

        # Einheiten berechnen
        units_to_sell = int(current_units * (sell_percentage / 100))
        units_remaining = current_units - units_to_sell

        # Erlös und P&L
        sale_proceeds = units_to_sell * current_price

        if is_short:
            pnl = units_to_sell * (entry_price - current_price)
        else:
            pnl = units_to_sell * (current_price - entry_price)

        # R-Multiple berechnen
        if is_short:
            risk_per_unit = original_stop - entry_price
            profit_per_unit = entry_price - current_price
        else:
            risk_per_unit = entry_price - original_stop
            profit_per_unit = current_price - entry_price

        r_multiple = profit_per_unit / risk_per_unit if risk_per_unit > 0 else 0

        # Stop-Loss Empfehlung
        should_move_stop = False
        recommended_stop = trade['current_stop']

        # Bei Gewinn (R > 0): Stop auf Break-even empfehlen
        if r_multiple > 0 and trade['current_stop'] != entry_price:
            should_move_stop = True
            recommended_stop = entry_price

        return {
            'units_sold': units_to_sell,
            'units_remaining': units_remaining,
            'sale_proceeds': sale_proceeds,
            'pnl': pnl,
            'r_multiple': r_multiple,
            'sale_price': current_price,
            'percentage': sell_percentage,
            'should_move_stop': should_move_stop,
            'recommended_stop': recommended_stop,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def execute_partial_sale(
        trade_manager,
        trade_id: str,
        sell_percentage: float,
        current_price: float,
        auto_update_stop: bool = True
    ) -> Optional[Dict]:
        """
        Führt Teilverkauf aus und updated Trade

        Args:
            trade_manager: TradeManager Instanz
            trade_id: Trade ID
            sell_percentage: Prozent zu verkaufen
            current_price: Verkaufspreis
            auto_update_stop: Automatisch Stop updaten bei Gewinn

        Returns:
            Teilverkauf-Details oder None bei Fehler
        """
        trade = trade_manager.get_trade(trade_id)
        if not trade:
            return None

        # Berechne Teilverkauf
        sale_details = PartialSaleManager.calculate_partial_sale(
            trade.to_dict(),
            sell_percentage,
            current_price
        )

        # Update Trade
        new_units = sale_details['units_remaining']
        new_realized_pnl = trade.total_realized_pnl + sale_details['pnl']

        # Teilverkauf zur Historie hinzufügen
        partial_sales = list(trade.partial_sales)  # Copy
        partial_sales.append({
            'date': sale_details['timestamp'],
            'units_sold': sale_details['units_sold'],
            'price': sale_details['sale_price'],
            'proceeds': sale_details['sale_proceeds'],
            'pnl': sale_details['pnl'],
            'r_multiple': sale_details['r_multiple'],
            'percentage': sale_details['percentage']
        })

        # Update Dictionary
        updates = {
            'units': new_units
        }

        # Update via trade_manager (nicht direkt auf trade object)
        # Wir müssen partial_sales und total_realized_pnl direkt setzen
        trade.units = new_units
        trade.total_realized_pnl = new_realized_pnl
        trade.partial_sales = partial_sales

        # Auto Stop-Update
        if auto_update_stop and sale_details['should_move_stop']:
            trade.current_stop = sale_details['recommended_stop']

        # Wenn alles verkauft: Trade schließen
        if new_units == 0:
            trade_manager.update_trade(trade_id, {
                'status': 'closed',
                'close_price': current_price,
                'close_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'final_pnl': new_realized_pnl,
                'final_r_multiple': sale_details['r_multiple']
            })

        return sale_details

    @staticmethod
    def analyze_partial_sales(trades_list) -> Dict:
        """
        Analysiert Teilverkäufe über alle Trades

        Args:
            trades_list: Liste von Trade-Objekten

        Returns:
            Dictionary mit Analytics:
            - total_partial_sales: Anzahl Teilverkäufe
            - total_proceeds: Gesamt-Erlös
            - total_pnl: Gesamt P&L aus Teilverkäufen
            - avg_r_multiple: Durchschnittliches R-Multiple
            - r_distribution: Verteilung der R-Multiples
            - by_percentage: Grouped by Verkaufs-Prozent
        """
        all_sales = []

        # Sammle alle Teilverkäufe
        for trade in trades_list:
            for sale in trade.partial_sales:
                sale_copy = sale.copy()
                sale_copy['symbol'] = trade.symbol
                sale_copy['product_type'] = trade.product_type
                all_sales.append(sale_copy)

        if not all_sales:
            return {
                'total_partial_sales': 0,
                'total_proceeds': 0,
                'total_pnl': 0,
                'avg_r_multiple': 0,
                'r_distribution': {},
                'by_percentage': {}
            }

        # Berechnungen
        total_proceeds = sum(s['proceeds'] for s in all_sales)
        total_pnl = sum(s['pnl'] for s in all_sales)
        avg_r = sum(s['r_multiple'] for s in all_sales) / len(all_sales)

        # R-Distribution (gruppiert in Bereiche)
        r_distribution = {
            '< 0R (Verlust)': 0,
            '0R - 1R': 0,
            '1R - 2R': 0,
            '2R - 5R': 0,
            '> 5R': 0
        }

        for sale in all_sales:
            r = sale['r_multiple']
            if r < 0:
                r_distribution['< 0R (Verlust)'] += 1
            elif r < 1:
                r_distribution['0R - 1R'] += 1
            elif r < 2:
                r_distribution['1R - 2R'] += 1
            elif r < 5:
                r_distribution['2R - 5R'] += 1
            else:
                r_distribution['> 5R'] += 1

        # By Percentage (gruppiert nach Verkaufs-Prozent)
        by_percentage = {}
        for sale in all_sales:
            pct = int(sale['percentage'])
            if pct not in by_percentage:
                by_percentage[pct] = {
                    'count': 0,
                    'total_pnl': 0,
                    'avg_r': 0
                }
            by_percentage[pct]['count'] += 1
            by_percentage[pct]['total_pnl'] += sale['pnl']

        # Avg R pro Percentage
        for pct in by_percentage:
            matching_sales = [s for s in all_sales if int(s['percentage']) == pct]
            by_percentage[pct]['avg_r'] = sum(s['r_multiple'] for s in matching_sales) / len(matching_sales)

        return {
            'total_partial_sales': len(all_sales),
            'total_proceeds': total_proceeds,
            'total_pnl': total_pnl,
            'avg_r_multiple': avg_r,
            'r_distribution': r_distribution,
            'by_percentage': by_percentage,
            'all_sales': all_sales  # Für Detail-Anzeige
        }


# Beispiel-Verwendung
if __name__ == "__main__":
    print("="*70)
    print("💰 PARTIAL SALE MANAGER - Test Examples")
    print("="*70)

    # Mock Trade
    mock_trade = {
        'id': 'test-123',
        'symbol': 'NVIDIA',
        'product_type': 'spot',
        'entry_price': 120.0,
        'stop_loss': 115.0,
        'current_stop': 115.0,
        'units': 100,
        'original_units': 100,
        'investment': 12000.0,
        'risk_amount': 500.0,
        'total_realized_pnl': 0.0,
        'partial_sales': []
    }

    # Test 1: 25% Teilverkauf
    print("\n✅ Test 1: 25% Teilverkauf bei 1R Target")
    print("-" * 70)

    sale_details = PartialSaleManager.calculate_partial_sale(
        mock_trade,
        sell_percentage=25.0,
        current_price=125.0  # 1R Target erreicht
    )

    print(f"Verkaufte Einheiten: {sale_details['units_sold']}")
    print(f"Verbleibende Einheiten: {sale_details['units_remaining']}")
    print(f"Erlös: €{sale_details['sale_proceeds']:,.2f}")
    print(f"P&L: €{sale_details['pnl']:,.2f}")
    print(f"R-Multiple: {sale_details['r_multiple']:.2f}R")
    print(f"Stop empfehlen: {sale_details['should_move_stop']}")
    if sale_details['should_move_stop']:
        print(f"Empfohlener Stop: €{sale_details['recommended_stop']:.2f}")

    # Test 2: 50% Teilverkauf
    print("\n✅ Test 2: 50% Teilverkauf bei 2R Target")
    print("-" * 70)

    # Update mock trade (als ob 25% bereits verkauft)
    mock_trade['units'] = 75
    mock_trade['current_stop'] = 120.0  # Break-even

    sale_details = PartialSaleManager.calculate_partial_sale(
        mock_trade,
        sell_percentage=50.0,  # 50% von verbleibenden 75
        current_price=130.0  # 2R Target
    )

    print(f"Verkaufte Einheiten: {sale_details['units_sold']}")
    print(f"Verbleibende Einheiten: {sale_details['units_remaining']}")
    print(f"P&L: €{sale_details['pnl']:,.2f}")
    print(f"R-Multiple: {sale_details['r_multiple']:.2f}R")

    # Test 3: Analytics (Mock)
    print("\n✅ Test 3: Teilverkauf Analytics")
    print("-" * 70)

    # Mock Trade-Objekt mit Teilverkäufen
    class MockTrade:
        def __init__(self):
            self.symbol = "NVIDIA"
            self.product_type = "spot"
            self.partial_sales = [
                {'date': '2025-11-15', 'units_sold': 25, 'price': 125.0, 'proceeds': 3125.0, 'pnl': 125.0, 'r_multiple': 1.0, 'percentage': 25},
                {'date': '2025-11-16', 'units_sold': 37, 'price': 130.0, 'proceeds': 4810.0, 'pnl': 370.0, 'r_multiple': 2.0, 'percentage': 50},
            ]

    mock_trades = [MockTrade()]

    analytics = PartialSaleManager.analyze_partial_sales(mock_trades)

    print(f"Total Teilverkäufe: {analytics['total_partial_sales']}")
    print(f"Total Erlös: €{analytics['total_proceeds']:,.2f}")
    print(f"Total P&L: €{analytics['total_pnl']:,.2f}")
    print(f"Avg R-Multiple: {analytics['avg_r_multiple']:.2f}R")
    print(f"\nR-Distribution:")
    for range_name, count in analytics['r_distribution'].items():
        print(f"  {range_name}: {count}")
    print(f"\nBy Percentage:")
    for pct, data in analytics['by_percentage'].items():
        print(f"  {pct}%: {data['count']} Verkäufe, Avg R: {data['avg_r']:.2f}R, Total P&L: €{data['total_pnl']:.2f}")

    print("\n" + "="*70)
    print("✅ Alle Test-Beispiele abgeschlossen!")
    print("="*70)
