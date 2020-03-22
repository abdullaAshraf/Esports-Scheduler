import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from task import updatePlayers


sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=60)
def update_players():
    succeeded = updatePlayers()
    if succeeded:
        logging.info({"message": "done"})
    else:
        logging.error({"message": "error updating players"})


sched.start()