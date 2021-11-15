FROM andrey21and/consul-python-base
COPY slave_kommy.py ./app
WORKDIR ./app
EXPOSE 5000
CMD ["python", "slave_kommy.py"]