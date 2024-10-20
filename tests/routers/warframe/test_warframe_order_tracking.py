from typing import Any

from fastapi import FastAPI, status
from httpx import AsyncClient

from tests.routers.warframe.utils import FAKE_ITEM_LIST, MockWarframeItems


class TestWarframeOrderTrackingAPI(MockWarframeItems):
    async def test_create_one_order_tracker_after_sync_with_notify_list_returns_400_bad_request(
        self,
        client: AsyncClient,
        fastapi_app: FastAPI,
    ) -> None:
        data = await self.sync_items_helper(client, fastapi_app)
        assert data["new"] == len(FAKE_ITEM_LIST)

        url = fastapi_app.url_path_for("create_order_tracker")
        payload: dict[str, Any] = {
            "user_id": 1234,
            "platinum_threshold": 1,
            "minimum_quantity": 1,
            "item_id": FAKE_ITEM_LIST[0]["id"],
            "notify_users": [1111111111111111],
        }

        response = await client.post(url, json=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_create_one_order_tracker_after_sync_returns_201_created(
        self,
        client: AsyncClient,
        fastapi_app: FastAPI,
    ) -> None:
        item_list = await self.sync_items_helper(client, fastapi_app)
        assert item_list["new"] == len(FAKE_ITEM_LIST)

        url = fastapi_app.url_path_for("create_order_tracker")
        payload: dict[str, Any] = {
            "user_id": 1234,
            "platinum_threshold": 1,
            "minimum_quantity": 1,
            "item_id": FAKE_ITEM_LIST[0]["id"],
        }

        response = await client.post(url, json=payload)

        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()

        assert data

        assert data["created_at"]
        assert data["updated_at"]
        assert data["notify_users"] == []
        for k, v in payload.items():
            assert data[k] == v
