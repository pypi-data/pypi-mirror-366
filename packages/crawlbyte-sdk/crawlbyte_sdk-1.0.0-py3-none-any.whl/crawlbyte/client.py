import httpx
from typing import Any

class Client:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.session = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": api_key,
                "Content-Type": "application/json"
            },
            timeout=20
        )

    async def do_request(self, method: str, endpoint: str, data: Any = None) -> Any:
        try:
            response = await self.session.request(
                method=method.upper(),
                url=endpoint,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Request failed: {str(e)}")
