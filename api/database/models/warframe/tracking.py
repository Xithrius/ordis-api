from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UUID, BigInteger, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import now

from api.database.base import Base

if TYPE_CHECKING:
    from api.database.models.warframe.items import WarframeItemModel


class UserOrderAlertsAssociationModel(Base):
    __tablename__ = "user_order_alerts_association"

    user_order_alert_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_order_notifications.id"),
        primary_key=True,
    )
    warframe_market_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("warframe_market_orders.id"),
        primary_key=True,
    )


class UserOrderAlertsModel(Base):
    """Users to be notified when an order hits a specific price threshold."""

    __tablename__ = "user_order_notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    orders: Mapped[list[WarframeMarketOrderModel]] = relationship(
        secondary="user_order_alerts_association",
        back_populates="notify_users",
        lazy="joined",
    )


class WarframeMarketOrderModel(Base):
    """
    Keeping track of what users have ordered.

    Once an item reaches a certain price and minimum quantity, then users will be pinged.
    """

    __tablename__ = "warframe_market_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=now(),
        onupdate=now(),
    )

    # Whoever initially created this order
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Once the item goes below this platinum amount, alert the user
    platinum_threshold: Mapped[int] = mapped_column(Integer, nullable=False)

    # How many items the user wants available in one order
    minimum_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Which item we're tracking -- it has to exist, of course
    item_id: Mapped[str] = mapped_column(ForeignKey("warframe_items.id"))
    item: Mapped[WarframeItemModel] = relationship(
        "WarframeItemModel",
        back_populates="orders",
        lazy="joined",
    )

    # Who else to ping when this order happens
    notify_users: Mapped[list[UserOrderAlertsModel]] = relationship(
        secondary="user_order_alerts_association",
        back_populates="orders",
        lazy="joined",
    )


# class WarframeMarketTrackingOrderModel(Base):
#     """Keeping track of an item's price over time, during the span of an order from a user."""

#     __tablename__ = "warframe_market_tracked_orders"

#     id: Mapped[str] = mapped_column(Text, ForeignKey("warframe_items.id"), primary_key=True)

#     user_id: Mapped[int] = mapped_column(Integer, nullable=False)
#     platinum: Mapped[int] = mapped_column(Integer, nullable=False)
#     quantity: Mapped[int] = mapped_column(Integer, nullable=False)

#     item: Mapped[WarframeItemModel] = relationship("WarframeItemModel", lazy="joined")
