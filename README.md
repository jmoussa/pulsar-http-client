# Alfred Pulsar Notification RestAPI

This is an attempt at establishing a customizable notification service on top of Apache Pulsar and hopefully set up an API with FastAPI.

## Dependencies

### Docker Container Running Pulsar :

```bash
docker run -it \
  -p 6650:6650 \
  -p 8080:8080 \
  --mount source=pulsardata,target=/pulsar/data \
  --mount source=pulsarconf,target=/pulsar/conf \
  apachepulsar/pulsar:2.7.0 \
  bin/pulsar standalone
```
