"""Service for pesantren pendidikan CRUD operations."""

from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.pesantren_pendidikan import PesantrenPendidikan
from app.models.pondok_pesantren import PondokPesantren
from app.schemas.pesantren_pendidikan_schema import PesantrenPendidikanCreate, PesantrenPendidikanUpdate


class PesantrenPendidikanService:
    """Service class for pesantren pendidikan operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_pesantren_id(self, pesantren_id: UUID) -> Optional[PesantrenPendidikan]:
        """Get pesantren pendidikan by pesantren ID."""
        return self.db.query(PesantrenPendidikan).filter(
            PesantrenPendidikan.pesantren_id == pesantren_id
        ).first()
    
    def get_by_id(self, pendidikan_id: UUID) -> Optional[PesantrenPendidikan]:
        """Get pesantren pendidikan by ID."""
        return self.db.query(PesantrenPendidikan).filter(
            PesantrenPendidikan.id == pendidikan_id
        ).first()
    
    def create(self, data: PesantrenPendidikanCreate) -> PesantrenPendidikan:
        """Create new pesantren pendidikan record."""
        # Check if pesantren exists
        pesantren = self.db.query(PondokPesantren).filter(
            PondokPesantren.id == data.pesantren_id
        ).first()
        if not pesantren:
            raise HTTPException(status_code=404, detail="Pesantren tidak ditemukan")
        
        # Check if pendidikan already exists for this pesantren
        existing = self.get_by_pesantren_id(data.pesantren_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Data pendidikan untuk pesantren ini sudah ada"
            )
        
        # Create pendidikan
        pendidikan_dict = data.model_dump()
        pendidikan = PesantrenPendidikan(**pendidikan_dict)
        self.db.add(pendidikan)
        self.db.commit()
        self.db.refresh(pendidikan)
        return pendidikan
    
    def update(
        self,
        pendidikan_id: UUID,
        data: PesantrenPendidikanUpdate
    ) -> Optional[PesantrenPendidikan]:
        """Update pesantren pendidikan data."""
        pendidikan = self.get_by_id(pendidikan_id)
        if not pendidikan:
            return None
        
        # Update fields
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(pendidikan, key, value)
        
        self.db.commit()
        self.db.refresh(pendidikan)
        return pendidikan
    
    def delete(self, pendidikan_id: UUID) -> bool:
        """Delete pesantren pendidikan record."""
        pendidikan = self.get_by_id(pendidikan_id)
        if not pendidikan:
            return False
        
        self.db.delete(pendidikan)
        self.db.commit()
        return True
