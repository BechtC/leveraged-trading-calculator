#!/usr/bin/env python3
"""
Trade Manager
Verwaltet Trade-Lifecycle und Positionen
"""

from typing import Dict, List, Optional, Literal
from datetime import datetime
import uuid
from dataclasses import dataclass, asdict

TradeStatus = Literal["planned", "open", "closed"]


@dataclass
class Trade:
    """Trade Daten-Struktur"""

    # Identification
    id: str
    symbol: str
    created_at: str
    status: TradeStatus

    # Position Details
    product_type: str
    entry_price: float
    stop_loss: float
    current_stop: float

    # Hebel-Specific (optional)
    leverage: float
    spread_percent: float
    overnight_percent: float
    holding_days: int

    # Position Size
    units: int
    original_units: int
    investment: float
    exposure: float  # Bei Hebel unterschiedlich

    # Risk/Reward
    risk_amount: float
    target_1r: float
    target_2r: float
    target_5r: float

    # Partial Sales
    partial_sales: List[Dict]
    total_realized_pnl: float

    # Final Close (wenn geschlossen)
    close_price: Optional[float] = None
    close_date: Optional[str] = None
    final_pnl: Optional[float] = None
    final_r_multiple: Optional[float] = None

    def to_dict(self) -> dict:
        """Konvertiere zu Dictionary"""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'Trade':
        """Erstelle Trade aus Dictionary"""
        return Trade(**data)


