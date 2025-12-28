"""Services for santri bansos business logic."""

from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException

from app.models.santri_bansos import SantriBansos
from app.models.santri_pribadi import SantriPribadi
from app.schemas.santri_bansos_schema import SantriBansosCreate, SantriBansosUpdate


class SantriBansosService:
    """Service class for santri bansos operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        santri_id: Optional[UUID] = None
    ) -> Tuple[List[SantriBansos], int]:
        """
        Get all bansos records with pagination and filters.
        
        Returns:
            Tuple of (list of bansos, total count)
        """
        query = self.db.query(SantriBansos)
        
        # Filter by santri_id if provided
        if santri_id:
            query = query.filter(SantriBansos.santri_id == santri_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        bansos_list = query.offset(offset).limit(per_page).all()
        
        return bansos_list, total
    
    def get_by_id(self, bansos_id: UUID) -> Optional[SantriBansos]:
        """Get bansos by ID."""
        return self.db.query(SantriBansos).filter(
            SantriBansos.id == bansos_id
        ).first()
    
    def get_by_santri_id(self, santri_id: UUID) -> Optional[SantriBansos]:
        """Get bansos by santri ID."""
        return self.db.query(SantriBansos).filter(
            SantriBansos.santri_id == santri_id
        ).first()
    
    def create(self, data: SantriBansosCreate) -> SantriBansos:
        """
        Create new bansos record.
        
        Args:
            data: Bansos data
            
        Returns:
            Created bansos object
        """
        # Check if santri exists
        santri = self.db.query(SantriPribadi).filter(
            SantriPribadi.id == data.santri_id
        ).first()
        if not santri:
            raise HTTPException(status_code=404, detail="Santri tidak ditemukan")
        
        # Check if bansos already exists for this santri
        existing = self.get_by_santri_id(data.santri_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Data bansos untuk santri ini sudah ada"
            )
        
        # Create bansos
        bansos_dict = data.model_dump()
        bansos = SantriBansos(**bansos_dict)
        self.db.add(bansos)
        self.db.commit()
        self.db.refresh(bansos)
        return bansos
    
    def update(
        self,
        bansos_id: UUID,
        data: SantriBansosUpdate
    ) -> Optional[SantriBansos]:
        """
        Update bansos data.
        
        Args:
            bansos_id: Bansos ID
            data: Updated data
            
        Returns:
            Updated bansos object or None if not found
        """
        bansos = self.get_by_id(bansos_id)
        if not bansos:
            return None
        
        # Update fields
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(bansos, key, value)
        
        self.db.commit()
        self.db.refresh(bansos)
        return bansos
    
    def delete(self, bansos_id: UUID) -> bool:
        """
        Delete bansos record.
        
        Args:
            bansos_id: Bansos ID
            
        Returns:
            True if deleted, False if not found
        """
        bansos = self.get_by_id(bansos_id)
        if not bansos:
            return False
        
        self.db.delete(bansos)
        self.db.commit()
        return True
