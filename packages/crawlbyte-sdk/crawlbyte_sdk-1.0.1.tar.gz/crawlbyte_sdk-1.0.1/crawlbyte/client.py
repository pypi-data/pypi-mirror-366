import httpx
import asyncio
from typing import Any


class Client:
    def __init__(self, base_url: str, api_key: str, retries: int = 5, backoff: float = 1.0):
        self.base_url = base_url
        self.retries = retries
        self.backoff = backoff

        self.session = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": api_key,
                "Content-Type": "application/json"
            },
            timeout=20
        )

    async def do_request(self, method: str, endpoint: str, data: Any = None) -> Any:
        for attempt in range(1, self.retries + 1):
            try:
                response = await self.session.request(
                    method=method.upper(),
                    url=endpoint,
                    json=data
                )
                response.raise_for_status()
                return response.json()

            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                is_retryable = (
                    isinstance(e, httpx.RequestError) or
                    (isinstance(e, httpx.HTTPStatusError) and
                     e.response.status_code in {429, 500, 502, 503, 504})
                )

                if attempt == self.retries or not is_retryable:
                    raise RuntimeError(f"Request failed after {attempt} attempts: {str(e)}")

                print(f"Retrying {method} {endpoint} (attempt {attempt}) due to: {str(e)}!")
                await asyncio.sleep(self.backoff * attempt)
