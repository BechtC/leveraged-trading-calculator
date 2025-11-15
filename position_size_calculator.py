#!/usr/bin/env python3
"""
1% Risiko-Regel Position Size Calculator
Für Tiedjes CROC Trading System
"""

class PositionSizeCalculator:
    def __init__(self, total_portfolio_value: float, risk_percentage: float = 1.0):
        """
        Initialize the calculator
        
        Args:
            total_portfolio_value: Gesamtes Depot + Cash in EUR
            risk_percentage: Risiko in Prozent (Standard: 1.0%)
        """
        self.total_portfolio = total_portfolio_value
        self.risk_percentage = risk_percentage / 100  # Convert to decimal
        self.max_risk_amount = self.total_portfolio * self.risk_percentage
        
    def calculate_position_size(self, entry_price: float, stop_loss: float) -> dict:
        """
        Berechne Positionsgröße basierend auf 1% Risiko-Regel
        
        Args:
            entry_price: Einstiegskurs (Stopp-Buy)
            stop_loss: Stop-Loss Kurs
            
        Returns:
            Dictionary mit allen relevanten Berechnungen
        """
        if entry_price <= stop_loss:
            raise ValueError("Entry Price muss höher als Stop-Loss sein!")
        
        risk_per_share = entry_price - stop_loss
        position_size = self.max_risk_amount / risk_per_share
        position_value = position_size * entry_price
        
        # Berechne weitere wichtige Kennzahlen
        risk_reward_needed = risk_per_share  # Minimum für 1:1 R/R
        target_1r = entry_price + risk_reward_needed
        target_2r = entry_price + (2 * risk_reward_needed)
        target_5r = entry_price + (5 * risk_reward_needed)
        
        return {
            'depot_info': {
                'gesamtdepot': f"€{self.total_portfolio:,.2f}",
                'max_risiko': f"€{self.max_risk_amount:,.2f}",
                'risiko_prozent': f"{self.risk_percentage*100:.1f}%"
            },
            'trade_setup': {
                'entry_preis': f"€{entry_price:.2f}",
                'stop_loss': f"€{stop_loss:.2f}",
                'risiko_pro_aktie': f"€{risk_per_share:.2f}"
            },
            'position_details': {
                'anzahl_aktien': f"{position_size:.0f}",
                'position_wert': f"€{position_value:,.2f}",
                'depot_anteil': f"{(position_value/self.total_portfolio)*100:.1f}%"
            },
            'risk_reward_targets': {
                '1R_target': f"€{target_1r:.2f}",
                '2R_target': f"€{target_2r:.2f}",
                '5R_target': f"€{target_5r:.2f}"
            },
            'validation': {
                'max_verlust': f"€{position_size * risk_per_share:,.2f}",
                'verlust_check': self.max_risk_amount >= (position_size * risk_per_share)
            }
        }
    
    def update_portfolio(self, new_value: float):
        """Update Portfolio-Wert und berechne neues Risiko neu"""
        self.total_portfolio = new_value
        self.max_risk_amount = self.total_portfolio * self.risk_percentage
        
    def batch_calculate(self, trades: list) -> list:
        """
        Berechne mehrere Trades gleichzeitig
        
        Args:
            trades: Liste von Dictionaries mit 'symbol', 'entry', 'stop_loss'
        """
        results = []
        for trade in trades:
            try:
                calc = self.calculate_position_size(trade['entry'], trade['stop_loss'])
                calc['symbol'] = trade.get('symbol', 'Unknown')
                results.append(calc)
            except ValueError as e:
                results.append({
                    'symbol': trade.get('symbol', 'Unknown'),
                    'error': str(e)
                })
        return results

def print_trade_analysis(result: dict):
    """Schöne Ausgabe der Trade-Analyse"""
    if 'error' in result:
        print(f"❌ Fehler bei {result['symbol']}: {result['error']}")
        return
    
    print("=" * 60)
    print(f"📊 TRADE ANALYSE - {result.get('symbol', 'Aktie')}")
    print("=" * 60)
    
    print("\n💰 DEPOT INFORMATION:")
    for key, value in result['depot_info'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n🎯 TRADE SETUP:")
    for key, value in result['trade_setup'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n📈 POSITIONS-DETAILS:")
    for key, value in result['position_details'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n🚀 RISK/REWARD TARGETS:")
    for key, value in result['risk_reward_targets'].items():
        print(f"  {key}: {value}")
    
    print("\n✅ VALIDIERUNG:")
    for key, value in result['validation'].items():
        if key == 'verlust_check':
            status = "✅ OK" if value else "❌ FEHLER"
            print(f"  Risiko-Check: {status}")
        else:
            print(f"  {key.replace('_', ' ').title()}: {value}")

# Beispiel-Verwendung
if __name__ == "__main__":
    # Initialisierung mit Depot-Wert
    depot_wert = 50000  # €50.000 Depot
    calc = PositionSizeCalculator(depot_wert, risk_percentage=1.0)
    
    # Beispiel 1: NVIDIA Trade
    print("🚀 BEISPIEL 1: NVIDIA Rotes Kreuz Setup")
    nvidia_result = calc.calculate_position_size(
        entry_price=120.00,  # Stopp-Buy bei €120
        stop_loss=115.00     # Stop-Loss bei €115
    )
    nvidia_result['symbol'] = 'NVIDIA'
    print_trade_analysis(nvidia_result)
    
    print("\n" + "="*60 + "\n")
    
    # Beispiel 2: Uranium Energy Trade
    print("🚀 BEISPIEL 2: Uranium Energy Setup")
    uranium_result = calc.calculate_position_size(
        entry_price=8.50,    # Stopp-Buy bei €8.50
        stop_loss=7.80       # Stop-Loss bei €7.80
    )
    uranium_result['symbol'] = 'Uranium Energy'
    print_trade_analysis(uranium_result)
    
    print("\n" + "="*60 + "\n")
    
    # Beispiel 3: Batch-Berechnung mehrerer Trades
    print("🚀 BEISPIEL 3: Mehrere Trades gleichzeitig")
    trades = [
        {'symbol': 'AAPL', 'entry': 180.00, 'stop_loss': 175.00},
        {'symbol': 'TSLA', 'entry': 250.00, 'stop_loss': 240.00},
        {'symbol': 'AMD', 'entry': 140.00, 'stop_loss': 135.00}
    ]
    
    batch_results = calc.batch_calculate(trades)
    for result in batch_results:
        print_trade_analysis(result)
        print()
