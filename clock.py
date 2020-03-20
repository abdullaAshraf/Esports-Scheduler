import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from task import updatePlayers


sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def update_players():
    print('This job is run every one minutes.')
    return
    succeeded = updatePlayers()
    if succeeded:
        logging.info({"message": "done"})
    else:
        logging.error({"message": "error updating players"})


sched.start()