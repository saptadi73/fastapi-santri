"""Services for santri pribadi business logic."""

from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from fastapi import UploadFile, HTTPException

from app.models.santri_pribadi import SantriPribadi
from app.models.foto_santri import FotoSantri
from app.schemas.santri_pribadi_schema import SantriPribadiCreate, SantriPribadiUpdate
from app.supports import FileHandler


class SantriPribadiService:
    """Service class for santri pribadi operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.file_handler = FileHandler(
            upload_dir="uploads/santri",
            max_size_mb=5,
            allowed_extensions=[".jpg", ".jpeg", ".png", ".webp"]
        )
    
    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        provinsi: Optional[str] = None,
        kabupaten: Optional[str] = None,
        jenis_kelamin: Optional[str] = None,
        pesantren_id: Optional[UUID] = None,
    ) -> Tuple[List[SantriPribadi], int]:
        """
        Get all santri with pagination and filters.
        
        Returns:
            Tuple of (list of santri, total count)
        """
        query = self.db.query(SantriPribadi)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    SantriPribadi.nama.ilike(f"%{search}%"),
                    SantriPribadi.nik.ilike(f"%{search}%")
                )
            )
        
        if provinsi:
            query = query.filter(SantriPribadi.provinsi == provinsi)
        
        if kabupaten:
            query = query.filter(SantriPribadi.kabupaten == kabupaten)
        
        if jenis_kelamin:
            query = query.filter(SantriPribadi.jenis_kelamin == jenis_kelamin)

        if pesantren_id:
            query = query.filter(SantriPribadi.pesantren_id == pesantren_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        santri_list = query.offset(offset).limit(per_page).all()
        
        return santri_list, total
    
    def get_by_id(self, santri_id: UUID) -> Optional[SantriPribadi]:
        """Get santri by ID with photos."""
        return self.db.query(SantriPribadi).filter(
            SantriPribadi.id == santri_id
        ).first()
    
    async def create(
        self,
        data: SantriPribadiCreate,
        foto_files: Optional[List[UploadFile]] = None
    ) -> SantriPribadi:
        """
        Create new santri with optional photos.
        
        Args:
            data: Santri data
            foto_files: List of photo files to upload
            
        Returns:
            Created santri object
        """
        # Create santri object
        santri_dict = data.model_dump(exclude={"latitude", "longitude"})
        
        # Handle geometry
        if data.latitude is not None and data.longitude is not None:
            santri_dict["lokasi"] = f"POINT({data.longitude} {data.latitude})"
        
        santri = SantriPribadi(**santri_dict)
        self.db.add(santri)
        self.db.flush()  # Flush to get santri.id
        
        # Upload photos if provided
        if foto_files:
            for foto_file in foto_files:
                try:
                    file_path, filename = await self.file_handler.save_file(
                        foto_file,
                        subfolder=str(santri.id),
                        prefix="santri"
                    )
                    
                    # Create foto record
                    foto = FotoSantri(
                        santri_id=santri.id,
                        nama_file=filename,
                        url_photo=file_path
                    )
                    self.db.add(foto)
                except Exception as e:
                    # Rollback on error
                    self.db.rollback()
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to upload photo: {str(e)}"
                    )
        
        self.db.commit()
        self.db.refresh(santri)
        return santri
    
    def update(
        self,
        santri_id: UUID,
        data: SantriPribadiUpdate
    ) -> Optional[SantriPribadi]:
        """
        Update santri data.
        
        Args:
            santri_id: Santri ID
            data: Updated data
            
        Returns:
            Updated santri object or None if not found
        """
        santri = self.get_by_id(santri_id)
        if not santri:
            return None
        
        # Update fields
        update_dict = data.model_dump(exclude_unset=True, exclude={"latitude", "longitude"})
        
        # Handle geometry update
        if data.latitude is not None and data.longitude is not None:
            update_dict["lokasi"] = f"POINT({data.longitude} {data.latitude})"
        
        for key, value in update_dict.items():
            setattr(santri, key, value)
        
        self.db.commit()
        self.db.refresh(santri)
        return santri
    
    def delete(self, santri_id: UUID) -> bool:
        """
        Delete santri and associated photos.
        
        Args:
            santri_id: Santri ID
            
        Returns:
            True if deleted, False if not found
        """
        santri = self.get_by_id(santri_id)
        if not santri:
            return False
        
        # Delete photo files from disk
        for foto in santri.foto_santri:
            self.file_handler.delete_file(str(foto.url_photo))
        
        # Delete santri (cascade will delete foto records)
        self.db.delete(santri)
        self.db.commit()
        return True
    
    async def add_photos(
        self,
        santri_id: UUID,
        foto_files: List[UploadFile]
    ) -> List[FotoSantri]:
        """
        Add photos to existing santri.
        
        Args:
            santri_id: Santri ID
            foto_files: List of photo files
            
        Returns:
            List of created foto objects
        """
        santri = self.get_by_id(santri_id)
        if not santri:
            raise HTTPException(status_code=404, detail="Santri not found")
        
        foto_list = []
        for foto_file in foto_files:
            try:
                file_path, filename = await self.file_handler.save_file(
                    foto_file,
                    subfolder=str(santri_id),
                    prefix="santri"
                )
                
                foto = FotoSantri(
                    santri_id=santri_id,
                    nama_file=filename,
                    url_photo=file_path
                )
                self.db.add(foto)
                foto_list.append(foto)
            except Exception as e:
                self.db.rollback()
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload photo: {str(e)}"
                )
        
        self.db.commit()
        return foto_list
    
    def delete_photo(self, foto_id: UUID) -> bool:
        """
        Delete a single photo.
        
        Args:
            foto_id: Photo ID
            
        Returns:
            True if deleted, False if not found
        """
        foto = self.db.query(FotoSantri).filter(FotoSantri.id == foto_id).first()
        if not foto:
            return False
        
        # Delete file from disk
        self.file_handler.delete_file(str(foto.url_photo))
        
        # Delete record
        self.db.delete(foto)
        self.db.commit()
        return True
    
    async def update_photo(self, foto_id: UUID, new_foto_file: UploadFile) -> Optional[FotoSantri]:
        """
        Replace a photo with a new one.
        
        Deletes the old file from disk and uploads the new one.
        
        Args:
            foto_id: Photo ID to update
            new_foto_file: New photo file to upload
            
        Returns:
            Updated FotoSantri object or None if not found
        """
        foto = self.db.query(FotoSantri).filter(FotoSantri.id == foto_id).first()
        if not foto:
            return None
        
        try:
            # Delete old file from disk
            self.file_handler.delete_file(str(foto.url_photo))
            
            # Upload new file
            santri_id = foto.santri_id
            file_path, filename = await self.file_handler.save_file(
                new_foto_file,
                subfolder=str(santri_id),
                prefix="santri"
            )
            
            # Update database record using SQLAlchemy update
            from sqlalchemy import update
            stmt = update(FotoSantri).where(FotoSantri.id == foto_id).values(
                nama_file=filename,
                url_photo=file_path
            )
            self.db.execute(stmt)
            self.db.commit()
            
            # Refresh to get updated object
            foto = self.db.query(FotoSantri).filter(FotoSantri.id == foto_id).first()
            return foto
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update photo: {str(e)}"
            )
