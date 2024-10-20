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
