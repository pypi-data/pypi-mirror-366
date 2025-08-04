#!/usr/bin/env python3
"""
Cross-Currency Convention Parser

Parses cross-currency default conventions from cross_currency_basis_swap.txt
and creates xccy_default_convention_config objects using xsigma builders.
"""

from pathlib import Path
from typing import Dict, Any
from xsigmamodules.Market import xccyDefaultConventionConfigBuilder
from xsigmamodules.market.enum_converters import (
    string_to_frequency,
    string_to_day_count,
    string_to_business_day_convention,
    settlement_days_to_int,
    get_currency_calendar_mapping,
)


class XccyConventionParser:
    """Parser for cross-currency conventions from cross_currency_basis_swap.txt."""
    
    def __init__(self, data_path: str):
        """
        Initialize the parser.
        
        Args:
            data_path: Directory containing the data files
        """
        self.data_path = Path(data_path)
        self.currency_calendar_map = get_currency_calendar_mapping()
    
    def parse_xccy_conventions(self) -> Dict[str, Dict]:
        """
        Parse cross-currency conventions from cross_currency_basis_swap.txt.
        
        Returns:
            Dictionary mapping currency codes to convention data
        """
        file_path = self.data_path
        conventions = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('CURRENCY') or line.startswith('-'):
                    continue
                
                # Parse table rows (pipe-separated format)
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 6 and parts[0]:
                    currency_code = parts[0]
                    convention = {
                        'currency': currency_code,
                        'benchmark_rate': parts[1],
                        'payment_frequency': parts[2],
                        'day_count_convention': parts[3],
                        'settlement': parts[4],
                        'business_day_convention': parts[5]
                    }
                    conventions[currency_code] = convention
        
        return conventions
    
    def create_xccy_convention(self, currency_str: str) -> Any:
        """
        Create xccy_default_convention_config for given currency.
        
        Args:
            currency_str: Currency code (e.g., "USD", "EUR")
            
        Returns:
            xccy_default_convention_config object
            
        Raises:
            ValueError: If no convention found for the specified currency
        """
        conventions = self.parse_xccy_conventions()
        
        if currency_str not in conventions:
            raise ValueError(f"No cross-currency convention found for {currency_str}")
        
        conv = conventions[currency_str]

        # Build the configuration using xsigma builder
        builder = xccyDefaultConventionConfigBuilder()

        return (builder
               .with_currency(currency_str)
               .with_benchmark_rate(conv['benchmark_rate'])
               .with_payment_frequency(string_to_frequency(conv['payment_frequency']))
               .with_day_count_convention(string_to_day_count(conv['day_count_convention']))
               .with_settlement_days(settlement_days_to_int(conv['settlement']))
               .with_business_day_convention(string_to_business_day_convention(conv['business_day_convention']))
               .with_calendar_name(self.currency_calendar_map.get(currency_str, currency_str))
               .build())
        
        return config
    
    def get_available_currencies(self) -> list:
        """Get list of available currencies for cross-currency conventions."""
        return list(self.parse_xccy_conventions().keys())

    def validate_data_file(self) -> bool:
        """Validate that the cross_currency_basis_swap.txt file exists and is readable."""
        return (self.data_path / "cross_currency_basis_swap.txt").exists()
