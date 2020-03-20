import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from task import updatePlayers


sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def fetch_new_posts():
    succeeded = updatePlayers()
    if succeeded:
        logging.info({"message": "done"})
    else:
        logging.error({"message": "error updating players"})


sched.start()