import consul
from dns import resolver
import requests
import numpy
import time
import sys
import grequests
import itertools
import argparse
from flask import Flask, jsonify

app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('--size')
args = parser.parse_args()

MATRIX_SIZE = int(args.size)

URLS_FILE = '../urls.txt'


def post(name, data, endpoint=None, parallel=True):
    url = get_url(name, endpoint)
    print(url)
    if parallel:
        return grequests.post(url, json=data)
    else:
        return requests.post(url, json=data)


def get(name, endpoint=None, parallel=True):
    url = get_url(name, endpoint)
    if parallel:
        return grequests.get(url)
    else:
        return requests.get(url)


def get_url(name, endpoint):
    consul_resolver = resolver.Resolver()
    consul_resolver.port = 8600
    consul_resolver.nameservers = ['127.0.0.1']
    service_name = name.split('http://')[1].split(':')[0]
    port = name.split(':')[2]
    hosts = consul_resolver.resolve(service_name, 'A')
    ips = []
    for ip in hosts:
        ips.append(ip)
    url = 'http://' + str(ips[0]) + ':' + port
    if endpoint is not None:
        url += endpoint
    return url


def parse_urls():
    urls = []
    with open(URLS_FILE, 'r') as f:
        lines = f.read().split('\n')[:-1]
        for line in lines:
            urls.append(line.split(', ')[0])
    return urls


def prepare():
    matrix = numpy.random.randint(10, 15, (MATRIX_SIZE, MATRIX_SIZE))
    for i in range(MATRIX_SIZE):
        for j in range(MATRIX_SIZE):
            if i == j:
                matrix[i, j] = 0
    return matrix


def calc_variant_dist(variant, matrix):
    route = [0, *variant, 0]
    dist = 0
    for i in range(1, len(route)):
        dist += matrix[route[i - 1], route[i]]
    return dist


def solve_serial(matrix):
    start = [i for i in range(1, MATRIX_SIZE)]
    total_variants = itertools.permutations(start, MATRIX_SIZE - 1)
    min_dist = sys.maxsize
    min_route = []
    for variant in total_variants:
        current_dist = calc_variant_dist(variant, matrix)
        if current_dist < min_dist:
            min_dist = current_dist
            min_route = variant
    return int(min_dist), [0, *min_route, 0]


def broadcast_tasks(matrix, urls):
    broadcast_requests = []
    used_urls = []
    for i in range(MATRIX_SIZE - 1):
        data = {
            'matrix': matrix.tolist(),
            'start_city': i + 1
        }
        broadcast_requests.append(post(urls[i], data=data, endpoint='/task'))
        used_urls.append(urls[i])
    responses = grequests.map(broadcast_requests)
    print(responses)
    return used_urls


def solve_parallel(matrix):
    urls = parse_urls()
    start_broadcast_time = time.time()
    used_urls = broadcast_tasks(matrix, urls)
    print('Broadcast time: ' + str(time.time() - start_broadcast_time))
    solve_requests = []
    for url in used_urls:
        solve_requests.append(get(url, endpoint='/solve'))
    solve_responses = grequests.map(solve_requests)
    print(solve_responses)
    distances = []
    routes = []
    for solve in solve_responses:
        distances.append(solve.json()['min_dist'])
        routes.append(solve.json()['min_route'])
    min_dist_index = numpy.argmin(distances)
    return int(distances[min_dist_index]), routes[min_dist_index]


@app.route('/', methods=['GET'])
def test():
    matrix = prepare()
    print('Start serial solve')
    start_time_serial = time.time()
    min_dist_serial, min_route_serial = solve_serial(matrix)
    work_time_1 = time.time() - start_time_serial
    print('End serial solve')

    print('Start parallel solve')
    start_time_parallel = time.time()
    min_dist_parallel, min_route_parallel = solve_parallel(matrix)
    work_time_2 = time.time() - start_time_parallel
    print('End parallel solve')

    print(min_dist_serial, min_dist_parallel)
    print(min_route_serial, min_route_parallel)

    correct = (int(min_dist_serial) == int(min_dist_parallel)) and (len(min_route_serial) == len(min_route_parallel))
    if correct:
        print('Checking routes')
        for i in range(len(min_route_serial)):
            correct &= min_route_serial[i] == min_route_parallel[i]
    return jsonify({'work_time_1': work_time_1, 'work_time_2': work_time_2, 'correct': correct})


if __name__ == '__main__':
    from gevent import monkey

    monkey.patch_all()
    consul = consul.Consul()

    consul.agent.service.register('test-master', port=8080)
    print(consul.agent.services())

    app.run('0.0.0.0', 8080)
    consul.agent.service.deregister(service_id='test-master')
