import sys
import time


def progress_bar(text,finish_tasks_number, tasks_number):
    percentage = round(finish_tasks_number / tasks_number * 100)
    num = round(finish_tasks_number / tasks_number * 50)
    process = "\r"+text+" %3s%%: |%-50s |" % (percentage, '▊' * num)
    print(process, end='', flush=True)


