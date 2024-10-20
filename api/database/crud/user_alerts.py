from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from api.database.crud.base import CRUDBase
from api.database.models.warframe.tracking import UserOrderAlertsModel
from api.routers.schemas.user_alerts import UserAlertCreate, UserAlertUpdate


class UserAlertsCRUD(CRUDBase[UserOrderAlertsModel, UserAlertCreate, UserAlertUpdate]):
    async def get_all(self, db: AsyncSession, *, limit: int, offset: int) -> Sequence[UserOrderAlertsModel]:
        return await self.select_all(db, limit=limit, offset=offset)

    async def create(self, db: AsyncSession, *, obj: UserAlertCreate) -> UserOrderAlertsModel:
        return await self.create_(db, obj=obj)

    async def delete(self, db: AsyncSession, *, pk: list[int]) -> int:
        return await self.delete_(db, filters=self.model.id.in_(pk))


user_alerts_dao = UserAlertsCRUD(UserOrderAlertsModel)
