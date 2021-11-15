FROM andrey21and/consul-python-base
COPY slave.py ./app
WORKDIR ./app
EXPOSE 5000
CMD ["python", "slave.py"]