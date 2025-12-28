"""Service for pondok pesantren CRUD operations."""

from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException

from app.models.pondok_pesantren import PondokPesantren
from app.schemas.pondok_pesantren_schema import PondokPesantrenCreate, PondokPesantrenUpdate


class PondokPesantrenService:
    """Service class for pondok pesantren operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        provinsi: Optional[str] = None,
        kabupaten: Optional[str] = None,
    ) -> Tuple[List[PondokPesantren], int]:
        """Get all pondok pesantren with pagination and filters."""
        query = self.db.query(PondokPesantren)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    PondokPesantren.nama.ilike(f"%{search}%"),
                    PondokPesantren.nsp.ilike(f"%{search}%")
                )
            )
        
        if provinsi:
            query = query.filter(PondokPesantren.provinsi == provinsi)
        
        if kabupaten:
            query = query.filter(PondokPesantren.kabupaten == kabupaten)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        pesantren_list = query.offset(offset).limit(per_page).all()
        
        return pesantren_list, total
    
    def get_by_id(self, pesantren_id: UUID) -> Optional[PondokPesantren]:
        """Get pondok pesantren by ID."""
        return self.db.query(PondokPesantren).filter(
            PondokPesantren.id == pesantren_id
        ).first()
    
    def create(self, data: PondokPesantrenCreate) -> PondokPesantren:
        """Create new pondok pesantren."""
        # Create pesantren object
        pesantren_dict = data.model_dump(exclude={"latitude", "longitude"})
        
        # Handle geometry
        if data.latitude is not None and data.longitude is not None:
            pesantren_dict["lokasi"] = f"POINT({data.longitude} {data.latitude})"
        
        pesantren = PondokPesantren(**pesantren_dict)
        self.db.add(pesantren)
        self.db.commit()
        self.db.refresh(pesantren)
        return pesantren
    
    def update(
        self,
        pesantren_id: UUID,
        data: PondokPesantrenUpdate
    ) -> Optional[PondokPesantren]:
        """Update pondok pesantren data."""
        pesantren = self.get_by_id(pesantren_id)
        if not pesantren:
            return None
        
        # Update fields
        update_dict = data.model_dump(exclude_unset=True, exclude={"latitude", "longitude"})
        
        # Handle geometry update
        if data.latitude is not None and data.longitude is not None:
            update_dict["lokasi"] = f"POINT({data.longitude} {data.latitude})"
        
        for key, value in update_dict.items():
            setattr(pesantren, key, value)
        
        self.db.commit()
        self.db.refresh(pesantren)
        return pesantren
    
    def delete(self, pesantren_id: UUID) -> bool:
        """Delete pondok pesantren."""
        pesantren = self.get_by_id(pesantren_id)
        if not pesantren:
            return False
        
        self.db.delete(pesantren)
        self.db.commit()
        return True
