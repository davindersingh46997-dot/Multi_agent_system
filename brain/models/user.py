from datetime import datetime
from sqlalchemy import DateTime,Integer,String
from sqlalchemy.orm import Mapped,MappedColumn

from brain.database.session import Base


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = MappedColumn(
        Integer,
        primary_key = True,
        index = True
    )

    # Username : Mapped[str | None] = MappedColumn(
    #     String(20),
    #     unique = True,
    #     nullable = True,
    # )

    email : MappedColumn[str | None] = MappedColumn(
        String(255),
        unique = True,
        nullable = True,
        index = True
    )

    password_hash : Mapped[str] = MappedColumn(
        String(255),
        nullable = False
    )

    created_at : Mapped[datetime] = MappedColumn(
        DateTime,
        default = datetime.utcnow,
        nullable = False
    )