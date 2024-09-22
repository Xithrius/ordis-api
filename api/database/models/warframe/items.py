from __future__ import annotations

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from api.database.base import Base


class WarframeItemModel(Base):
    __tablename__ = "warframe_items"

    id: Mapped[str] = mapped_column(Text, primary_key=True)

    thumb: Mapped[str] = mapped_column(Text, nullable=False)
    item_name: Mapped[str] = mapped_column(Text, nullable=False)
    url_name: Mapped[str] = mapped_column(Text, nullable=False)
