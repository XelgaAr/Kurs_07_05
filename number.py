import logging
from threading import Thread
from multiprocessing import Process

logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")


def action_function(num_start, num_end, digits_len, name):
    logging.info(f"Started {name}")
    count = 0
    number_len = digits_len // 2

    for num in range(num_start, num_end):
        string = str(num).zfill(digits_len)
        left_str = string[:number_len]
        right_str = string[number_len:]

        left_sum = sum(int(j) for j in left_str)
        right_sum = sum(int(j) for j in right_str)
        if left_sum == right_sum:
            count += 1

    logging.info(f"Finishing {name}, start {num_start}, end {num_end}, count {count}")


if __name__ == "__main__":
    max_number = 99999999
    divider = 4
    part = (max_number + 1) // divider
    length = len(str(max_number))

    for i in range(divider):
        left_num = i * part
        right_num = ((i + 1) * part) - 1

        t = Thread(target=action_function, args=(left_num, right_num, length, f"Thread {i + 1}"))
        t.start()

        p = Process(target=action_function, args=(left_num, right_num, length, f"Process {i + 1}"))
        p.start()
