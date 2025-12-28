"""Service for pesantren fasilitas CRUD operations."""

from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.pesantren_fasilitas import PesantrenFasilitas
from app.models.pondok_pesantren import PondokPesantren
from app.schemas.pesantren_fasilitas_schema import PesantrenFasilitasCreate, PesantrenFasilitasUpdate


class PesantrenFasilitasService:
    """Service class for pesantren fasilitas operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_pesantren_id(self, pesantren_id: UUID) -> Optional[PesantrenFasilitas]:
        """Get pesantren fasilitas by pesantren ID."""
        return self.db.query(PesantrenFasilitas).filter(
            PesantrenFasilitas.pesantren_id == pesantren_id
        ).first()
    
    def get_by_id(self, fasilitas_id: UUID) -> Optional[PesantrenFasilitas]:
        """Get pesantren fasilitas by ID."""
        return self.db.query(PesantrenFasilitas).filter(
            PesantrenFasilitas.id == fasilitas_id
        ).first()
    
    def create(self, data: PesantrenFasilitasCreate) -> PesantrenFasilitas:
        """Create new pesantren fasilitas record."""
        # Check if pesantren exists
        pesantren = self.db.query(PondokPesantren).filter(
            PondokPesantren.id == data.pesantren_id
        ).first()
        if not pesantren:
            raise HTTPException(status_code=404, detail="Pesantren tidak ditemukan")
        
        # Check if fasilitas already exists for this pesantren
        existing = self.get_by_pesantren_id(data.pesantren_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Data fasilitas untuk pesantren ini sudah ada"
            )
        
        # Create fasilitas
        fasilitas_dict = data.model_dump()
        fasilitas = PesantrenFasilitas(**fasilitas_dict)
        self.db.add(fasilitas)
        self.db.commit()
        self.db.refresh(fasilitas)
        return fasilitas
    
    def update(
        self,
        fasilitas_id: UUID,
        data: PesantrenFasilitasUpdate
    ) -> Optional[PesantrenFasilitas]:
        """Update pesantren fasilitas data."""
        fasilitas = self.get_by_id(fasilitas_id)
        if not fasilitas:
            return None
        
        # Update fields
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(fasilitas, key, value)
        
        self.db.commit()
        self.db.refresh(fasilitas)
        return fasilitas
    
    def delete(self, fasilitas_id: UUID) -> bool:
        """Delete pesantren fasilitas record."""
        fasilitas = self.get_by_id(fasilitas_id)
        if not fasilitas:
            return False
        
        self.db.delete(fasilitas)
        self.db.commit()
        return True
