from func_for_scheduler import remind_dates
import schedule
from multiprocessing import *


def start_process():  # Запуск Process
    Process(target=ScheduleInfinite.start_schedule, args=()).start()


class ScheduleInfinite:

    def start_schedule():
        schedule.every(1).day.at('00:00').do(remind_dates)

        print(schedule.get_jobs())

        while True:
            schedule.run_pending()
