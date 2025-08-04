#!/usr/bin/env python3
"""
FX Volatility Parser

Parses FX volatility calibration targets from fx_volatility.txt and creates
structured volatility data for use with xsigma FX volatility models.
"""

from pathlib import Path
from typing import Dict, List, Any


class FxVolatilityParser:
    """Parser for FX volatility calibration targets from fx_volatility.txt."""
    
    def __init__(self, data_dir: str):
        """
        Initialize the parser.
        
        Args:
            data_dir: Directory containing the data files
        """
        self.data_dir = Path(data_dir)
    
    def parse_fx_volatility(self) -> Dict[str, List]:
        """
        Parse FX volatility data from fx_volatility.txt.
        
        Returns:
            Dictionary containing parsed volatility surface data
        """
        file_path = self.data_dir / "fx_volatility.txt"
        data = {
            'tenors': [], 'atm': [], 'rr25': [], 'ms25': [], 'rr10': [], 'ms10': []
        }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # Skip header line
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                
                # Split by whitespace and handle multiple spaces/tabs
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        data['tenors'].append(parts[0])  # tenor is a string in xsigma
                        data['atm'].append(float(parts[1]))
                        data['rr25'].append(float(parts[2]))
                        data['ms25'].append(float(parts[3]))
                        data['rr10'].append(float(parts[4]))
                        data['ms10'].append(float(parts[5]))
                    except (ValueError, Exception) as e:
                        print(f"Warning: Skipping invalid line: {line} - {e}")
                        continue
        
        return data
    
    def create_fx_volatility_targets(self, currency_pair: str = "EURUSD") -> Dict[str, Any]:
        """
        Create FX volatility calibration targets from fx_volatility.txt.
        
        Args:
            currency_pair: Currency pair identifier (e.g., "EURUSD")
            
        Returns:
            Dictionary containing structured FX volatility data
            
        Raises:
            ValueError: If no valid FX volatility data found
        """
        data = self.parse_fx_volatility()
        
        if not data['tenors']:
            raise ValueError("No valid FX volatility data found")
        
        # Create structured volatility surface data
        volatility_data = {
            'currency_pair': currency_pair,
            'tenors': data['tenors'],
            'atm_vols': data['atm'],
            'risk_reversals_25': data['rr25'],
            'market_strangles_25': data['ms25'],
            'risk_reversals_10': data['rr10'],
            'market_strangles_10': data['ms10'],
            'num_tenors': len(data['tenors'])
        }
        
        # Add derived data for convenience
        volatility_data['tenor_strings'] = data['tenors']  # tenors are already strings
        volatility_data['atm_vol_range'] = {
            'min': min(data['atm']),
            'max': max(data['atm']),
            'avg': sum(data['atm']) / len(data['atm'])
        }
        
        return volatility_data
    
    def create_volatility_smile_data(self, tenor_index: int = 0) -> Dict[str, Any]:
        """
        Create volatility smile data for a specific tenor.
        
        Args:
            tenor_index: Index of the tenor to extract (0-based)
            
        Returns:
            Dictionary containing smile data for the specified tenor
            
        Raises:
            ValueError: If tenor_index is out of range
        """
        data = self.parse_fx_volatility()
        
        if not data['tenors'] or tenor_index >= len(data['tenors']):
            raise ValueError(f"Invalid tenor index: {tenor_index}")
        
        smile_data = {
            'tenor': data['tenors'][tenor_index],
            'tenor_string': data['tenors'][tenor_index],  # tenor is already a string
            'atm_vol': data['atm'][tenor_index],
            'risk_reversal_25': data['rr25'][tenor_index],
            'market_strangle_25': data['ms25'][tenor_index],
            'risk_reversal_10': data['rr10'][tenor_index],
            'market_strangle_10': data['ms10'][tenor_index]
        }
        
        # Calculate implied strikes/deltas (simplified)
        smile_data['strikes'] = {
            'atm': 1.0,  # Normalized ATM
            'call_25': 1.0 + data['rr25'][tenor_index] / 100,  # Simplified
            'put_25': 1.0 - data['rr25'][tenor_index] / 100,   # Simplified
            'call_10': 1.0 + data['rr10'][tenor_index] / 100,  # Simplified
            'put_10': 1.0 - data['rr10'][tenor_index] / 100    # Simplified
        }
        
        return smile_data
    
    def get_available_tenors(self) -> List[str]:
        """Get list of available tenors."""
        return self.parse_fx_volatility()['tenors']

    def validate_data_file(self) -> bool:
        """Validate that the fx_volatility.txt file exists and is readable."""
        return (self.data_dir / "fx_volatility.txt").exists()
