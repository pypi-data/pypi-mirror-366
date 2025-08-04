import time
from .client import Client
from .types import TaskPayload, Task, PollOptions

class CrawlbyteSDK:
    def __init__(self, api_key: str):
        self.client = Client("https://api.crawlbyte.ai/api", api_key)

    def create_task(self, payload: TaskPayload) -> Task:  
        return self.client.do_request("POST", "/tasks", payload)  # Remove await

    def get_task(self, task_id: str) -> Task:  
        return self.client.do_request("GET", f"/tasks/{task_id}")  # Remove await

    def poll_task(self, task_id: str, opts: PollOptions) -> Task:  
        interval = opts.interval_seconds
        timeout = opts.timeout_seconds
        deadline = time.time() + timeout

        while True:
            task = self.get_task(task_id)  # Remove await
            if task["status"] in ["completed", "failed"]:
                return task

            if time.time() > deadline:
                raise TimeoutError(f"Timeout reached while polling task {task_id}")

            time.sleep(interval)    
           