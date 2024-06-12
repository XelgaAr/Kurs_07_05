import logging
import multiprocessing
import threading
import time
from multiprocessing import Process

def action_function(num_start, num_end, name):
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.info(f"{name}: starting")
    count = 0
    for i in range(int(num_start), int(num_end)):
        string = str(i)
        number_len = int(len(string) / 2)
        first_part = string[0:number_len]
        second_part = string[number_len + 1:len(string)]
        first_sum = sum(int(i) for i in first_part)
        second_sum = sum(int(i) for i in second_part)
        if first_sum == second_sum:
            count += 1
    logging.info(f"{name} finishing, start {int(num_start)}, end {int(num_end)}, count {count} ")


if __name__ == "__main__":
    mim_number = 0
    max_number = 99999999
    divider = 4
    num1 = max_number / divider

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    for i in range(1, divider + 1):
        left_num = (i - 1) * num1
        right_num = left_num + num1
        x = threading.Thread(target=action_function, args=(left_num, right_num, f"Thread {i}"))
        x.start()

    for i in range(1, divider + 1):
        left_num = (i - 1) * num1
        right_num = left_num + num1
        y = Process(target=action_function, args=(left_num, right_num, f"Process {i}"))
        y.start()

    logging.info("End of code")
