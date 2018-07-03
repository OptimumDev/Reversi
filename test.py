import threading
import datetime
from multiprocessing import Pool

numbers = 40000000

def one_thread():
    time = datetime.datetime.now() 
    print(sum([i for i in range(numbers)]))
    print(datetime.datetime.now() - time)


summary = []
def get_sum(start, end):
    summary.append(sum([i for i in range(start, end)]))

threads = []
def four_threads():
    time = datetime.datetime.now() 
    for i in range(4):
        j = i
        thread = threading.Thread(target=get_sum, args=(j * numbers // 4, (j + 1) * numbers // 4))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    print(sum(summary))
    print(datetime.datetime.now() - time)

def four_processes():
    summary = []
    time = datetime.datetime.now()
    p= Pool(4)
    p.map(get_sum, [(j * numbers // 4, (j + 1) * numbers // 4) for j in range(4)])
    p.close()
    p.join()
    print(sum(summary))
    print(datetime.datetime.now() - time)

one_thread()

print('===========================')

four_threads()

print('===========================')

four_processes()