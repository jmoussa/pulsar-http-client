# Alfred Pulsar Notification RestAPI

This repo establishes a customizable notification service on top of Apache Pulsar and is able to be interacted with via FastAPI.

## To Run

### Required: Docker Container Running Pulsar

```bash
docker run -it \
  -p 6650:6650 \
  -p 8080:8080 \
  --mount source=pulsardata,target=/pulsar/data \
  --mount source=pulsarconf,target=/pulsar/conf \
  apachepulsar/pulsar:2.7.0 \
  bin/pulsar standalone
```

### Running

```bash
conda env create -f environment.yml
conda activate pulsar
python setup.py develop
cd alfred/
cp config.template.py config.py
# Fill in env variables here
./run
