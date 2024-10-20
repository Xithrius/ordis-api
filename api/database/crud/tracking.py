from sqlalchemy.ext.asyncio import AsyncSession

from api.database.crud.base import CRUDBase
from api.database.models.warframe.tracking import WarframeMarketOrderModel
from api.routers.schemas.tracking import OrderCreate, OrderUpdate


class OrderTrackingCRUD(CRUDBase[WarframeMarketOrderModel, OrderCreate, OrderUpdate]):
    async def get_by_user_id(self, db: AsyncSession, *, user_id: int) -> WarframeMarketOrderModel | None:
        return await self.select_first_(db, filters=self.model.user_id == user_id)

    async def create(self, db: AsyncSession, *, obj: OrderCreate) -> WarframeMarketOrderModel:
        return await self.create_(db, obj=obj)

    async def delete(self, db: AsyncSession, *, pk: list[int]) -> int:
        return await self.delete_(db, filters=self.model.user_id.in_(pk))


order_tracking_dao = OrderTrackingCRUD(WarframeMarketOrderModel)
