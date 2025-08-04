#!/usr/bin/env python3
"""
Swap Convention Parser

Parses swap default conventions from swaps_specifications.txt and creates
swap_default_convention_config objects using xsigma builders.
"""

from pathlib import Path
from typing import Dict, Tuple, Any
from xsigmamodules.Market import swapDefaultConventionConfigBuilder
from xsigmamodules.market.enum_converters import (
    string_to_frequency,
    string_to_day_count,
    string_to_business_day_convention,
    settlement_days_to_int,
    get_currency_calendar_mapping,
)

class SwapConventionParser:
    """Parser for swap default conventions from swaps_specifications.txt."""
    
    def __init__(self, data_path: str):
        """
        Initialize the parser.
        
        Args:
            data_path: the data file paht
        """
        self.data_path = Path(data_path)
        self.currency_calendar_map = get_currency_calendar_mapping()
    
    def parse_swap_conventions(self) -> Dict[Tuple[str, str], Dict]:
        """
        Parse swap conventions from data_path.
        
        Returns:
            Dictionary mapping (currency, index_type) tuples to convention data
        """
        file_path = self.data_path
        conventions = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Parse table rows in comment format (* | ... | ... |)
                if line.startswith('* |') and '|' in line:
                    # Remove the '* |' prefix and split by '|'
                    clean_line = line[3:].strip()  # Remove '* |' (3 characters)
                    parts = [p.strip() for p in clean_line.split('|')]
                    
                    # Skip header and separator lines
                    if (len(parts) >= 13 and parts[0] and 
                        parts[0] not in ['Currency', '+----------', '', 'Country/Region']):
                        
                        currency = parts[0]
                        floating_index = parts[4]
                        index_type = parts[5]  # RFR or IBOR
                        
                        convention = {
                            'currency': currency,
                            'fixed_frequency': parts[2],
                            'fixed_day_count': parts[3],
                            'floating_index': floating_index,
                            'index_type': index_type,
                            'floating_frequency': parts[6],
                            'floating_day_count': parts[7],
                            'business_day_convention': parts[8],
                            'fixing_date': parts[9],
                            'effective_date': parts[10],
                            'calendar': parts[11]
                        }
                        
                        key = (currency, index_type)
                        conventions[key] = convention
        
        return conventions
    
    def create_swap_convention(self, currency: str, index_type: str = "") -> Any:
        """
        Create swap_default_convention_config for given currency and index type.
        
        Args:
            currency: Currency code (e.g., "USD", "EUR")
            index_type: Index type ("RFR", "IBOR", or "" for default)
            
        Returns:
            swap_default_convention_config object
            
        Raises:
            ValueError: If no convention found for the specified parameters
        """
        conventions = self.parse_swap_conventions()
        
        # Find matching convention
        if index_type:
            key = (currency, index_type)
            if key not in conventions:
                raise ValueError(f"No convention found for {currency} with {index_type}")
            conv = conventions[key]
        else:
            # Default logic: prefer IBOR if available, otherwise RFR
            ibor_key = (currency, "IBOR")
            rfr_key = (currency, "RFR")
            
            if ibor_key in conventions:
                conv = conventions[ibor_key]
            elif rfr_key in conventions:
                conv = conventions[rfr_key]
            else:
                raise ValueError(f"No convention found for currency {currency}")
        
        # Build the configuration using xsigma builder
        builder = swapDefaultConventionConfigBuilder()
        
        return (builder
               .with_floating_index(conv['floating_index'])
               .with_settlement_days(settlement_days_to_int(conv['effective_date']))
               .with_fixing_days(settlement_days_to_int(conv['fixing_date']))
               .with_business_day_convention(string_to_business_day_convention(conv['business_day_convention']))
               .with_fixed_frequency(string_to_frequency(conv['fixed_frequency']))
               .with_fixed_basis(string_to_day_count(conv['fixed_day_count']))
               .with_forecast_frequency(string_to_frequency(conv['floating_frequency']))
               .with_forecast_basis(string_to_day_count(conv['floating_day_count']))
               .with_calendar_name(self.currency_calendar_map.get(currency, currency))
               .build())
        
        return config
    
    def get_available_currencies(self) -> Dict[str, list]:
        """
        Get available currencies and their supported index types.
        
        Returns:
            Dictionary mapping currency codes to lists of available index types
        """
        conventions = self.parse_swap_conventions()
        currencies = {}
        
        for (currency, index_type), _ in conventions.items():
            if currency not in currencies:
                currencies[currency] = []
            currencies[currency].append(index_type)
        
        return currencies
    
    def validate_data_file(self) -> bool:
        """Validate that the swaps_specifications.txt file exists and is readable."""
        return (self.data_path).exists()
