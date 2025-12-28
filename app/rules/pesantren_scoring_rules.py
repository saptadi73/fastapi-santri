"""Scoring rules for pesantren based on JSON configuration."""

import json
import os
from typing import Dict, Any, Tuple
from uuid import UUID

from app.repositories.pesantren_data_repository import PesantrenDataRepository


def load_pesantren_scoring_config() -> Dict[str, Any]:
    """Load pesantren scoring configuration from JSON file."""
    config_path = os.path.join(
        os.path.dirname(__file__),
        "pesantren_scoring.json"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_dimension_score(
    repo: PesantrenDataRepository,
    pesantren_id: UUID,
    dimension: Dict[str, Any]
) -> int:
    """Calculate score for one dimension based on parameters."""
    # Get all data
    data = repo.get_all(pesantren_id)
    
    total_param_score = 0
    param_count = 0
    
    for param in dimension["parameters"]:
        key = param["key"]
        mapping = param["mapping"]
        
        # Find value from appropriate table
        value = None
        
        # Check fisik table
        if data["fisik"] and hasattr(data["fisik"], key):
            value = getattr(data["fisik"], key)
        
        # Check fasilitas table
        elif data["fasilitas"] and hasattr(data["fasilitas"], key):
            value = getattr(data["fasilitas"], key)
        
        # Check pendidikan table
        elif data["pendidikan"] and hasattr(data["pendidikan"], key):
            value = getattr(data["pendidikan"], key)
        
        # Map value to score
        if value and value in mapping:
            total_param_score += mapping[value]
            param_count += 1
        elif value:
            # If value exists but not in mapping, use lowest score
            total_param_score += min(mapping.values()) if mapping else 0
            param_count += 1
    
    # Calculate average score for this dimension
    if param_count > 0:
        avg_score = total_param_score / param_count
    else:
        avg_score = 0
    
    return int(avg_score)


def categorize_score(total_score: int, result_mapping: list) -> str:
    """Determine category based on total score."""
    for rule in result_mapping:
        if total_score >= rule["min"]:
            return rule["category"]
    return "tidak_layak"


def calculate_pesantren_scores_from_config(
    repo: PesantrenDataRepository,
    pesantren_id: UUID
) -> Tuple[Dict[str, int], int, str, str, str]:
    """
    Calculate all dimension scores and total for a pesantren.
    
    Returns:
        - per_dimension: dict with dimension scores
        - total_score: weighted total score
        - category: category label
        - method: scoring method name
        - version: configuration version
    """
    config = load_pesantren_scoring_config()
    
    dimensions = config["dimensions"]
    result_mapping = config["result_mapping"]
    
    per_dimension = {}
    weighted_total = 0.0
    
    for dimension in dimensions:
        dim_key = dimension["key"]
        weight = dimension["weight"]
        
        # Calculate raw score for this dimension
        dim_score = calculate_dimension_score(repo, pesantren_id, dimension)
        
        # Store dimension score
        per_dimension[f"skor_{dim_key}"] = dim_score
        
        # Add weighted contribution to total
        weighted_total += dim_score * weight
    
    total_score = int(weighted_total)
    category = categorize_score(total_score, result_mapping)
    
    method = f"{config['scoring_type']}.rules"
    version = config["version"]
    
    return per_dimension, total_score, category, method, version


def aggregate_pesantren_scores(
    skor_kelayakan_fisik: int,
    skor_air_sanitasi: int,
    skor_fasilitas_pendukung: int,
    skor_mutu_pendidikan: int
) -> Tuple[int, str]:
    """
    Calculate total score from dimension scores (legacy support).
    
    Returns:
        - total_score: weighted total
        - category: category label
    """
    config = load_pesantren_scoring_config()
    
    # Weights from config
    weights = {
        "kelayakan_fisik": 0.40,
        "air_sanitasi": 0.25,
        "fasilitas_pendukung": 0.20,
        "mutu_pendidikan": 0.15,
    }
    
    weighted_total = (
        skor_kelayakan_fisik * weights["kelayakan_fisik"] +
        skor_air_sanitasi * weights["air_sanitasi"] +
        skor_fasilitas_pendukung * weights["fasilitas_pendukung"] +
        skor_mutu_pendidikan * weights["mutu_pendidikan"]
    )
    
    total_score = int(weighted_total)
    category = categorize_score(total_score, config["result_mapping"])
    
    return total_score, category
