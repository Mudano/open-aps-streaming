from ingester.scheduler import app_scheduler
from datetime import datetime
import os


def test():
    time = datetime.now()
    print(f'schedule test running at {time}')


if __name__ == '__main__':
    print(f'{datetime.now()} - Scheduled Nightscout ingester is starting up.')

    app_scheduler.add_job(test, 'interval', seconds=5, id='1', replace_existing=True)
    exit_key = 'Break' if os.name == 'nt' else 'C'
    print(f'Press Ctrl+{exit_key} to exit')

    try:
        app_scheduler.start()
    except (KeyboardInterrupt, SystemExit) as e:
        print(f'and exception was encountered whilst running the scheduler: {e}')
        pass
else:
    print('why am I not main?')
