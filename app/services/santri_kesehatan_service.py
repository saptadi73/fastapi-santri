"""Services for santri kesehatan business logic."""

from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.santri_kesehatan import SantriKesehatan
from app.models.santri_pribadi import SantriPribadi
from app.schemas.santri_kesehatan_schema import SantriKesehatanCreate, SantriKesehatanUpdate


class SantriKesehatanService:
    """Service class for santri kesehatan operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        santri_id: Optional[UUID] = None,
        status_gizi: Optional[str] = None,
        pesantren_id: Optional[UUID] = None,
    ) -> Tuple[List[SantriKesehatan], int]:
        """
        Get all kesehatan records with pagination and filters.
        
        Returns:
            Tuple of (list of kesehatan, total count)
        """
        query = self.db.query(SantriKesehatan)
        
        # Filter by santri_id if provided
        if santri_id:
            query = query.filter(SantriKesehatan.santri_id == santri_id)
        
        # Filter by status_gizi if provided
        if status_gizi:
            query = query.filter(SantriKesehatan.status_gizi == status_gizi)

        # Filter by pesantren_id via join to SantriPribadi
        if pesantren_id:
            query = query.join(
                SantriPribadi, SantriPribadi.id == SantriKesehatan.santri_id
            ).filter(SantriPribadi.pesantren_id == pesantren_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        kesehatan_list = query.offset(offset).limit(per_page).all()
        
        return kesehatan_list, total
    
    def get_by_id(self, kesehatan_id: UUID) -> Optional[SantriKesehatan]:
        """Get kesehatan by ID."""
        return self.db.query(SantriKesehatan).filter(
            SantriKesehatan.id == kesehatan_id
        ).first()
    
    def get_by_santri_id(self, santri_id: UUID) -> Optional[SantriKesehatan]:
        """Get kesehatan by santri ID."""
        return self.db.query(SantriKesehatan).filter(
            SantriKesehatan.santri_id == santri_id
        ).first()
    
    def create(self, data: SantriKesehatanCreate) -> SantriKesehatan:
        """
        Create new kesehatan record.
        
        Args:
            data: Kesehatan data
            
        Returns:
            Created kesehatan object
        """
        # Check if santri exists
        santri = self.db.query(SantriPribadi).filter(
            SantriPribadi.id == data.santri_id
        ).first()
        if not santri:
            raise HTTPException(status_code=404, detail="Santri tidak ditemukan")
        
        # Check if kesehatan already exists for this santri
        existing = self.get_by_santri_id(data.santri_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Data kesehatan untuk santri ini sudah ada"
            )
        
        # Create kesehatan
        kesehatan_dict = data.model_dump()
        kesehatan = SantriKesehatan(**kesehatan_dict)
        self.db.add(kesehatan)
        self.db.commit()
        self.db.refresh(kesehatan)
        return kesehatan
    
    def update(
        self,
        kesehatan_id: UUID,
        data: SantriKesehatanUpdate
    ) -> Optional[SantriKesehatan]:
        """
        Update kesehatan data.
        
        Args:
            kesehatan_id: Kesehatan ID
            data: Updated data
            
        Returns:
            Updated kesehatan object or None if not found
        """
        kesehatan = self.get_by_id(kesehatan_id)
        if not kesehatan:
            return None
        
        # Update fields
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(kesehatan, key, value)
        
        self.db.commit()
        self.db.refresh(kesehatan)
        return kesehatan
    
    def delete(self, kesehatan_id: UUID) -> bool:
        """
        Delete kesehatan record.
        
        Args:
            kesehatan_id: Kesehatan ID
            
        Returns:
            True if deleted, False if not found
        """
        kesehatan = self.get_by_id(kesehatan_id)
        if not kesehatan:
            return False
        
        self.db.delete(kesehatan)
        self.db.commit()
        return True
