"""Service to calculate and persist santri scores."""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import update

from app.repositories.santri_data_repository import SantriDataRepository
from app.rules.scoring_rules import aggregate_scores, calculate_scores_from_config
from app.models.santri_skor import SantriSkor
from fastapi import HTTPException


class ScoreService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SantriDataRepository(db)

    def calculate_and_save(self, santri_id: UUID, metode: str = "rules.v1", version: str = "1.0.0") -> SantriSkor:
        # Ensure santri exists
        pribadi = self.repo.get_pribadi(santri_id)
        if not pribadi:
            raise HTTPException(status_code=404, detail="Santri tidak ditemukan")

        # Compute scores using config-driven rules
        per_component, total, kategori, metode_cfg, version_cfg = calculate_scores_from_config(self.repo, santri_id)

        # Upsert logic: if record exists, update; else create
        existing: Optional[SantriSkor] = self.db.query(SantriSkor).filter(SantriSkor.santri_id == santri_id).first()
        if existing:
            stmt = update(SantriSkor).where(SantriSkor.santri_id == santri_id).values(
                skor_ekonomi=per_component["skor_ekonomi"],
                skor_rumah=per_component["skor_rumah"],
                skor_aset=per_component["skor_aset"],
                skor_pembiayaan=per_component["skor_pembiayaan"],
                skor_kesehatan=per_component["skor_kesehatan"],
                skor_bansos=per_component["skor_bansos"],
                skor_total=total,
                kategori_kemiskinan=kategori,
                metode=metode_cfg,
                version=version_cfg,
            )
            self.db.execute(stmt)
            self.db.commit()
            # Refresh
            existing = self.db.query(SantriSkor).filter(SantriSkor.santri_id == santri_id).first()
            return existing
        else:
            record = SantriSkor(
                santri_id=santri_id,
                skor_ekonomi=per_component["skor_ekonomi"],
                skor_rumah=per_component["skor_rumah"],
                skor_aset=per_component["skor_aset"],
                skor_pembiayaan=per_component["skor_pembiayaan"],
                skor_kesehatan=per_component["skor_kesehatan"],
                skor_bansos=per_component["skor_bansos"],
                skor_total=total,
                kategori_kemiskinan=kategori,
                metode=metode_cfg,
                version=version_cfg,
            )
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record

    def get_by_santri_id(self, santri_id: UUID) -> Optional[SantriSkor]:
        return self.db.query(SantriSkor).filter(SantriSkor.santri_id == santri_id).first()

    def get_by_id(self, skor_id: UUID) -> Optional[SantriSkor]:
        return self.db.query(SantriSkor).filter(SantriSkor.id == skor_id).first()
