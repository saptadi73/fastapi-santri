"""Repository for fetching pesantren data across all tables."""

from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.pondok_pesantren import PondokPesantren
from app.models.pesantren_fisik import PesantrenFisik
from app.models.pesantren_fasilitas import PesantrenFasilitas
from app.models.pesantren_pendidikan import PesantrenPendidikan


class PesantrenDataRepository:
    """Repository to retrieve pesantren data from multiple tables."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_pesantren(self, pesantren_id: UUID) -> Optional[PondokPesantren]:
        """Get basic pesantren data."""
        return self.db.query(PondokPesantren).filter(
            PondokPesantren.id == pesantren_id
        ).first()
    
    def get_fisik(self, pesantren_id: UUID) -> Optional[PesantrenFisik]:
        """Get pesantren fisik data."""
        return self.db.query(PesantrenFisik).filter(
            PesantrenFisik.pesantren_id == pesantren_id
        ).first()
    
    def get_fasilitas(self, pesantren_id: UUID) -> Optional[PesantrenFasilitas]:
        """Get pesantren fasilitas data."""
        return self.db.query(PesantrenFasilitas).filter(
            PesantrenFasilitas.pesantren_id == pesantren_id
        ).first()
    
    def get_pendidikan(self, pesantren_id: UUID) -> Optional[PesantrenPendidikan]:
        """Get pesantren pendidikan data."""
        return self.db.query(PesantrenPendidikan).filter(
            PesantrenPendidikan.pesantren_id == pesantren_id
        ).first()
    
    def get_all(self, pesantren_id: UUID) -> Dict[str, Any]:
        """
        Get all pesantren data for scoring.
        
        Returns a dictionary with all tables' data.
        """
        result = {
            "pesantren": self.get_pesantren(pesantren_id),
            "fisik": self.get_fisik(pesantren_id),
            "fasilitas": self.get_fasilitas(pesantren_id),
            "pendidikan": self.get_pendidikan(pesantren_id),
        }
        return result
