import requests
import time
import subprocess
import matplotlib.pyplot as plt


def get_data(size):
    process = subprocess.Popen(['python', 'master_kommy.py', '--size', str(size)], stdout=subprocess.PIPE)
    time.sleep(1)
    response = requests.get('http://127.0.0.1:8080/')
    process.kill()
    print(response.json()['correct'])
    return response.json()['work_time_1'], response.json()['work_time_2']


size_list = []
serial_times = []
parallel_times = []

for i in range(3, 13):
    size_list.append(i)
    serial, parallel = get_data(i)
    serial_times.append(serial)
    parallel_times.append(parallel)

plt.plot(size_list, serial_times, label='Serial')
plt.plot(size_list, parallel_times, label='Parallel')
plt.legend()
plt.show()
