"""Resource counting and formatting functionality."""

from typing import Dict
from catscan.utils import get_logger
logger = get_logger('catscan.scanner.resources')


def count_resources_recursive(module_data: Dict) -> Dict[str, int]:
    """Recursively count resources in a module and all child modules.
    
    Args:
        module_data: Module data containing resources and child_modules
        
    Returns:
        Dictionary mapping resource type to count
    """
    logger.debug("Counting resources recursively in module")
    resource_counts = {}
    
    # Count resources in current module
    resources = module_data.get("resources", [])
    logger.debug(f"Found {len(resources)} resources in current module")
    
    for resource in resources:
        # Skip data sources (they start with "data.")
        if resource.get("mode") == "data":
            continue
        resource_type = resource.get("type", "unknown")
        resource_counts[resource_type] = resource_counts.get(resource_type, 0) + 1
    
    # Recursively count resources in child modules
    child_modules = module_data.get("child_modules", [])
    if child_modules:
        logger.debug(f"Processing {len(child_modules)} child modules")
    
    for child in child_modules:
        child_counts = count_resources_recursive(child)
        # Merge child counts into total
        for rtype, count in child_counts.items():
            resource_counts[rtype] = resource_counts.get(rtype, 0) + count
    
    total = sum(resource_counts.values())
    logger.debug(f"Module total: {total} resources across {len(resource_counts)} types")
    
    return resource_counts


def format_resource_summary(resource_counts: Dict[str, int]) -> str:
    """Format resource counts into a readable string.
    
    Args:
        resource_counts: Dictionary mapping resource type to count
        
    Returns:
        Formatted string summary of resources
    """
    if not resource_counts:
        logger.debug("No resources to format")
        return "[dim]No resources[/dim]"
    
    sorted_resources = sorted(resource_counts.items(), key=lambda x: (-x[1], x[0]))
    total = sum(resource_counts.values())
    
    logger.debug(f"Formatting summary for {total} resources across {len(sorted_resources)} types")
    
    if len(sorted_resources) <= 3:
        summary = ", ".join([f"{rtype}({count})" for rtype, count in sorted_resources])
    else:
        top_3 = ", ".join([f"{rtype}({count})" for rtype, count in sorted_resources[:3]])
        summary = f"{top_3} + {len(sorted_resources)-3} more ({total} total)"
    
    logger.debug(f"Formatted summary: {summary}")
    return summary