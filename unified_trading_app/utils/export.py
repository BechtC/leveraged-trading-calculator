#!/usr/bin/env python3
"""
Export & Import Utilities
Für Backup/Restore und Daten-Export
"""

import json
import csv
from datetime import datetime
from typing import List
from io import StringIO


class DataExporter:
    """
    Export-Manager für Trades und Analytics

    Features:
    - CSV Export (Trade-History)
    - JSON Export (vollständiger Backup)
    - Backup Session State
    - Restore from Backup
    """

    @staticmethod
    def export_trades_to_csv(trades_list) -> str:
        """
        Exportiert Trades als CSV

        Args:
            trades_list: Liste von Trade-Objekten

        Returns:
            CSV String
        """
        if not trades_list:
            return ""

        output = StringIO()
        fieldnames = [
            'symbol', 'status', 'product_type', 'created_at',
            'entry_price', 'stop_loss', 'current_stop',
            'units', 'original_units', 'investment', 'exposure',
            'leverage', 'risk_amount',
            'target_1r', 'target_2r', 'target_5r',
            'close_price', 'close_date',
            'final_pnl', 'final_r_multiple',
            'total_realized_pnl', 'partial_sales_count'
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for trade in trades_list:
            writer.writerow({
                'symbol': trade.symbol,
                'status': trade.status,
                'product_type': trade.product_type,
                'created_at': trade.created_at,
                'entry_price': trade.entry_price,
                'stop_loss': trade.stop_loss,
                'current_stop': trade.current_stop,
                'units': trade.units,
                'original_units': trade.original_units,
                'investment': trade.investment,
                'exposure': trade.exposure,
                'leverage': trade.leverage,
                'risk_amount': trade.risk_amount,
                'target_1r': trade.target_1r,
                'target_2r': trade.target_2r,
                'target_5r': trade.target_5r,
                'close_price': trade.close_price or '',
                'close_date': trade.close_date or '',
                'final_pnl': trade.final_pnl or '',
                'final_r_multiple': trade.final_r_multiple or '',
                'total_realized_pnl': trade.total_realized_pnl,
                'partial_sales_count': len(trade.partial_sales)
            })

        return output.getvalue()

    @staticmethod
    def export_trades_to_json(trade_manager) -> str:
        """
        Exportiert vollständigen Backup als JSON

        Args:
            trade_manager: TradeManager Instanz

        Returns:
            JSON String
        """
        backup_data = {
            'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'version': '1.0',
            'trades': trade_manager.export_to_dict()
        }

        return json.dumps(backup_data, indent=2, ensure_ascii=False)

    @staticmethod
    def import_trades_from_json(trade_manager, json_string: str) -> bool:
        """
        Importiert Trades aus JSON Backup

        Args:
            trade_manager: TradeManager Instanz
            json_string: JSON String

        Returns:
            True wenn erfolgreich
        """
        try:
            backup_data = json.loads(json_string)

            if 'trades' not in backup_data:
                return False

            trade_manager.import_from_dict(backup_data['trades'])
            return True

        except (json.JSONDecodeError, KeyError):
            return False

    @staticmethod
    def export_partial_sales_to_csv(analytics_data) -> str:
        """
        Exportiert Teilverkäufe als CSV

        Args:
            analytics_data: Dictionary von analyze_partial_sales()

        Returns:
            CSV String
        """
        if not analytics_data.get('all_sales'):
            return ""

        output = StringIO()
        fieldnames = ['date', 'symbol', 'product_type', 'percentage',
                     'units_sold', 'price', 'proceeds', 'pnl', 'r_multiple']

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for sale in analytics_data['all_sales']:
            writer.writerow(sale)

        return output.getvalue()

    @staticmethod
    def export_performance_to_csv(closed_trades) -> str:
        """
        Exportiert Performance-Daten als CSV

        Args:
            closed_trades: Liste geschlossener Trades

        Returns:
            CSV String
        """
        if not closed_trades:
            return ""

        output = StringIO()
        fieldnames = [
            'symbol', 'product_type', 'entry_price', 'close_price',
            'units', 'investment', 'final_pnl', 'final_r_multiple',
            'created_at', 'close_date', 'holding_days'
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for trade in closed_trades:
            # Berechne Holding Days
            if trade.close_date:
                try:
                    created = datetime.strptime(trade.created_at, "%Y-%m-%d %H:%M:%S")
                    closed = datetime.strptime(trade.close_date, "%Y-%m-%d %H:%M:%S")
                    holding_days = (closed - created).days
                except:
                    holding_days = 0
            else:
                holding_days = 0

            writer.writerow({
                'symbol': trade.symbol,
                'product_type': trade.product_type,
                'entry_price': trade.entry_price,
                'close_price': trade.close_price or '',
                'units': trade.units,
                'investment': trade.investment,
                'final_pnl': trade.final_pnl or '',
                'final_r_multiple': trade.final_r_multiple or '',
                'created_at': trade.created_at,
                'close_date': trade.close_date or '',
                'holding_days': holding_days
            })

        return output.getvalue()


# Beispiel-Verwendung
if __name__ == "__main__":
    print("="*70)
    print("📤 DATA EXPORTER - Test Examples")
    print("="*70)

    from trade_manager import TradeManager

    # Setup Mock Data
    manager = TradeManager()

    # Erstelle Test-Trades
    trade_id1 = manager.create_trade(
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
        status="closed"
    )
    manager.close_trade(trade_id1, close_price=130.0)

    trade_id2 = manager.create_trade(
        symbol="AAPL",
        product_type="cfd_long",
        entry_price=180.0,
        stop_loss=175.0,
        units=50,
        investment=9000.0,
        exposure=45000.0,
        risk_amount=250.0,
        target_1r=185.0,
        target_2r=190.0,
        target_5r=205.0,
        leverage=5.0,
        status="open"
    )

    # Test 1: CSV Export
    print("\n✅ Test 1: CSV Export")
    print("-" * 70)
    csv_data = DataExporter.export_trades_to_csv(manager.get_all_trades())
    print("CSV Preview (erste 5 Zeilen):")
    for line in csv_data.split('\n')[:5]:
        print(f"  {line}")

    # Test 2: JSON Export
    print("\n✅ Test 2: JSON Export (Backup)")
    print("-" * 70)
    json_data = DataExporter.export_trades_to_json(manager)
    print("JSON Preview (erste 500 chars):")
    print(json_data[:500] + "...")

    # Test 3: JSON Import
    print("\n✅ Test 3: JSON Import (Restore)")
    print("-" * 70)
    new_manager = TradeManager()
    success = DataExporter.import_trades_from_json(new_manager, json_data)
    print(f"Import erfolgreich: {success}")
    print(f"Trades nach Import: {len(new_manager.get_all_trades())}")

    # Test 4: Performance CSV
    print("\n✅ Test 4: Performance CSV Export")
    print("-" * 70)
    closed_trades = [t for t in manager.get_all_trades() if t.status == "closed"]
    perf_csv = DataExporter.export_performance_to_csv(closed_trades)
    print("Performance CSV Preview:")
    for line in perf_csv.split('\n')[:3]:
        print(f"  {line}")

    print("\n" + "="*70)
    print("✅ Alle Test-Beispiele abgeschlossen!")
    print("="*70)
