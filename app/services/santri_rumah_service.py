"""Service for santri rumah operations."""

from uuid import UUID
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.models.santri_pribadi import SantriPribadi
from sqlalchemy import update

from app.models.santri_rumah import SantriRumah
from app.schemas.santri_rumah_schema import SantriRumahCreate, SantriRumahUpdate


class SantriRumahService:
    """Service for managing santri rumah data."""

    def __init__(self, db: Session):
        self.db = db

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

    def create(self, data: SantriRumahCreate) -> SantriRumah:
        """Create new rumah record."""
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
        self.db.commit()
        self.db.refresh(rumah)
        return rumah

    def update(self, rumah_id: UUID, data: SantriRumahUpdate) -> Optional[SantriRumah]:
        """Update rumah by ID (partial update)."""
        rumah = self.get_by_id(rumah_id)
        if not rumah:
            return None

        update_dict = data.model_dump(exclude_unset=True)

        stmt = update(SantriRumah).where(SantriRumah.id == rumah_id).values(**update_dict)
        self.db.execute(stmt)
        self.db.commit()

        return self.get_by_id(rumah_id)

    def delete(self, rumah_id: UUID) -> bool:
        """Delete rumah by ID."""
        rumah = self.get_by_id(rumah_id)
        if not rumah:
            return False

        self.db.delete(rumah)
        self.db.commit()
        return True
