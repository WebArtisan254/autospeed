import time
from datetime import datetime, timedelta, timezone
from rq import Retry
from autospeed import create_app
from autospeed.jobs import get_queue

INTERVAL = 3600

def main():
    app = create_app()
    q = get_queue()

    next_run = datetime.now(timezone.utc)

    while True:
        now = datetime.now(timezone.utc)
        if now >= next_run:
            with app.app_context():
                q.enqueue(
                    "autospeed.tasks.maintenance.cleanup_expired_tokens_and_stale_email",
                    retry=Retry(max=1),
                )
                next_run = now + timedelta(seconds=INTERVAL)

        time.sleep(10)

if __name__ == "__main__":
    main()
