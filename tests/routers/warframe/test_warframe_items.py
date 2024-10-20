from fastapi import FastAPI, status
from httpx import AsyncClient

from tests.routers.warframe.utils import FAKE_ITEM_LIST, MockWarframeItems


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
