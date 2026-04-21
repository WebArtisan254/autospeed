import time
from flask import current_app

class TaskTimer:
    def __init__(self, name: str, job_id: str):
        self.name = name
        self.job_id = job_id
        self.start = time.time()

    def __enter__(self):
        current_app.logger.info("Task start %s job=%s", self.name, self.job_id)
        return self
    
    def __exit__(self, exc_type, exc, tb):
        dur = int((time.time() - self.start) * 1000)
        if exc_type:
            current_app.logger.exception("Task failed %s job=%s dur_ms=%s", self.name, self.job_id, dur)
        else:
            current_app.logger.info("Task done %s job=%s dur_ms=%s", self.name, self.job_id, dur)