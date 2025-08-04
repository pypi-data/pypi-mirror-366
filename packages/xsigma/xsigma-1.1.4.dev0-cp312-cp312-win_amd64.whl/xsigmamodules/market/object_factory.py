import os
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple, Union


class ObjectFactory:
    def __init__(self, xml_path: str, data_root: str):
        """Initialize the ObjectFactory with XML rules and data root path.

        Args:
            xml_path: Path to the XML configuration file
            data_root: Root path for data files
        """
        self.data_root = data_root
        self.mappings = self._load_mappings(xml_path)

    def _load_mappings(self, xml_path: str) -> Dict[str, Dict[str, str]]:
        """Load and parse the XML mapping rules.

        Args:
            xml_path: Path to the XML configuration file

        Returns:
            Dictionary of mapping rules
        """
        tree = ET.parse(xml_path)
        root = tree.getroot()

        mappings = {}
        for mapping in root.findall("mapping"):
            id_pattern = mapping.find("id_pattern").text
            object_type = mapping.find("object_type").text
            factory_method = mapping.find("factory_method").text
            path_template = mapping.find("path_template").text

            mappings[id_pattern] = {
                "object_type": object_type,
                "factory_method": factory_method,
                "path_template": path_template,
            }

        return mappings

    def _match_pattern(
        self, id_pattern: str, id_value: str
    ) -> Optional[Tuple[str, List[str]]]:
        """Match an ID value against a pattern and extract parameters.

        Args:
            id_pattern: Pattern to match against
            id_value: Actual ID value

        Returns:
            Tuple of (matched pattern, list of parameters) or None if no match
        """
        # Convert pattern to regex
        regex_pattern = id_pattern.replace("*", "([^_]+)")
        match = re.match(regex_pattern, id_value)

        if match:
            return id_pattern, match.groups()
        return None

    def contains(self, id_value: Union[str, Any]) -> bool:
        """Check if the factory supports creating an object for the given ID.

        Args:
            id_value: The ID value or ID object to check

        Returns:
            True if the factory can create an object for this ID, False otherwise
        """
        if not isinstance(id_value, str):
            id_value = str(id_value)

        for pattern in self.mappings:
            if self._match_pattern(pattern, id_value):
                return True
        return False

    def create_object(self, id_value: Union[str, Any]) -> Any:
        """Create an object based on the ID value using the mapping rules.

        Args:
            id_value: The ID value or ID object to create an object for

        Returns:
            Created object

        Raises:
            ValueError: If no matching rule is found
        """
        # Convert ID object to string if needed
        if not isinstance(id_value, str):
            id_value = str(id_value)

        # Find matching pattern
        for pattern, mapping in self.mappings.items():
            match_result = self._match_pattern(pattern, id_value)
            if match_result:
                matched_pattern, params = match_result
                return self._create_object_from_mapping(mapping, params)

        raise ValueError(f"No mapping rule found for ID: {id_value}")

    def _create_object_from_mapping(
        self, mapping: Dict[str, str], params: List[str]
    ) -> Any:
        """Create an object using the mapping rule and parameters.

        Args:
            mapping: Mapping rule dictionary
            params: List of parameters extracted from ID

        Returns:
            Created object
        """
        # Get the object type and factory method
        object_type = mapping["object_type"]
        factory_method = mapping["factory_method"]

        # Build the path template
        path_template = mapping["path_template"]
        path = path_template.replace("${XSIGMA_DATA_ROOT}", self.data_root)

        # Replace parameters in path
        for i, param in enumerate(params, 1):
            path = path.replace(f"{{param{i}}}", param)
            path = path.replace("{param}", param)  # For single parameter cases

        # Import the required module and get the factory method
        module = __import__(f"xsigma", fromlist=[object_type])
        obj_class = getattr(module, object_type)
        factory = getattr(obj_class, factory_method)

        # Create and return the object
        return factory(path)

    def update_market_container(self, market_container: Any, ids: List[Any]) -> None:
        """Update market container with objects created from a list of IDs.

        Args:
            market_container: The market container to update
            ids: List of IDs to create objects for
        """
        from xsigmamodules.Market import anyId, anyObject

        for id in ids:
            market_container.insert(id, anyObject(self.create_object(str(id))))
