import uuid
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class UUIDBase(Base):
    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
