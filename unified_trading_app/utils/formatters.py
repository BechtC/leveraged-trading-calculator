#!/usr/bin/env python3
"""
Utility Functions - Formatters
"""


def format_currency(value: float, decimals: int = 2) -> str:
    """
    Formatiert Wert als Euro

    Args:
        value: Wert in EUR
        decimals: Nachkommastellen (Standard: 2)

    Returns:
        Formatierter String (z.B. "€1,234.56")
    """
    return f"€{value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formatiert Wert als Prozent

    Args:
        value: Wert (0-100)
        decimals: Nachkommastellen (Standard: 1)

    Returns:
        Formatierter String (z.B. "45.5%")
    """
    return f"{value:.{decimals}f}%"


def format_r_multiple(value: float, decimals: int = 2) -> str:
    """
    Formatiert R-Multiple

    Args:
        value: R-Multiple Wert
        decimals: Nachkommastellen (Standard: 2)

    Returns:
        Formatierter String (z.B. "2.50R")
    """
    return f"{value:.{decimals}f}R"


def get_product_badge(product_type: str) -> str:
    """
    Gibt Badge-Emoji für Produkt-Typ zurück

    Args:
        product_type: Produkt-Typ

    Returns:
        Emoji
    """
    badges = {
        "spot": "📈",
        "cfd_long": "🔥",
        "cfd_short": "🔻",
        "knockout_long": "🚀",
        "knockout_short": "📉"
    }
    return badges.get(product_type, "❓")


def get_product_label(product_type: str) -> str:
    """
    Gibt lesbaren Label für Produkt-Typ zurück

    Args:
        product_type: Produkt-Typ

    Returns:
        Label
    """
    labels = {
        "spot": "Spot",
        "cfd_long": "CFD Long",
        "cfd_short": "CFD Short",
        "knockout_long": "Knockout Long",
        "knockout_short": "Knockout Short"
    }
    return labels.get(product_type, product_type)


def get_status_badge(status: str) -> str:
    """
    Gibt Badge-Emoji für Trade-Status zurück

    Args:
        status: Trade Status

    Returns:
        Emoji
    """
    badges = {
        "planned": "📋",
        "open": "🟢",
        "closed": "⚫"
    }
    return badges.get(status, "❓")


def calculate_pnl(current_price: float, entry_price: float, units: int, is_short: bool = False) -> float:
    """
    Berechnet P&L

    Args:
        current_price: Aktueller Preis
        entry_price: Einstiegspreis
        units: Anzahl Einheiten
        is_short: Ist Short-Position

    Returns:
        P&L in EUR
    """
    if is_short:
        return units * (entry_price - current_price)
    else:
        return units * (current_price - entry_price)


def calculate_current_r_multiple(current_price: float, entry_price: float, stop_loss: float, is_short: bool = False) -> float:
    """
    Berechnet aktuelles R-Multiple

    Args:
        current_price: Aktueller Preis
        entry_price: Einstiegspreis
        stop_loss: Stop-Loss
        is_short: Ist Short-Position

    Returns:
        R-Multiple
    """
    if is_short:
        risk_per_unit = stop_loss - entry_price
        profit_per_unit = entry_price - current_price
    else:
        risk_per_unit = entry_price - stop_loss
        profit_per_unit = current_price - entry_price

    if risk_per_unit == 0:
        return 0

    return profit_per_unit / risk_per_unit
