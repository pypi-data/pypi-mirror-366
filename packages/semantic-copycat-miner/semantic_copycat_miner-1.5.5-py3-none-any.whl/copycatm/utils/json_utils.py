"""
JSON utilities for CopycatM.
"""

import json
from typing import Any, Dict
from datetime import datetime
from .. import __version__


def format_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format output data for consistent JSON structure."""
    # Ensure all timestamps are in ISO format
    if "analysis_timestamp" in data:
        if isinstance(data["analysis_timestamp"], datetime):
            data["analysis_timestamp"] = data["analysis_timestamp"].isoformat() + "Z"
    
    # Ensure all numeric values are properly formatted
    def format_numeric_values(obj):
        if isinstance(obj, dict):
            return {k: format_numeric_values(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [format_numeric_values(item) for item in obj]
        elif isinstance(obj, float):
            # Round to 2 decimal places for readability
            return round(obj, 2)
        else:
            return obj
    
    return format_numeric_values(data)


def validate_output_structure(data: Dict[str, Any]) -> bool:
    """Validate that output data has the expected structure."""
    required_fields = [
        "copycatm_version",
        "analysis_config",
        "file_metadata",
        "file_properties",
        "algorithms",
        "mathematical_invariants",
        "analysis_summary"
    ]
    
    for field in required_fields:
        if field not in data:
            return False
    
    return True


def serialize_output(data: Dict[str, Any], indent: int = 2) -> str:
    """Serialize output data to JSON string."""
    formatted_data = format_output(data)
    
    # Custom JSON encoder for handling special types
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat() + "Z"
            return super().default(obj)
    
    return json.dumps(formatted_data, indent=indent, cls=CustomEncoder)


def deserialize_output(json_str: str) -> Dict[str, Any]:
    """Deserialize JSON string to output data."""
    return json.loads(json_str)


def merge_outputs(outputs: list[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple analysis outputs into a single output."""
    if not outputs:
        return {}
    
    merged = {
        "copycatm_version": outputs[0].get("copycatm_version", __version__),
        "analysis_config": outputs[0].get("analysis_config", {}),
        "results": outputs,
        "summary": {
            "total_files": len(outputs),
            "total_algorithms": sum(len(out.get("algorithms", [])) for out in outputs),
            "total_invariants": sum(len(out.get("mathematical_invariants", [])) for out in outputs),
            "average_confidence": 0.0,
            "processing_time_ms": 0
        }
    }
    
    # Calculate averages
    total_confidence = 0.0
    total_time = 0
    count = 0
    
    for output in outputs:
        summary = output.get("analysis_summary", {})
        total_confidence += summary.get("average_confidence", 0.0)
        total_time += summary.get("processing_time_ms", 0)
        count += 1
    
    if count > 0:
        merged["summary"]["average_confidence"] = round(total_confidence / count, 2)
        merged["summary"]["processing_time_ms"] = total_time
    
    return merged 