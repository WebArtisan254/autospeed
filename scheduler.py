import time 
from datetime import datetime, timedelta
from autospeed import create_app
from autospeed.jobs import get_queue

INTERVAL = 3600

def main():
    app = create_app()
    q = get_queue()

    next_run = datetime.utcnow()

    while True:
        now = datetime.utcnow()
        if now >= next_run:
            with app.app_context():
                q.enqueue(
                    "autospeed.tasks.maintenance.cleanup_expired_tokens_and_stale_email",
                    retry=1,
                )
                next_run = now + timedelta(seconds=INTERVAL)

            time.sleep(10)

if __name__ == "__main__":
    main()