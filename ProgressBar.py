import sys
import time


def progress_bar(str,finish_tasks_number, tasks_number):
    percentage = round(finish_tasks_number / tasks_number * 100)
    print("\r"+str+" {}%: ".format(percentage), "▓" * (percentage // 2), end="")
    sys.stdout.flush()


