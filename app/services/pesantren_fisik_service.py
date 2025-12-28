"""Service for pesantren fisik CRUD operations."""

from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.pesantren_fisik import PesantrenFisik
from app.models.pondok_pesantren import PondokPesantren
from app.schemas.pesantren_fisik_schema import PesantrenFisikCreate, PesantrenFisikUpdate


class PesantrenFisikService:
    """Service class for pesantren fisik operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_pesantren_id(self, pesantren_id: UUID) -> Optional[PesantrenFisik]:
        """Get pesantren fisik by pesantren ID."""
        return self.db.query(PesantrenFisik).filter(
            PesantrenFisik.pesantren_id == pesantren_id
        ).first()
    
    def get_by_id(self, fisik_id: UUID) -> Optional[PesantrenFisik]:
        """Get pesantren fisik by ID."""
        return self.db.query(PesantrenFisik).filter(
            PesantrenFisik.id == fisik_id
        ).first()
    
    def create(self, data: PesantrenFisikCreate) -> PesantrenFisik:
        """Create new pesantren fisik record."""
        # Check if pesantren exists
        pesantren = self.db.query(PondokPesantren).filter(
            PondokPesantren.id == data.pesantren_id
        ).first()
        if not pesantren:
            raise HTTPException(status_code=404, detail="Pesantren tidak ditemukan")
        
        # Check if fisik already exists for this pesantren
        existing = self.get_by_pesantren_id(data.pesantren_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Data fisik untuk pesantren ini sudah ada"
            )
        
        # Create fisik
        fisik_dict = data.model_dump()
        fisik = PesantrenFisik(**fisik_dict)
        self.db.add(fisik)
        self.db.commit()
        self.db.refresh(fisik)
        return fisik
    
    def update(
        self,
        fisik_id: UUID,
        data: PesantrenFisikUpdate
    ) -> Optional[PesantrenFisik]:
        """Update pesantren fisik data."""
        fisik = self.get_by_id(fisik_id)
        if not fisik:
            return None
        
        # Update fields
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(fisik, key, value)
        
        self.db.commit()
        self.db.refresh(fisik)
        return fisik
    
    def delete(self, fisik_id: UUID) -> bool:
        """Delete pesantren fisik record."""
        fisik = self.get_by_id(fisik_id)
        if not fisik:
            return False
        
        self.db.delete(fisik)
        self.db.commit()
        return True
