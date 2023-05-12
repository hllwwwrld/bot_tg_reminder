from func_for_scheduler import Reminds
import schedule
from multiprocessing import *


reminds = Reminds()


def start_process():  # Запуск Process
    Process(target=ScheduleInfinite.start_schedule, args=()).start()


class ScheduleInfinite:

    def start_schedule():
        schedule.every(1).day.at('00:00').do(reminds.remind_dates)
        schedule.every(1).hour.at(':00').do(reminds.remind_hours)

        print(schedule.get_jobs())

        for job in schedule.get_jobs():
            print(job)

        while True:
            schedule.run_pending()
