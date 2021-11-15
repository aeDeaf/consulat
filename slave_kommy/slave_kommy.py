import consul
import os
import numpy
import sys
import datetime
import itertools
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

matrix = numpy.empty(0)
start_city = 0


def calc_variant_dist(variant):
    global matrix, start_city
    route = [0, start_city, *variant, 0]
    dist = 0
    for i in range(1, len(route)):
        dist += matrix[route[i - 1], route[i]]
    return dist


@app.route('/task', methods=['POST'])
def set_task():
    global matrix, start_city
    matrix = numpy.array(request.json['matrix'])
    start_city = request.json['start_city']
    return jsonify({'res': 'OK'})


@app.route('/solve', methods=['GET'])
def solve():
    global matrix, start_city
    matrix_size = matrix.shape[0]
    start = [i for i in range(1, matrix_size)]
    start.remove(start_city)
    total_variants = itertools.permutations(start, matrix_size - 2)
    min_dist = sys.maxsize
    min_route = []
    for variant in total_variants:
        current_dist = calc_variant_dist(variant)
        if current_dist < min_dist:
            min_dist = current_dist
            min_route = variant
    return jsonify({'min_dist': int(min_dist),
                    'min_route': [0, start_city, *min_route, 0]})


if __name__ == '__main__':
    consul = consul.Consul(host=os.environ['CONSUL_HOST'])
    name = os.environ['NAME']
    consul.agent.service.register(name, port=5000)
    print(consul.agent.services())

    app.run('0.0.0.0', 5000)
    consul.agent.service.deregister(service_id=name)
