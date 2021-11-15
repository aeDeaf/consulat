import consul
from dns import resolver
import requests
import numpy
import time
import grequests
from flask import Flask, jsonify

app = Flask(__name__)

BLOCK_SIZE = 5000
TOTAL_BLOCKS = 3
MATRIX_SIZE = BLOCK_SIZE * TOTAL_BLOCKS


def post(name, data):
    consul_resolver = resolver.Resolver()
    consul_resolver.port = 8600
    consul_resolver.nameservers = ['127.0.0.1']
    hosts = consul_resolver.resolve(name + '.service.consul', 'A')
    ips = []
    for ip in hosts:
        ips.append(ip)
    return grequests.post('http://' + str(ips[0]) + ':5000/', json=data)


@app.route('/', methods=['GET'])
def test():
    app.logger.error('Total blocks: ' + str(TOTAL_BLOCKS))
    app.logger.error('Block size: ' + str(BLOCK_SIZE))
    blocks = []
    vector_blocks = []
    vector = numpy.random.uniform(0, 1, MATRIX_SIZE)
    for index in range(TOTAL_BLOCKS):
        blocks.append(numpy.random.uniform(0, 1, (BLOCK_SIZE, BLOCK_SIZE)))
        vector_blocks.append(vector[index * BLOCK_SIZE:(index + 1) * BLOCK_SIZE])

    start_time = time.time()
    res = []
    for index, block in enumerate(blocks):
        vector_block = vector[index * BLOCK_SIZE:(index + 1) * BLOCK_SIZE]
        res.extend(numpy.matmul(numpy.linalg.inv(block), vector_block))
    res = numpy.array(res)
    work_time_1 = time.time() - start_time

    urls = ['slave-test-0', 'slave-test-1', 'slave-test-3']
    app.logger.error(str(urls))
    requests_list = []

    for index, block in enumerate(blocks):
        url = urls[index]
        vector_block = vector_blocks[index]
        data = {'matrix': block.tolist(), 'vector': vector_block.tolist()}
        requests_list.append(post(url, data))

    app.logger.error(str(requests_list))
    start_time2 = time.time()

    responses = grequests.map(requests_list, size=TOTAL_BLOCKS)
    res2 = numpy.zeros_like(res)
    app.logger.error(str(responses))
    for index, response in enumerate(responses):
        data = response.json()
        app.logger.error('Start time for index' + str(index) + ': ' + data['start'] + '; end time: ' + data['end'])
        res2[index * BLOCK_SIZE:(index + 1) * BLOCK_SIZE] = data['res']
    work_time_2 = time.time() - start_time2

    delta = numpy.abs(res - numpy.array(res2))
    app.logger.error(str(res2))
    correct = str(numpy.all(delta < 1e-5))

    return jsonify({'work_time_1': work_time_1, 'work_time_2': work_time_2, 'correct': correct})


if __name__ == '__main__':
    from gevent import monkey

    monkey.patch_all()
    consul = consul.Consul()

    consul.agent.service.register('test-master', port=8080)
    print(consul.agent.services())

    app.run('0.0.0.0', 8080)
    consul.agent.service.deregister(service_id='test-master')
