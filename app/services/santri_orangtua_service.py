"""Services for santri orangtua business logic."""

from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.santri_pribadi import SantriPribadi
from sqlalchemy import func, or_
from fastapi import UploadFile, HTTPException

from app.models.santri_orangtua import SantriOrangtua
from app.models.foto_orangtua import FotoOrangtua
from app.schemas.santri_orangtua_schema import SantriOrangtuaCreate, SantriOrangtuaUpdate
from app.supports import FileHandler


class SantriOrangtuaService:
    """Service class for santri orangtua operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.file_handler = FileHandler(
            upload_dir="uploads/orangtua",
            max_size_mb=5,
            allowed_extensions=[".jpg", ".jpeg", ".png", ".webp"]
        )
    
    def get_all(
        self,
        santri_id: Optional[UUID] = None,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        hubungan: Optional[str] = None,
        pesantren_id: Optional[UUID] = None,
    ) -> Tuple[List[SantriOrangtua], int]:
        """Get all orangtua with pagination and filters."""
        query = self.db.query(SantriOrangtua)

        if santri_id:
            query = query.filter(SantriOrangtua.santri_id == santri_id)

        if pesantren_id:
            query = query.join(
                SantriPribadi, SantriPribadi.id == SantriOrangtua.santri_id
            ).filter(SantriPribadi.pesantren_id == pesantren_id)
        
        if search:
            query = query.filter(
                or_(
                    SantriOrangtua.nama.ilike(f"%{search}%"),
                    SantriOrangtua.nik.ilike(f"%{search}%")
                )
            )
        
        if hubungan:
            query = query.filter(SantriOrangtua.hubungan == hubungan)
        
        total = query.count()
        orangtua_list = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return orangtua_list, total
    
    def get_by_id(self, orangtua_id: UUID) -> Optional[SantriOrangtua]:
        """Get orangtua by ID with photos."""
        return self.db.query(SantriOrangtua).filter(
            SantriOrangtua.id == orangtua_id
        ).first()
    
    async def create(
        self,
        santri_id: UUID,
        data: SantriOrangtuaCreate,
        foto_files: Optional[List[UploadFile]] = None
    ) -> SantriOrangtua:
        """Create new orangtua with optional photos."""
        try:
            # Create orangtua
            orangtua = SantriOrangtua(
                santri_id=santri_id,
                nama=data.nama,
                nik=data.nik,
                hubungan=data.hubungan,
                pendidikan=data.pendidikan,
                pekerjaan=data.pekerjaan,
                pendapatan_bulanan=data.pendapatan_bulanan,
                status_hidup=data.status_hidup,
                kontak_telepon=data.kontak_telepon
            )
            
            self.db.add(orangtua)
            self.db.flush()
            
            # Upload photos if provided
            if foto_files:
                for foto_file in foto_files:
                    url_photo = await self.file_handler.save_file(
                        foto_file, f"{orangtua.id}"
                    )
                    
                    foto = FotoOrangtua(
                        orangtua_id=orangtua.id,
                        nama_file=foto_file.filename,
                        url_photo=url_photo
                    )
                    self.db.add(foto)
            
            self.db.commit()
            self.db.refresh(orangtua)
            return orangtua
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create orangtua: {str(e)}")
    
    async def update(
        self,
        orangtua_id: UUID,
        data: SantriOrangtuaUpdate
    ) -> Optional[SantriOrangtua]:
        """Update orangtua by ID."""
        orangtua = self.db.query(SantriOrangtua).filter(
            SantriOrangtua.id == orangtua_id
        ).first()
        
        if not orangtua:
            return None
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(orangtua, field, value)
        
        self.db.commit()
        self.db.refresh(orangtua)
        return orangtua
    
    async def delete(self, orangtua_id: UUID) -> bool:
        """Delete orangtua and related photos."""
        orangtua = self.db.query(SantriOrangtua).filter(
            SantriOrangtua.id == orangtua_id
        ).first()
        
        if not orangtua:
            return False
        
        # Delete photos from disk
        fotos = self.db.query(FotoOrangtua).filter(
            FotoOrangtua.orangtua_id == orangtua_id
        ).all()
        
        for foto in fotos:
            self.file_handler.delete_file(str(foto.url_photo))
        
        # Delete orangtua (cascade will delete fotos)
        self.db.delete(orangtua)
        self.db.commit()
        
        return True
    
    async def add_photos(
        self,
        orangtua_id: UUID,
        foto_files: List[UploadFile]
    ) -> List[FotoOrangtua]:
        """Add photos to existing orangtua."""
        orangtua = self.db.query(SantriOrangtua).filter(
            SantriOrangtua.id == orangtua_id
        ).first()
        
        if not orangtua:
            raise HTTPException(status_code=404, detail="Orangtua not found")
        
        fotos = []
        try:
            for foto_file in foto_files:
                url_photo = await self.file_handler.save_file(
                    foto_file, f"{orangtua_id}"
                )
                
                foto = FotoOrangtua(
                    orangtua_id=orangtua_id,
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
        foto = self.db.query(FotoOrangtua).filter(
            FotoOrangtua.id == foto_id
        ).first()
        
        if not foto:
            return False
        
        # Delete file from disk
        self.file_handler.delete_file(str(foto.url_photo))
        
        # Delete from database
        self.db.delete(foto)
        self.db.commit()
        
        return True
    
    async def update_photo(self, foto_id: UUID, new_foto_file: UploadFile) -> Optional[FotoOrangtua]:
        """Replace a photo with a new one.
        
        Deletes the old file from disk and uploads the new one.
        
        Args:
            foto_id: Photo ID to update
            new_foto_file: New photo file to upload
            
        Returns:
            Updated FotoOrangtua object or None if not found
        """
        foto = self.db.query(FotoOrangtua).filter(
            FotoOrangtua.id == foto_id
        ).first()
        
        if not foto:
            return None
        
        try:
            # Delete old file from disk
            self.file_handler.delete_file(str(foto.url_photo))
            
            # Upload new file
            orangtua_id = foto.orangtua_id
            url_photo = await self.file_handler.save_file(
                new_foto_file, f"{orangtua_id}"
            )
            
            # Update database record using SQLAlchemy update
            from sqlalchemy import update
            stmt = update(FotoOrangtua).where(FotoOrangtua.id == foto_id).values(
                nama_file=new_foto_file.filename,
                url_photo=url_photo
            )
            self.db.execute(stmt)
            self.db.commit()
            
            # Refresh to get updated object
            foto = self.db.query(FotoOrangtua).filter(FotoOrangtua.id == foto_id).first()
            return foto
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update photo: {str(e)}")
