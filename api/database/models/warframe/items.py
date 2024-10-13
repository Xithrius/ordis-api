from __future__ import annotations

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.base import Base
from api.database.models.warframe.tracking import WarframeMarketOrderModel


class WarframeItemModel(Base):
    """All of the available items currently in the game."""

    __tablename__ = "warframe_items"

    id: Mapped[str] = mapped_column(Text, primary_key=True)

    item_name: Mapped[str] = mapped_column(Text, nullable=False)

    # Partial URL path for the thumbnail image
    thumb: Mapped[str] = mapped_column(Text, nullable=False)

    # The item's name that can be used in a URL
    url_name: Mapped[str] = mapped_column(Text, nullable=False)

    orders: Mapped[list[WarframeMarketOrderModel]] = relationship(
        "WarframeMarketOrderModel",
        back_populates="item",
        lazy="joined",
    )
