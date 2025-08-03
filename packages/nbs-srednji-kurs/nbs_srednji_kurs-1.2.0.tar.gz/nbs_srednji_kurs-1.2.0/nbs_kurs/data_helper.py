from typing import List, Optional

from nbs_kurs.get_values_from_nbs import ValueData


def get_value_by_currency(short_names: List[str], data: List[ValueData]) -> List[ValueData]:
    """
    Filter ValueData objects by their short_name attribute.
    
    Args:
        short_names: List of currency short names to filter by
        data: List of ValueData objects to filter
        
    Returns:
        List of ValueData objects whose short_name is in the short_names list
        
    Examples:
        >>> get_value_by_currency(["USD", "EUR"], data)
        [ValueData(short_name="USD", ...), ValueData(short_name="EUR", ...)]
    """
    if not short_names:
        return []
    
    if not data:
        return []
        
    return [item for item in data if item.short_name in short_names]


def get_currency_by_name(name: str, data: List[ValueData]) -> Optional[ValueData]:
    """
    Get the first ValueData object with the specified short_name.
    
    Args:
        name: Currency short name to search for
        data: List of ValueData objects to search in
        
    Returns:
        ValueData object if found, None otherwise
        
    Examples:
        >>> get_currency_by_name("USD", data)
        ValueData(short_name="USD", ...)
    """
    if not name or not data:
        return None
        
    for item in data:
        if item.short_name == name:
            return item
    
    return None
