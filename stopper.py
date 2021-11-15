import paramiko
import time
import requests

hosts = ['192.168.31.90', '192.168.31.62', '192.168.31.250', '192.168.31.220']
usernames = ['andrey', 'andrey', 'dev', 'andrey']
slave_name_template = 'slave-test-'

ssh = paramiko.SSHClient()
index = 0
for host, username in zip(hosts, usernames):
    print(host)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password='2718281828')
    ssh.exec_command("docker ps | awk '/andrey21and*/{print $1}' | xargs docker stop")
    time.sleep(1)

with open('urls.txt', 'r') as f:
    lines = f.read().split('\n')[:-1]
    ips = []
    for line in lines:
        ips.append(line.split(', ')[1])
    print(ips)


for index, host in enumerate(ips):
    slave_name = slave_name_template + str(index)
    command = 'http://{0}:8500/v1/agent/service/deregister/{1}'.format(host, slave_name)
    requests.put(command)
