import paramiko
import time

hosts = [('192.168.31.90', 4), ('192.168.31.62', 4), ('192.168.31.250', 0), ('192.168.31.220', 3)]
usernames = ['andrey', 'andrey', 'dev', 'andrey']
image_name = 'andrey21and/consul-slave-kommy-go'

ssh = paramiko.SSHClient()
index = 0
urls = []
for host, username in zip(hosts, usernames):
    print(host)
    ip = host[0]
    replicas = host[1]
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip, username=username, password='2718281828')
    current_port = 5000
    for i in range(replicas):
        name = 'slave-test-' + str(index)
        urls.append(('http://' + name + '.service.consul' + ':' + str(current_port), ip))
        command = "docker run -d -p {0}:5000 -e CONSUL_HOST='{1}' -e NAME='{2}' " \
                  "--cpuset-cpus={3} {4}".format(current_port, ip, name, str(i), image_name)
        index += 1
        current_port += 1
        print(command)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
        print(ssh_stdout.read())
        print(ssh_stderr.read())

    time.sleep(3)
    ssh.close()

with open('urls.txt', 'w') as f:
    output = ""
    for url in urls:
        output += url[0] + ', ' + url[1] + '\n'
    f.write(output)
