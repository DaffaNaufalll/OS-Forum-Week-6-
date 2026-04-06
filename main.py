import threading
import random

print("Program started")


LOWER_NUM = 1
UPPER_NUM = 10000
BUFFER_SIZE = 100
MAX_COUNT = 10000

buffer = []

lock = threading.Lock()
not_full = threading.Condition(lock)
not_empty = threading.Condition(lock)

producer_done = False

# Buffered writes
all_data = []
even_data = []
odd_data = []


def producer():
    global producer_done

    for _ in range(MAX_COUNT):
        num = random.randint(LOWER_NUM, UPPER_NUM)

        with not_full:
            while len(buffer) >= BUFFER_SIZE:
                not_full.wait()

            buffer.append(num)
            all_data.append(f"{num}\n")

            not_empty.notify_all()  

    with lock:
        producer_done = True
        not_empty.notify_all()


def even_consumer():
    while True:
        with not_empty:
            while True:
                if len(buffer) == 0:
                    if producer_done:
                        return
                    not_empty.wait()
                else:
                    num = buffer[-1]
                    if num % 2 == 0:
                        buffer.pop()
                        even_data.append(f"{num}\n")
                        not_full.notify_all()   # wake producer
                        not_empty.notify_all()  # wake other consumer
                        break
                    else:
                        not_empty.wait()


def odd_consumer():
    while True:
        with not_empty:
            while True:
                if len(buffer) == 0:
                    if producer_done:
                        return
                    not_empty.wait()
                else:
                    num = buffer[-1]
                    if num % 2 == 1:
                        buffer.pop()
                        odd_data.append(f"{num}\n")
                        not_full.notify_all()   # wake producer
                        not_empty.notify_all()  # wake other consumer
                        break
                    else:
                        not_empty.wait()


producer_thread = threading.Thread(target=producer)
even_thread = threading.Thread(target=even_consumer)
odd_thread = threading.Thread(target=odd_consumer)

producer_thread.start()
even_thread.start()
odd_thread.start()

producer_thread.join()
even_thread.join()
odd_thread.join()

# Write files in one go (FAST)
with open("all.txt", "w") as f:
    f.writelines(all_data)

with open("even.txt", "w") as f:
    f.writelines(even_data)

with open("odd.txt", "w") as f:
    f.writelines(odd_data)

print("Optimized program finished.")
