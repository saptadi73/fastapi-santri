"""Service for santri rumah operations."""

from uuid import UUID
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import update
from fastapi import UploadFile, HTTPException

from app.models.santri_pribadi import SantriPribadi
from app.models.santri_rumah import SantriRumah
from app.models.foto_rumah import FotoRumah
from app.schemas.santri_rumah_schema import SantriRumahCreate, SantriRumahUpdate
from app.supports import FileHandler


class SantriRumahService:
    """Service for managing santri rumah data."""

    def __init__(self, db: Session):
        self.db = db
        self.file_handler = FileHandler(
            upload_dir="uploads/rumah",
            max_size_mb=5,
            allowed_extensions=[".jpg", ".jpeg", ".png", ".webp"]
        )

    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        santri_id: Optional[UUID] = None,
        pesantren_id: Optional[UUID] = None,
    ) -> Tuple[List[SantriRumah], int]:
        """Get all rumah records with pagination and optional filtering."""
        query = self.db.query(SantriRumah)

        if santri_id:
            query = query.filter(SantriRumah.santri_id == santri_id)

        if pesantren_id:
            query = query.join(
                SantriPribadi, SantriPribadi.id == SantriRumah.santri_id
            ).filter(SantriPribadi.pesantren_id == pesantren_id)

        total = query.count()
        offset = (page - 1) * per_page

        rumah_list = query.offset(offset).limit(per_page).all()
        return rumah_list, total

    def get_by_id(self, rumah_id: UUID) -> Optional[SantriRumah]:
        """Get rumah by ID."""
        return self.db.query(SantriRumah).filter(SantriRumah.id == rumah_id).first()

    def get_by_santri_id(self, santri_id: UUID) -> Optional[SantriRumah]:
        """Get rumah by santri ID."""
        return self.db.query(SantriRumah).filter(SantriRumah.santri_id == santri_id).first()

    async def create(
        self,
        data: SantriRumahCreate,
        foto_files: Optional[List[UploadFile]] = None
    ) -> SantriRumah:
        """Create new rumah record with optional photos."""
        try:
            rumah = SantriRumah(
                santri_id=data.santri_id,
                status_rumah=data.status_rumah,
                jenis_lantai=data.jenis_lantai,
                jenis_dinding=data.jenis_dinding,
                jenis_atap=data.jenis_atap,
                akses_air_bersih=data.akses_air_bersih,
                daya_listrik_va=data.daya_listrik_va
            )
            self.db.add(rumah)
            self.db.flush()
            
            # Upload photos if provided
            if foto_files:
                for foto_file in foto_files:
                    file_path, filename = await self.file_handler.save_file(
                        foto_file, f"{rumah.id}"
                    )
                    
                    foto = FotoRumah(
                        rumah_id=rumah.id,
                        nama_file=filename,
                        url_photo=file_path
                    )
                    self.db.add(foto)
            
            self.db.commit()
            self.db.refresh(rumah)
            return rumah
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create rumah: {str(e)}")

    async def update(
        self,
        rumah_id: UUID,
        data: SantriRumahUpdate,
        foto_files: Optional[List[UploadFile]] = None
    ) -> Optional[SantriRumah]:
        """Update rumah by ID (partial update) with optional new photos."""
        rumah = self.get_by_id(rumah_id)
        if not rumah:
            return None

        try:
            update_dict = data.model_dump(exclude_unset=True)
            
            # Update rumah fields if any
            if update_dict:
                stmt = update(SantriRumah).where(SantriRumah.id == rumah_id).values(**update_dict)
                self.db.execute(stmt)
            
            # Upload new photos if provided
            if foto_files:
                for foto_file in foto_files:
                    file_path, filename = await self.file_handler.save_file(
                        foto_file, f"{rumah_id}"
                    )
                    
                    foto = FotoRumah(
                        rumah_id=rumah_id,
                        nama_file=filename,
                        url_photo=file_path
                    )
                    self.db.add(foto)
            
            self.db.commit()
            return self.get_by_id(rumah_id)
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update rumah: {str(e)}")

    async def delete(self, rumah_id: UUID) -> bool:
        """Delete rumah by ID and related photos."""
        rumah = self.get_by_id(rumah_id)
        if not rumah:
            return False

        # Delete photos from disk
        fotos = self.db.query(FotoRumah).filter(
            FotoRumah.rumah_id == rumah_id
        ).all()
        
        for foto in fotos:
            self.file_handler.delete_file(str(foto.url_photo))

        self.db.delete(rumah)
        self.db.commit()
        return True
    
    async def add_photos(
        self,
        rumah_id: UUID,
        foto_files: List[UploadFile]
    ) -> List[FotoRumah]:
        """Add photos to existing rumah."""
        rumah = self.db.query(SantriRumah).filter(
            SantriRumah.id == rumah_id
        ).first()
        
        if not rumah:
            raise HTTPException(status_code=404, detail="Rumah not found")
        
        fotos = []
        try:
            for foto_file in foto_files:
                file_path, filename = await self.file_handler.save_file(
                    foto_file, f"{rumah_id}"
                )
                
                foto = FotoRumah(
                    rumah_id=rumah_id,
                    nama_file=filename,
                    url_photo=file_path
                )
                self.db.add(foto)
                fotos.append(foto)
            
            self.db.commit()
            return fotos
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to upload photos: {str(e)}")
    
    async def update_photo(self, foto_id: UUID, new_foto_file: UploadFile) -> Optional[FotoRumah]:
        """Replace a photo with a new one."""
        foto = self.db.query(FotoRumah).filter(
            FotoRumah.id == foto_id
        ).first()
        
        if not foto:
            return None
        
        try:
            # Delete old file from disk
            self.file_handler.delete_file(str(foto.url_photo))
            
            # Upload new file
            rumah_id = foto.rumah_id
            file_path, filename = await self.file_handler.save_file(
                new_foto_file, f"{rumah_id}"
            )
            
            # Update database record
            stmt = update(FotoRumah).where(FotoRumah.id == foto_id).values(
                nama_file=filename,
                url_photo=file_path
            )
            self.db.execute(stmt)
            self.db.commit()
            
            # Refresh to get updated object
            foto = self.db.query(FotoRumah).filter(FotoRumah.id == foto_id).first()
            return foto
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update photo: {str(e)}")
    
    async def delete_photo(self, foto_id: UUID) -> bool:
        """Delete single photo."""
        foto = self.db.query(FotoRumah).filter(
            FotoRumah.id == foto_id
        ).first()
        
        if not foto:
            return False
        
        # Delete file from disk
        self.file_handler.delete_file(str(foto.url_photo))
        
        # Delete from database
        self.db.delete(foto)
        self.db.commit()
        
        return True
