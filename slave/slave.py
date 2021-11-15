import consul
import os
import numpy
import datetime
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

matrix = None
vector = None


@app.route('/', methods=['POST'])
def test():
    receive_datetime = datetime.datetime.now().time()
    data = request.json
    k = numpy.array(data['k'])
    vector = numpy.array(data['vector'])
    block_size = vector.size
    matrix = numpy.linspace(0, 1, block_size ** 2).reshape((block_size, block_size)) * k
    res = numpy.matmul(numpy.linalg.inv(matrix), vector)
    end_time = datetime.datetime.now().time()
    return jsonify({'res': res.tolist(), 'name': os.environ['NAME'], 'start': str(receive_datetime),
                    'end': str(end_time)})


@app.route('/matrix', methods=['POST'])
def set_matrix():
    global matrix, vector
    matrix = numpy.array(request.json['matrix'])
    vector = numpy.array(request.json['vector'])
    return jsonify({'res': True})


@app.route('/solve', methods=['GET'])
def solve():
    global matrix, vector
    receive_datetime = datetime.datetime.now().time()
    if (matrix is not None) and (vector is not None):
        res = numpy.matmul(numpy.linalg.inv(matrix), vector)
    else:
        abort(500)
        return
    end_time = datetime.datetime.now().time()
    return jsonify({'res': res.tolist(), 'name': os.environ['NAME'], 'start': str(receive_datetime),
                    'end': str(end_time)})


if __name__ == '__main__':
    consul = consul.Consul(host=os.environ['CONSUL_HOST'])
    name = os.environ['NAME']
    consul.agent.service.register(name, port=5000)
    print(consul.agent.services())

    app.run('0.0.0.0', 5000)
    consul.agent.service.deregister(service_id=name)
