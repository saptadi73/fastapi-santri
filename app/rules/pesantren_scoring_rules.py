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
) -> Tuple[int, list]:
    """Calculate score for one dimension based on parameters.
    
    Returns:
        - int: average score for dimension
        - list: parameter details for breakdown
    """
    # Get all data
    data = repo.get_all(pesantren_id)
    
    total_param_score = 0
    param_count = 0
    detail_params = []
    
    # Map parameter keys to friendly names
    param_name_map = {
        "kondisi_bangunan": "Kondisi Bangunan",
        "status_bangunan": "Status Bangunan",
        "keamanan_bangunan": "Keamanan Bangunan",
        "jenis_lantai": "Jenis Lantai",
        "jenis_dinding": "Jenis Dinding",
        "jenis_atap": "Jenis Atap",
        "air_bersih": "Air Bersih",
        "sumber_air": "Sumber Air",
        "kualitas_air": "Kualitas Air",
        "sanitasi": "Sanitasi",
        "sumber_listrik": "Sumber Listrik",
        "kestabilan_listrik": "Kestabilan Listrik",
        "fasilitas_mengajar": "Fasilitas Mengajar",
        "fasilitas_komunikasi": "Fasilitas Komunikasi",
        "fasilitas_transportasi": "Fasilitas Transportasi",
        "akses_jalan": "Akses Jalan",
        "jenjang_pendidikan": "Jenjang Pendidikan",
        "kurikulum": "Kurikulum",
        "akreditasi": "Akreditasi",
        "prestasi_santri": "Prestasi Santri"
    }
    
    for param in dimension["parameters"]:
        key = param["key"]
        mapping = param["mapping"]
        param_name = param_name_map.get(key, key.replace("_", " ").title())
        
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
        param_score = 0
        if value and value in mapping:
            param_score = mapping[value]
            total_param_score += param_score
            param_count += 1
        elif value:
            # If value exists but not in mapping, use lowest score
            param_score = min(mapping.values()) if mapping else 0
            total_param_score += param_score
            param_count += 1
        
        # Add to detail breakdown
        detail_params.append({
            "parameter": param_name,
            "nilai": str(value).replace("_", " ").title() if value else "Tidak ada data",
            "skor": param_score
        })
    
    # Calculate average score for this dimension
    if param_count > 0:
        avg_score = total_param_score / param_count
    else:
        avg_score = 0
    
    return int(avg_score), detail_params


def categorize_score(total_score: int, result_mapping: list) -> str:
    """Determine category based on total score."""
    for rule in result_mapping:
        if total_score >= rule["min"]:
            return rule["category"]
    return "tidak_layak"


def calculate_pesantren_scores_from_config(
    repo: PesantrenDataRepository,
    pesantren_id: UUID
) -> Tuple[Dict[str, int], int, str, str, str, Dict[str, Any]]:
    """
    Calculate all dimension scores and total for a pesantren.
    
    Returns:
        - per_dimension: dict with dimension scores
        - total_score: weighted total score
        - category: category label
        - method: scoring method name
        - version: configuration version
        - breakdown: detailed breakdown for display
    """
    config = load_pesantren_scoring_config()
    
    dimensions = config["dimensions"]
    result_mapping = config["result_mapping"]
    
    per_dimension = {}
    weighted_total = 0.0
    breakdown_dimensi = []
    
    # Friendly dimension names
    dimension_name_map = {
        "kelayakan_fisik": "Kelayakan Fisik Bangunan",
        "air_sanitasi": "Air Bersih dan Sanitasi",
        "fasilitas_pendukung": "Fasilitas Pendukung",
        "mutu_pendidikan": "Mutu Pendidikan"
    }
    
    # Category interpretations
    kategori_interpretasi = {
        "sangat_layak": "Kondisi sangat baik, memenuhi semua standar kelayakan",
        "layak": "Kondisi baik, memenuhi standar kelayakan",
        "cukup_layak": "Kondisi cukup, perlu perbaikan di beberapa aspek",
        "tidak_layak": "Kondisi kurang baik, memerlukan perbaikan menyeluruh"
    }
    
    for dimension in dimensions:
        dim_key = dimension["key"]
        weight = dimension["weight"]
        
        # Calculate raw score for this dimension with details
        dim_score, detail_params = calculate_dimension_score(repo, pesantren_id, dimension)
        
        # Store dimension score
        per_dimension[f"skor_{dim_key}"] = dim_score
        
        # Add weighted contribution to total
        contribution = dim_score * weight
        weighted_total += contribution
        
        # Interpretasi dimensi berdasarkan skor
        if dim_score >= 85:
            interpretasi = "Sangat Baik"
        elif dim_score >= 70:
            interpretasi = "Baik"
        elif dim_score >= 55:
            interpretasi = "Cukup"
        else:
            interpretasi = "Kurang"
        
        breakdown_dimensi.append({
            "nama": dimension_name_map.get(dim_key, dim_key.replace("_", " ").title()),
            "skor": dim_score,
            "skor_maks": 100,
            "bobot": weight * 100,  # Convert to percentage
            "kontribusi": round(contribution, 2),
            "interpretasi": interpretasi,
            "detail": detail_params
        })
    
    total_score = int(weighted_total)
    category = categorize_score(total_score, result_mapping)
    
    method = f"{config['scoring_type']}.rules"
    version = config["version"]
    
    breakdown = {
        "dimensi": breakdown_dimensi,
        "skor_total": total_score,
        "kategori_kelayakan": category,
        "interpretasi_kategori": kategori_interpretasi.get(category, "")
    }
    
    return per_dimension, total_score, category, method, version, breakdown


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
