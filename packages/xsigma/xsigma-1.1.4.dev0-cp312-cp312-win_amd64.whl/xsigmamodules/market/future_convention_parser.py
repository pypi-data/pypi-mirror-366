
#!/usr/bin/env python3
"""
Future Convention Parser

Parses future default conventions from futures_specifications.json and creates
futureDefaultConventionConfig objects using xsigma builders.
"""

from pathlib import Path
from typing import Dict, Any
from xsigmamodules.Market import futureDefaultConventionConfigBuilder
from xsigmamodules.market.enum_converters import (
    string_to_day_count,
    string_to_business_day_convention,
    string_to_future_type,
)

class FutureConventionParser:
    """Parser for future default conventions from futures_specifications.json."""

    def __init__(self, data_path: str):
        """
        Initialize the parser.

        Args:
            data_path: Path to the futures_specifications.json file
        """
        self.data_path = Path(data_path)

    def parse_future_conventions(self) -> Dict[str, Dict]:
        """
        Parse future conventions from futures_specifications.json.

        Returns:
            Dictionary mapping (index_tenor) keys to convention data
        """
        conventions = {}

        with open(self.data_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '|' in line and not line.startswith('|---') and not line.startswith('| Currency'):
                    # Clean and split by |
                    parts = [p.strip() for p in line.split('|')]
                    # Remove empty first/last parts from leading/trailing |
                    parts = [p for p in parts if p]

                    if len(parts) >= 14:  # Ensure we have all columns including rolling days
                        # Extract index from reference rate
                        index = parts[4]
                        key = f"{index.upper()}_{parts[1].lower()}"

                        convention = {
                            'currency': parts[0],
                            'tenor': parts[1],
                            'contract_name': parts[2],
                            'exchange': parts[3],
                            'reference_rate': parts[4],
                            'rate_fixing_time': parts[5],
                            'first_trading_day': parts[6],
                            'last_trading_day': parts[7],
                            'bus_day_conv': parts[8],
                            'day_count': parts[9],
                            'holiday_calendar': parts[10],
                            'rate_computation': parts[11],
                            'first_rolling_date': parts[12],
                            'last_rolling_date': parts[13],
                            'index': index
                        }
                        conventions[key] = convention

        return conventions

    def create_future_convention(self, index: str, tenor: str) -> Any:
        """
        Create futureDefaultConventionConfig for given index and tenor.

        Args:
            index: Index name (e.g., "SOFR", "EURIBOR")
            tenor: Tenor (e.g., "1M", "3M")

        Returns:
            futureDefaultConventionConfig object

        Raises:
            ValueError: If no convention found for the specified parameters
        """
        conventions = self.parse_future_conventions()
        key = f"{index.upper()}_{tenor.lower()}"

        if key not in conventions:
            raise ValueError(f"No future convention found for {index} {tenor}")

        conv = conventions[key]

        # Build the configuration using xsigma builder
        builder = futureDefaultConventionConfigBuilder()

        return (builder
               .with_index_tenor(conv['tenor'].lower())
               .with_index(conv['index'].upper())
               .with_start_rolling_convention(string_to_business_day_convention(conv['bus_day_conv']))
               .with_end_rolling_convention(string_to_business_day_convention(conv['bus_day_conv']))
               .with_future_type(string_to_future_type(conv['rate_computation']))
               .with_basis(string_to_day_count(conv['day_count']))
               .with_start_rolling_days(int(conv['first_rolling_date']))
               .with_end_rolling_days(int(conv['last_rolling_date']))
               .with_contract_size(1)
               .build())

    def get_available_conventions(self) -> Dict[str, list]:
        """
        Get available indices and their supported tenors.

        Returns:
            Dictionary mapping index names to lists of available tenors
        """
        conventions = self.parse_future_conventions()
        indices = {}

        for key, conv in conventions.items():
            index = conv['index'].upper()
            tenor = conv['tenor'].lower()
            if index not in indices:
                indices[index] = []
            indices[index].append(tenor)

        return indices

    def validate_data_file(self) -> bool:
        """Validate that the futures_specifications.json file exists and is readable."""
        return self.data_path.exists()

