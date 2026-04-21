from rq import Worker
from autospeed import create_app
from autospeed.jobs import get_redis

def main():
    app = create_app()
    redis_conn = get_redis()
    worker = Worker(["autospeed"], connection=redis_conn)

    with app.app_context():
        worker.work()

if __name__ == "__main__":
    main()