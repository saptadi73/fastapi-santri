"""Services for santri asset business logic."""

from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from fastapi import UploadFile, HTTPException

from app.models.santri_asset import SantriAsset
from app.models.foto_asset import FotoAsset
from app.schemas.santri_asset_schema import SantriAssetCreate, SantriAssetUpdate
from app.supports import FileHandler


class SantriAssetService:
    """Service class for santri asset operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.file_handler = FileHandler(
            upload_dir="uploads/asset",
            max_size_mb=5,
            allowed_extensions=[".jpg", ".jpeg", ".png", ".webp"]
        )
    
    def get_all(
        self,
        santri_id: UUID,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        jenis_aset: Optional[str] = None,
    ) -> Tuple[List[SantriAsset], int]:
        """Get all assets for a santri with pagination and filters."""
        query = self.db.query(SantriAsset).filter(
            SantriAsset.santri_id == santri_id
        )
        
        if search:
            query = query.filter(
                SantriAsset.jenis_aset.ilike(f"%{search}%")
            )
        
        if jenis_aset:
            query = query.filter(SantriAsset.jenis_aset == jenis_aset)
        
        total = query.count()
        asset_list = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return asset_list, total
    
    def get_by_id(self, asset_id: UUID) -> Optional[SantriAsset]:
        """Get asset by ID with photos."""
        return self.db.query(SantriAsset).filter(
            SantriAsset.id == asset_id
        ).first()
    
    async def create(
        self,
        santri_id: UUID,
        data: SantriAssetCreate,
        foto_files: Optional[List[UploadFile]] = None
    ) -> SantriAsset:
        """Create new asset with optional photos."""
        try:
            # Create asset
            asset = SantriAsset(
                santri_id=santri_id,
                jenis_aset=data.jenis_aset,
                jumlah=data.jumlah,
                nilai_perkiraan=data.nilai_perkiraan
            )
            
            self.db.add(asset)
            self.db.flush()
            
            # Upload photos if provided
            if foto_files:
                for foto_file in foto_files:
                    url_photo = await self.file_handler.save_file(
                        foto_file, f"{asset.id}"
                    )
                    
                    foto = FotoAsset(
                        asset_id=asset.id,
                        nama_file=foto_file.filename,
                        url_photo=url_photo
                    )
                    self.db.add(foto)
            
            self.db.commit()
            self.db.refresh(asset)
            return asset
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create asset: {str(e)}")
    
    async def update(
        self,
        asset_id: UUID,
        data: SantriAssetUpdate
    ) -> Optional[SantriAsset]:
        """Update asset by ID."""
        asset = self.db.query(SantriAsset).filter(
            SantriAsset.id == asset_id
        ).first()
        
        if not asset:
            return None
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(asset, field, value)
        
        self.db.commit()
        self.db.refresh(asset)
        return asset
    
    async def delete(self, asset_id: UUID) -> bool:
        """Delete asset and related photos."""
        asset = self.db.query(SantriAsset).filter(
            SantriAsset.id == asset_id
        ).first()
        
        if not asset:
            return False
        
        # Delete photos from disk
        fotos = self.db.query(FotoAsset).filter(
            FotoAsset.asset_id == asset_id
        ).all()
        
        for foto in fotos:
            self.file_handler.delete_file(str(foto.url_photo))
        
        # Delete asset (cascade will delete fotos)
        self.db.delete(asset)
        self.db.commit()
        
        return True
    
    async def add_photos(
        self,
        asset_id: UUID,
        foto_files: List[UploadFile]
    ) -> List[FotoAsset]:
        """Add photos to existing asset."""
        asset = self.db.query(SantriAsset).filter(
            SantriAsset.id == asset_id
        ).first()
        
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        fotos = []
        try:
            for foto_file in foto_files:
                url_photo = await self.file_handler.save_file(
                    foto_file, f"{asset_id}"
                )
                
                foto = FotoAsset(
                    asset_id=asset_id,
                    nama_file=foto_file.filename,
                    url_photo=url_photo
                )
                self.db.add(foto)
                fotos.append(foto)
            
            self.db.commit()
            return fotos
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to upload photos: {str(e)}")
    
    async def delete_photo(self, foto_id: UUID) -> bool:
        """Delete single photo."""
        foto = self.db.query(FotoAsset).filter(
            FotoAsset.id == foto_id
        ).first()
        
        if not foto:
            return False
        
        # Delete file from disk
        self.file_handler.delete_file(str(foto.url_photo))
        
        # Delete from database
        self.db.delete(foto)
        self.db.commit()
        
        return True
    
    async def update_photo(self, foto_id: UUID, new_foto_file: UploadFile) -> Optional[FotoAsset]:
        """Replace a photo with a new one.
        
        Deletes the old file from disk and uploads the new one.
        
        Args:
            foto_id: Photo ID to update
            new_foto_file: New photo file to upload
            
        Returns:
            Updated FotoAsset object or None if not found
        """
        foto = self.db.query(FotoAsset).filter(
            FotoAsset.id == foto_id
        ).first()
        
        if not foto:
            return None
        
        try:
            # Delete old file from disk
            self.file_handler.delete_file(str(foto.url_photo))
            
            # Upload new file
            asset_id = foto.asset_id
            url_photo = await self.file_handler.save_file(
                new_foto_file, f"{asset_id}"
            )
            
            # Update database record using SQLAlchemy update
            from sqlalchemy import update
            stmt = update(FotoAsset).where(FotoAsset.id == foto_id).values(
                nama_file=new_foto_file.filename,
                url_photo=url_photo
            )
            self.db.execute(stmt)
            self.db.commit()
            
            # Refresh to get updated object
            foto = self.db.query(FotoAsset).filter(FotoAsset.id == foto_id).first()
            return foto
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update photo: {str(e)}")
