from fastapi import APIRouter, HTTPException, status

from api.database.crud.tracking import order_tracking_dao
from api.database.dependencies import DBSession
from api.database.models.warframe.tracking import WarframeMarketOrderModel
from api.routers.schemas.tracking import Order, OrderCreate

router = APIRouter()


@router.post(
    "/create",
    description="Track the warframe market for an item being sold between thresholds",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
)
async def create_order_tracker(
    session: DBSession,
    track_new_order: OrderCreate,
) -> WarframeMarketOrderModel:
    if track_new_order.notify_users:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Notification of multiple users is currently not supported",
        )

    return await order_tracking_dao.create(session, obj=track_new_order)


# @router.get(
#     "/track/buyers",
#     description="Track the warframe market for an item being bought between thresholds",
#     # response_model=WarframeItemResponse,
#     status_code=status.HTTP_200_OK,
# )
# async def track_item_price_from_buyers(
#     session: DBSession,
#     requested_item: str,
#     lower_threshold: int,
#     upper_thresold: int,
# ) -> None: ...
