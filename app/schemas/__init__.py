"""Schemas package for request/response models."""

from .santri_pribadi_schema import (
    FotoSantriBase,
    FotoSantriResponse,
    SantriPribadiBase,
    SantriPribadiCreate,
    SantriPribadiUpdate,
    SantriPribadiResponse,
    SantriPribadiListResponse,
)

from .santri_orangtua_schema import (
    FotoOrangtuaBase,
    FotoOrangtuaResponse,
    SantriOrangtuaBase,
    SantriOrangtuaCreate,
    SantriOrangtuaUpdate,
    SantriOrangtuaResponse,
    SantriOrangtuaListResponse,
)

from .santri_asset_schema import (
    FotoAssetBase,
    FotoAssetResponse,
    SantriAssetBase,
    SantriAssetCreate,
    SantriAssetUpdate,
    SantriAssetResponse,
    SantriAssetListResponse,
)

from .santri_bansos_schema import (
    SantriBansosBase,
    SantriBansosCreate,
    SantriBansosUpdate,
    SantriBansosResponse,
)

from .santri_kesehatan_schema import (
    SantriKesehatanBase,
    SantriKesehatanCreate,
    SantriKesehatanUpdate,
    SantriKesehatanResponse,
)

from .santri_pembiayaan_schema import (
    SantriPembiayaanBase,
    SantriPembiayaanCreate,
    SantriPembiayaanUpdate,
    SantriPembiayaanResponse,
)

from .santri_skor_schema import (
    SantriSkorResponse,
)

__all__ = [
    "FotoSantriBase",
    "FotoSantriResponse",
    "SantriPribadiBase",
    "SantriPribadiCreate",
    "SantriPribadiUpdate",
    "SantriPribadiResponse",
    "SantriPribadiListResponse",
    "FotoOrangtuaBase",
    "FotoOrangtuaResponse",
    "SantriOrangtuaBase",
    "SantriOrangtuaCreate",
    "SantriOrangtuaUpdate",
    "SantriOrangtuaResponse",
    "SantriOrangtuaListResponse",
    "FotoAssetBase",
    "FotoAssetResponse",
    "SantriAssetBase",
    "SantriAssetCreate",
    "SantriAssetUpdate",
    "SantriAssetResponse",
    "SantriAssetListResponse",
    "SantriBansosBase",
    "SantriBansosCreate",
    "SantriBansosUpdate",
    "SantriBansosResponse",
    "SantriKesehatanBase",
    "SantriKesehatanCreate",
    "SantriKesehatanUpdate",
    "SantriKesehatanResponse",
    "SantriPembiayaanBase",
    "SantriPembiayaanCreate",
    "SantriPembiayaanUpdate",
    "SantriPembiayaanResponse",
    "SantriSkorResponse",
]
