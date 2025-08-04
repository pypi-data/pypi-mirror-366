#!/usr/bin/env python3
"""
Enum Converters for XSigma Market Data

Converts string values from data files to xsigma enum types.
Optimized for production use with minimal code.
"""

try:
    from xsigmamodules.Util import (
        frequency_enum,
        day_count_convention_enum,
        business_day_convention_enum,
        future_type_enum,
    )
except ImportError:
    # Mock enums for testing
    class MockEnum:
        def __init__(self, name): self.name = name
        def __str__(self): return self.name
        def __repr__(self): return f"MockEnum({self.name})"

    class frequency_enum:
        ANNUAL = MockEnum("ANNUAL")
        SEMI_ANNUAL = MockEnum("SEMI_ANNUAL")
        QUARTERLY = MockEnum("QUARTERLY")
        MONTHLY = MockEnum("MONTHLY")
        BIMONTHLY = MockEnum("BIMONTHLY")

    class day_count_convention_enum:
        ACT_365 = MockEnum("ACT_365")
        ACT_360 = MockEnum("ACT_360")
        ACT_ACT = MockEnum("ACT_ACT")
        B_30_360 = MockEnum("B_30_360")
        B_30U_360 = MockEnum("B_30U_360")
        B_30E_360 = MockEnum("B_30E_360")
        BUS_252 = MockEnum("BUS_252")

    class business_day_convention_enum:
        MODIFIED_FOLLOWING = MockEnum("MODIFIED_FOLLOWING")
        FOLLOWING = MockEnum("FOLLOWING")
        PRECEDING = MockEnum("PRECEDING")
        MODIFIED_PRECEDING = MockEnum("MODIFIED_PRECEDING")
        UNADJUSTED = MockEnum("UNADJUSTED")

    class future_type_enum:
        SIMPLE = MockEnum("SIMPLE")
        ARITHMETIC_AVERAGE = MockEnum("ARITHMETIC_AVERAGE")
        COMPOUNDING = MockEnum("COMPOUNDING")


def string_to_frequency(freq_str: str) -> frequency_enum:
    """Convert frequency string to frequency_enum."""
    return {
        "Annual": frequency_enum.ANNUAL,
        "Semi-annual": frequency_enum.SEMI_ANNUAL,
        "Quarterly": frequency_enum.QUARTERLY,
        "Monthly": frequency_enum.MONTHLY,
        "Bimonthly": frequency_enum.BIMONTHLY,
    }.get(freq_str, frequency_enum.ANNUAL)


def string_to_day_count(day_count_str: str) -> day_count_convention_enum:
    """Convert day count string to day_count_convention_enum."""
    return {
        "30/360": day_count_convention_enum.B_30_360,
        "30U/360": day_count_convention_enum.B_30U_360,
        "30E/360": day_count_convention_enum.B_30E_360,
        "ACT/365": day_count_convention_enum.ACT_365,
        "ACT/360": day_count_convention_enum.ACT_360,
        "ACT/ACT": day_count_convention_enum.ACT_ACT,
        "Actual/365": day_count_convention_enum.ACT_365,
        "Actual/360": day_count_convention_enum.ACT_360,
        "Business/252": day_count_convention_enum.BUS_252,
        "ACT/252": day_count_convention_enum.BUS_252,
    }.get(day_count_str, day_count_convention_enum.ACT_365)


def string_to_business_day_convention(bdc_str: str) -> business_day_convention_enum:
    """Convert business day convention string to business_day_convention_enum."""
    return {
        "Modified Following": business_day_convention_enum.MODIFIED_FOLLOWING,
        "Following": business_day_convention_enum.FOLLOWING,
        "Preceding": business_day_convention_enum.PRECEDING,
        "Modified Preceding": business_day_convention_enum.MODIFIED_PRECEDING,
        "Unadjusted": business_day_convention_enum.UNADJUSTED,
    }.get(bdc_str, business_day_convention_enum.MODIFIED_FOLLOWING)


def settlement_days_to_int(settlement_str: str) -> int:
    """Convert settlement string (T+2, T-1, etc.) to integer days."""
    if settlement_str.startswith("T+"):
        return int(settlement_str[2:])
    elif settlement_str.startswith("T-"):
        return -int(settlement_str[2:])
    elif settlement_str in ("T+0", "T-0"):
        return 0
    return 2  # Default


def string_to_future_type(future_type_str: str) -> future_type_enum:
    """Convert future type string to future_type_enum."""
    return {
        "SIMPLE": future_type_enum.SIMPLE,
        "ARITHMETIC_AVERAGE": future_type_enum.ARITHMETIC_AVERAGE,
        "COMPOUNDING": future_type_enum.COMPOUNDING,
    }.get(future_type_str, future_type_enum.SIMPLE)


def get_currency_calendar_mapping() -> dict:
    """Get currency to calendar mapping."""
    return {
        "USD": "NYSE", "EUR": "EUR", "GBP": "LDN", "JPY": "TOK",
        "AUD": "AUSY", "CAD": "TSE", "CHF": "ZUR", "CNY": "CNBE",
        "INR": "INMU", "BRL": "BRSP", "RUB": "RUMO", "MXN": "MXMC",
        "ZAR": "ZAJO", "TRY": "TRIS", "KRW": "KRSE", "IDR": "IDJA",
        "SAR": "SARI", "SEK": "SEST", "NOK": "NOOS", "DKK": "DKCO",
        "NZD": "NZWE", "SGD": "SGSI", "HKD": "HKHK", "PLN": "PLN"
    }
