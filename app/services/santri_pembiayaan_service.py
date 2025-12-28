"""Services for santri pembiayaan business logic."""

from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.santri_pembiayaan import SantriPembiayaan
from app.models.santri_pribadi import SantriPribadi
from app.schemas.santri_pembiayaan_schema import SantriPembiayaanCreate, SantriPembiayaanUpdate


class SantriPembiayaanService:
    """Service class for santri pembiayaan operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        santri_id: Optional[UUID] = None,
        sumber_biaya: Optional[str] = None,
        status_pembayaran: Optional[str] = None,
        pesantren_id: Optional[UUID] = None,
    ) -> Tuple[List[SantriPembiayaan], int]:
        """
        Get all pembiayaan records with pagination and filters.
        
        Returns:
            Tuple of (list of pembiayaan, total count)
        """
        query = self.db.query(SantriPembiayaan)
        
        # Filter by santri_id if provided
        if santri_id:
            query = query.filter(SantriPembiayaan.santri_id == santri_id)
        
        # Filter by sumber_biaya if provided
        if sumber_biaya:
            query = query.filter(SantriPembiayaan.sumber_biaya == sumber_biaya)
        
        # Filter by status_pembayaran if provided
        if status_pembayaran:
            query = query.filter(SantriPembiayaan.status_pembayaran == status_pembayaran)

        # Filter by pesantren_id via join to SantriPribadi
        if pesantren_id:
            query = query.join(
                SantriPribadi, SantriPribadi.id == SantriPembiayaan.santri_id
            ).filter(SantriPribadi.pesantren_id == pesantren_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        pembiayaan_list = query.offset(offset).limit(per_page).all()
        
        return pembiayaan_list, total
    
    def get_by_id(self, pembiayaan_id: UUID) -> Optional[SantriPembiayaan]:
        """Get pembiayaan by ID."""
        return self.db.query(SantriPembiayaan).filter(
            SantriPembiayaan.id == pembiayaan_id
        ).first()
    
    def get_by_santri_id(self, santri_id: UUID) -> Optional[SantriPembiayaan]:
        """Get pembiayaan by santri ID."""
        return self.db.query(SantriPembiayaan).filter(
            SantriPembiayaan.santri_id == santri_id
        ).first()
    
    def create(self, data: SantriPembiayaanCreate) -> SantriPembiayaan:
        """
        Create new pembiayaan record.
        
        Args:
            data: Pembiayaan data
            
        Returns:
            Created pembiayaan object
        """
        # Check if santri exists
        santri = self.db.query(SantriPribadi).filter(
            SantriPribadi.id == data.santri_id
        ).first()
        if not santri:
            raise HTTPException(status_code=404, detail="Santri tidak ditemukan")
        
        # Check if pembiayaan already exists for this santri
        existing = self.get_by_santri_id(data.santri_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Data pembiayaan untuk santri ini sudah ada"
            )
        
        # Create pembiayaan
        pembiayaan_dict = data.model_dump()
        pembiayaan = SantriPembiayaan(**pembiayaan_dict)
        self.db.add(pembiayaan)
        self.db.commit()
        self.db.refresh(pembiayaan)
        return pembiayaan
    
    def update(
        self,
        pembiayaan_id: UUID,
        data: SantriPembiayaanUpdate
    ) -> Optional[SantriPembiayaan]:
        """
        Update pembiayaan data.
        
        Args:
            pembiayaan_id: Pembiayaan ID
            data: Updated data
            
        Returns:
            Updated pembiayaan object or None if not found
        """
        pembiayaan = self.get_by_id(pembiayaan_id)
        if not pembiayaan:
            return None
        
        # Update fields
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(pembiayaan, key, value)
        
        self.db.commit()
        self.db.refresh(pembiayaan)
        return pembiayaan
    
    def delete(self, pembiayaan_id: UUID) -> bool:
        """
        Delete pembiayaan record.
        
        Args:
            pembiayaan_id: Pembiayaan ID
            
        Returns:
            True if deleted, False if not found
        """
        pembiayaan = self.get_by_id(pembiayaan_id)
        if not pembiayaan:
            return False
        
        self.db.delete(pembiayaan)
        self.db.commit()
        return True
