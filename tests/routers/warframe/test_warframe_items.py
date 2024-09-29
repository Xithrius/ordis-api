from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

FAKE_ITEM_LIST: list[dict[str, str]] = [
    {
        "id": "54aae292e7798909064f1575",
        "item_name": "Secura Dual Cestra",
        "thumb": "items/images/en/thumbs/secura_dual_cestra.3d47a4ec6675ff774bb0da9b16c53e0e.128x128.png",
        "url_name": "secura_dual_cestra",
    },
]


class MockWarframeItems:
    @pytest.fixture(autouse=True)
    async def mock_get_all_warframe_items(self) -> AsyncGenerator[None, Any]:
        with patch("api.routers.warframe.items.get_all_warframe_items", new_callable=AsyncMock) as mocked_func:
            mocked_func.return_value = FAKE_ITEM_LIST
            yield

    async def sync_items_helper(self, client: AsyncClient, fastapi_app: FastAPI) -> dict[str, int]:
        url = fastapi_app.url_path_for("sync_items")

        response = await client.get(url)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        return data


class TestWarframeItemAPI(MockWarframeItems):
    async def test_sync_items_empty_database_returns_correct_length(
        self,
        client: AsyncClient,
        fastapi_app: FastAPI,
    ) -> None:
        data = await self.sync_items_helper(client, fastapi_app)
        assert data["new"] == len(FAKE_ITEM_LIST)

    async def test_sync_items_called_twice_returns_zero_new_items(
        self,
        client: AsyncClient,
        fastapi_app: FastAPI,
    ) -> None:
        # Database is empty, amount of items should be how many `FAKE_ITEM_LIST` has.
        data = await self.sync_items_helper(client, fastapi_app)
        assert data["new"] == len(FAKE_ITEM_LIST)

        # Second call should conflict with current items, so no new are added.
        data = await self.sync_items_helper(client, fastapi_app)
        assert data["new"] == 0

    async def test_get_all_items_in_empty_database_returns_empty_list(
        self,
        client: AsyncClient,
        fastapi_app: FastAPI,
    ) -> None:
        url = fastapi_app.url_path_for("get_all_items")

        response = await client.get(url)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data == []

    async def test_get_all_items_after_sync_returns_item(
        self,
        client: AsyncClient,
        fastapi_app: FastAPI,
    ) -> None:
        data = await self.sync_items_helper(client, fastapi_app)
        assert data["new"] == len(FAKE_ITEM_LIST)

        url = fastapi_app.url_path_for("get_all_items")

        response = await client.get(url)

        assert response.status_code == status.HTTP_200_OK

        all_items = response.json()

        assert data["new"] == len(all_items)
        assert all_items == FAKE_ITEM_LIST

    async def test_get_item_by_fuzzy_item_on_empty_database_returns_404(
        self,
        client: AsyncClient,
        fastapi_app: FastAPI,
    ) -> None:
        url = fastapi_app.url_path_for("get_item_by_fuzzy")

        search = {"search": FAKE_ITEM_LIST[0]["item_name"]}
        response = await client.get(url, params=search)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_item_by_fuzzy_after_sync_with_invalid_search_returns_404(
        self,
        client: AsyncClient,
        fastapi_app: FastAPI,
    ) -> None:
        data = await self.sync_items_helper(client, fastapi_app)
        assert data["new"] == len(FAKE_ITEM_LIST)

        url = fastapi_app.url_path_for("get_item_by_fuzzy")

        search = {"search": "asdfasdfasdf"}
        response = await client.get(url, params=search)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_item_by_fuzzy_after_sync_returns_item(
        self,
        client: AsyncClient,
        fastapi_app: FastAPI,
    ) -> None:
        data = await self.sync_items_helper(client, fastapi_app)
        assert data["new"] == len(FAKE_ITEM_LIST)

        url = fastapi_app.url_path_for("get_item_by_fuzzy")

        search = {"search": FAKE_ITEM_LIST[0]["item_name"]}
        response = await client.get(url, params=search)

        assert response.status_code == status.HTTP_200_OK

        queried_item = response.json()

        assert queried_item == FAKE_ITEM_LIST[0]

    async def test_get_item_in_empty_database_returns_404(
        self,
        client: AsyncClient,
        fastapi_app: FastAPI,
    ) -> None:
        url = fastapi_app.url_path_for("get_item", item_id=FAKE_ITEM_LIST[0]["id"])

        response = await client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_item_after_sync_with_invalid_search_returns_404(
        self,
        client: AsyncClient,
        fastapi_app: FastAPI,
    ) -> None:
        data = await self.sync_items_helper(client, fastapi_app)
        assert data["new"] == len(FAKE_ITEM_LIST)

        url = fastapi_app.url_path_for("get_item", item_id="asdfasdfasdf")

        response = await client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_item_after_sync_returns_item(
        self,
        client: AsyncClient,
        fastapi_app: FastAPI,
    ) -> None:
        data = await self.sync_items_helper(client, fastapi_app)
        assert data["new"] == len(FAKE_ITEM_LIST)

        url = fastapi_app.url_path_for("get_item", item_id=FAKE_ITEM_LIST[0]["id"])

        response = await client.get(url)

        assert response.status_code == status.HTTP_200_OK

        queried_item = response.json()

        assert queried_item == FAKE_ITEM_LIST[0]
