import time
from .client import Client
from .types import TaskPayload, Task, PollOptions

class CrawlbyteSDK:
    def __init__(self, api_key: str):
        self.client = Client("https://api.crawlbyte.ai/api", api_key)

    async def create_task(self, payload: TaskPayload) -> Task:
        return await self.client.do_request("POST", "/tasks", payload)

    async def get_task(self, task_id: str) -> Task:
        return await self.client.do_request("GET", f"/tasks/{task_id}")

    async def poll_task(self, task_id: str, opts: PollOptions) -> Task:
        interval = opts.interval_seconds
        timeout = opts.timeout_seconds
        deadline = time.time() + timeout

        while True:
            task = await self.get_task(task_id)
            if task["status"] in ["completed", "failed"]:
                return task

            if time.time() > deadline:
                raise TimeoutError(f"Timeout reached while polling task {task_id}")

            time.sleep(interval)