class TradeManager:
    """
    Verwaltet Trade-Lifecycle

    Features:
    - CRUD Operationen
    - Status-Tracking (planned/open/closed)
    - Filterung und Suche
    - Portfolio-Integration
    """

    def __init__(self):
        """Initialize TradeManager"""
        self.trades: Dict[str, Trade] = {}

    def create_trade(
        self,
        symbol: str,
        product_type: str,
        entry_price: float,
        stop_loss: float,
        units: int,
        investment: float,
        exposure: float,
        risk_amount: float,
        target_1r: float,
        target_2r: float,
        target_5r: float,
        leverage: float = 1.0,
        spread_percent: float = 0.0,
        overnight_percent: float = 0.0,
        holding_days: int = 1,
        status: TradeStatus = "planned"
    ) -> str:
        """
        Erstellt neuen Trade

        Args:
            symbol: Aktien-Symbol
            product_type: Art des Produkts
            entry_price: Einstiegskurs
            stop_loss: Stop-Loss Kurs
            units: Anzahl Einheiten
            investment: Tatsächliches Investment
            exposure: Exposure (bei Hebel unterschiedlich)
            risk_amount: Max Risiko
            target_1r/2r/5r: R-Multiple Targets
            leverage: Hebel (Standard: 1.0)
            spread_percent: Spread in %
            overnight_percent: Overnight in %
            holding_days: Halte-Dauer
            status: Trade Status (Standard: "planned")

        Returns:
            Trade ID (UUID)
        """
        trade_id = str(uuid.uuid4())
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        trade = Trade(
            id=trade_id,
            symbol=symbol,
            created_at=now,
            status=status,
            product_type=product_type,
            entry_price=entry_price,
            stop_loss=stop_loss,
            current_stop=stop_loss,  # Initial gleich Stop
            leverage=leverage,
            spread_percent=spread_percent,
            overnight_percent=overnight_percent,
            holding_days=holding_days,
            units=units,
            original_units=units,
            investment=investment,
            exposure=exposure,
            risk_amount=risk_amount,
            target_1r=target_1r,
            target_2r=target_2r,
            target_5r=target_5r,
            partial_sales=[],
            total_realized_pnl=0.0
        )

        self.trades[trade_id] = trade
        return trade_id

    def get_trade(self, trade_id: str) -> Optional[Trade]:
        """
        Holt Trade nach ID

        Args:
            trade_id: Trade ID

        Returns:
            Trade object oder None
        """
        return self.trades.get(trade_id)

    def update_trade(self, trade_id: str, updates: dict) -> bool:
        """
        Updated Trade-Felder

        Args:
            trade_id: Trade ID
            updates: Dictionary mit zu updatenden Feldern

        Returns:
            True wenn erfolgreich, False wenn Trade nicht gefunden
        """
        trade = self.get_trade(trade_id)
        if not trade:
            return False

        # Update erlaubte Felder
        allowed_fields = [
            'current_stop', 'units', 'status', 'close_price',
            'close_date', 'final_pnl', 'final_r_multiple'
        ]

        for key, value in updates.items():
            if key in allowed_fields and hasattr(trade, key):
                setattr(trade, key, value)

        return True

    def close_trade(
        self,
        trade_id: str,
        close_price: float,
        calculate_pnl: bool = True
    ) -> bool:
        """
        Schließt Trade komplett

        Args:
            trade_id: Trade ID
            close_price: Schlusskurs
            calculate_pnl: P&L automatisch berechnen

        Returns:
            True wenn erfolgreich
        """
        trade = self.get_trade(trade_id)
        if not trade:
            return False

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # P&L berechnen
        if calculate_pnl:
            # Berücksichtige bereits realisierte Teilverkäufe
            remaining_units = trade.units
            remaining_pnl = remaining_units * (close_price - trade.entry_price)
            final_pnl = trade.total_realized_pnl + remaining_pnl

            # R-Multiple berechnen
            final_r_multiple = final_pnl / trade.risk_amount if trade.risk_amount > 0 else 0

            self.update_trade(trade_id, {
                'status': 'closed',
                'close_price': close_price,
                'close_date': now,
                'final_pnl': final_pnl,
                'final_r_multiple': final_r_multiple,
                'units': 0  # Alles verkauft
            })
        else:
            self.update_trade(trade_id, {
                'status': 'closed',
                'close_price': close_price,
                'close_date': now,
                'units': 0
            })

        return True

    def get_trades_by_status(self, status: TradeStatus) -> List[Trade]:
        """
        Filtert Trades nach Status

        Args:
            status: Trade Status

        Returns:
            Liste von Trades
        """
        return [t for t in self.trades.values() if t.status == status]

    def get_open_trades(self) -> List[Trade]:
        """Gibt alle offenen Trades zurück"""
        return self.get_trades_by_status("open")

    def get_planned_trades(self) -> List[Trade]:
        """Gibt alle geplanten Trades zurück"""
        return self.get_trades_by_status("planned")

    def get_closed_trades(self) -> List[Trade]:
        """Gibt alle geschlossenen Trades zurück"""
        return self.get_trades_by_status("closed")

    def get_trades_by_product_type(self, product_type: str) -> List[Trade]:
        """
        Filtert Trades nach Produkt-Typ

        Args:
            product_type: Produkt-Typ

        Returns:
            Liste von Trades
        """
        return [t for t in self.trades.values() if t.product_type == product_type]

    def get_all_trades(self) -> List[Trade]:
        """Gibt alle Trades zurück"""
        return list(self.trades.values())

    def delete_trade(self, trade_id: str) -> bool:
        """
        Löscht Trade

        Args:
            trade_id: Trade ID

        Returns:
            True wenn erfolgreich
        """
        if trade_id in self.trades:
            del self.trades[trade_id]
            return True
        return False

    def calculate_portfolio_metrics(self) -> dict:
        """
        Berechnet Portfolio-Metriken

        Returns:
            Dictionary mit Metriken
        """
        open_trades = self.get_open_trades()
        closed_trades = self.get_closed_trades()

        # Total Investment in offenen Positionen
        total_investment = sum(t.investment for t in open_trades)

        # Total Exposure (wichtig bei Hebelprodukten)
        total_exposure = sum(t.exposure for t in open_trades)

        # Total Risk
        total_risk = sum(t.risk_amount for t in open_trades)

        # Realized P&L (geschlossene Trades)
        total_pnl = sum(t.final_pnl or 0 for t in closed_trades)

        # Win Rate
        winning_trades = [t for t in closed_trades if (t.final_pnl or 0) > 0]
        win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0

        # Average R-Multiple
        r_multiples = [t.final_r_multiple for t in closed_trades if t.final_r_multiple is not None]
        avg_r_multiple = sum(r_multiples) / len(r_multiples) if r_multiples else 0

        return {
            'total_trades': len(self.trades),
            'open_trades': len(open_trades),
            'closed_trades': len(closed_trades),
            'planned_trades': len(self.get_planned_trades()),
            'total_investment': total_investment,
            'total_exposure': total_exposure,
            'total_risk': total_risk,
            'realized_pnl': total_pnl,
            'win_rate': win_rate,
            'avg_r_multiple': avg_r_multiple
        }

    def export_to_dict(self) -> dict:
        """
        Exportiert alle Trades als Dictionary

        Returns:
            Dictionary mit allen Trades
        """
        return {
            trade_id: trade.to_dict()
            for trade_id, trade in self.trades.items()
        }

    def import_from_dict(self, data: dict):
        """
        Importiert Trades aus Dictionary

        Args:
            data: Dictionary mit Trades
        """
        self.trades = {
            trade_id: Trade.from_dict(trade_data)
            for trade_id, trade_data in data.items()
        }


