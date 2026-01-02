"""Service to calculate and persist pesantren scores."""

from typing import Optional, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import update
from fastapi import HTTPException

from app.repositories.pesantren_data_repository import PesantrenDataRepository
from app.rules.pesantren_scoring_rules import calculate_pesantren_scores_from_config
from app.models.pesantren_skor import PesantrenSkor
from app.services.pesantren_map_service import PesantrenMapService


class PesantrenScoreService:
    """Service for pesantren scoring operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = PesantrenDataRepository(db)
    
    def calculate_and_save(
        self,
        pesantren_id: UUID,
        metode: str = "pesantren.rules",
        version: str = "1.1"
    ) -> Tuple[PesantrenSkor, Dict[str, Any]]:
        """
        Calculate scores for a pesantren and save to database.
        
        Args:
            pesantren_id: UUID of the pesantren
            metode: Scoring method (default: pesantren.rules)
            version: Configuration version (default: 1.1)
            
        Returns:
            Tuple of (PesantrenSkor object, breakdown dict)
        """
        # Ensure pesantren exists
        pesantren = self.repo.get_pesantren(pesantren_id)
        if not pesantren:
            raise HTTPException(status_code=404, detail="Pesantren tidak ditemukan")
        
        # Compute scores using config-driven rules
        per_dimension, total, kategori, metode_cfg, version_cfg, breakdown = (
            calculate_pesantren_scores_from_config(self.repo, pesantren_id)
        )
        
        # Upsert logic: if record exists, update; else create
        existing: Optional[PesantrenSkor] = (
            self.db.query(PesantrenSkor)
            .filter(PesantrenSkor.pesantren_id == pesantren_id)
            .first()
        )
        
        if existing:
            # Update existing record
            stmt = update(PesantrenSkor).where(
                PesantrenSkor.pesantren_id == pesantren_id
            ).values(
                skor_fisik=per_dimension["skor_kelayakan_fisik"],
                skor_air_sanitasi=per_dimension["skor_air_sanitasi"],
                skor_fasilitas_pendukung=per_dimension["skor_fasilitas_pendukung"],
                skor_mutu_pendidikan=per_dimension["skor_mutu_pendidikan"],
                skor_total=total,
                kategori_kelayakan=kategori,
                metode=metode_cfg,
                version=version_cfg,
            )
            self.db.execute(stmt)
            self.db.commit()
            
            # AUTO-UPDATE PESANTREN MAP for GIS (with error handling)
            try:
                map_service = PesantrenMapService(self.db)
                map_service.upsert_from_scoring(pesantren_id, total, kategori)
            except Exception as map_error:
                # Log error but don't fail the scoring operation
                print(f"Warning: Failed to update pesantren_map: {map_error}")
            
            # Refresh and return
            existing = (
                self.db.query(PesantrenSkor)
                .filter(PesantrenSkor.pesantren_id == pesantren_id)
                .first()
            )
            return existing, breakdown
        else:
            # Create new record
            record = PesantrenSkor(
                pesantren_id=pesantren_id,
                skor_fisik=per_dimension["skor_kelayakan_fisik"],
                skor_air_sanitasi=per_dimension["skor_air_sanitasi"],
                skor_fasilitas_pendukung=per_dimension["skor_fasilitas_pendukung"],
                skor_mutu_pendidikan=per_dimension["skor_mutu_pendidikan"],
                skor_total=total,
                kategori_kelayakan=kategori,
                metode=metode_cfg,
                version=version_cfg,
            )
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            
            # AUTO-UPDATE PESANTREN MAP for GIS (with error handling)
            try:
                map_service = PesantrenMapService(self.db)
                map_service.upsert_from_scoring(pesantren_id, total, kategori)
            except Exception as map_error:
                # Log error but don't fail the scoring operation
                print(f"Warning: Failed to update pesantren_map: {map_error}")
            
            return record, breakdown
    
    def get_by_pesantren_id(self, pesantren_id: UUID) -> Optional[Tuple[PesantrenSkor, Dict[str, Any]]]:
        """Get score by pesantren ID with breakdown."""
        record = (
            self.db.query(PesantrenSkor)
            .filter(PesantrenSkor.pesantren_id == pesantren_id)
            .first()
        )
        if record:
            # Re-calculate breakdown for display
            _, _, _, _, _, breakdown = calculate_pesantren_scores_from_config(self.repo, pesantren_id)
            return record, breakdown
        return None
    
    def get_by_id(self, skor_id: UUID) -> Optional[PesantrenSkor]:
        """Get score by skor ID."""
        return (
            self.db.query(PesantrenSkor)
            .filter(PesantrenSkor.id == skor_id)
            .first()
        )