# Beispiel-Verwendung
if __name__ == "__main__":
    print("="*70)
    print("📊 TRADE MANAGER - Test Examples")
    print("="*70)

    # Setup
    manager = TradeManager()

    # Test 1: Erstelle Trade
    print("\n✅ Test 1: Trade erstellen")
    print("-" * 70)
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
    print(f"Trade erstellt: {trade_id}")

    # Test 2: Trade holen
    print("\n✅ Test 2: Trade abrufen")
    print("-" * 70)
    trade = manager.get_trade(trade_id)
    print(f"Symbol: {trade.symbol}")
    print(f"Status: {trade.status}")
    print(f"Units: {trade.units}")
    print(f"Investment: €{trade.investment:,.2f}")

    # Test 3: Trade updaten (auf open setzen)
    print("\n✅ Test 3: Trade auf 'open' setzen")
    print("-" * 70)
    manager.update_trade(trade_id, {'status': 'open'})
    trade = manager.get_trade(trade_id)
    print(f"Neuer Status: {trade.status}")

    # Test 4: Trade schließen
    print("\n✅ Test 4: Trade schließen")
    print("-" * 70)
    manager.close_trade(trade_id, close_price=130.0)
    trade = manager.get_trade(trade_id)
    print(f"Status: {trade.status}")
    print(f"Close Price: €{trade.close_price:.2f}")
    print(f"Final P&L: €{trade.final_pnl:,.2f}")
    print(f"R-Multiple: {trade.final_r_multiple:.2f}R")

    # Test 5: Portfolio Metriken
    print("\n✅ Test 5: Portfolio Metriken")
    print("-" * 70)

    # Erstelle noch einen offenen Trade
    trade_id2 = manager.create_trade(
        symbol="AAPL",
        product_type="cfd_long",
        entry_price=180.0,
        stop_loss=175.0,
        units=50,
        investment=9000.0,
        exposure=45000.0,  # Hebel 5x
        risk_amount=500.0,
        target_1r=185.0,
        target_2r=190.0,
        target_5r=205.0,
        leverage=5.0,
        status="open"
    )

    metrics = manager.calculate_portfolio_metrics()
    print(f"Total Trades: {metrics['total_trades']}")
    print(f"Open Trades: {metrics['open_trades']}")
    print(f"Closed Trades: {metrics['closed_trades']}")
    print(f"Total Investment: €{metrics['total_investment']:,.2f}")
    print(f"Total Exposure: €{metrics['total_exposure']:,.2f}")
    print(f"Total Risk: €{metrics['total_risk']:,.2f}")
    print(f"Realized P&L: €{metrics['realized_pnl']:,.2f}")
    print(f"Win Rate: {metrics['win_rate']:.1f}%")
    print(f"Avg R-Multiple: {metrics['avg_r_multiple']:.2f}R")

    print("\n" + "="*70)
    print("✅ Alle Test-Beispiele abgeschlossen!")
    print("="*70)
