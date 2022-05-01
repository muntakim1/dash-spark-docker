# dash-spark-docker

Spark is a in-memory big data processing tool from apache. Spark is written in Scala. It can perform computation in distributed manner.
PySpark is a framework or modules for python to work with Spark. We are using docker for creating a multicluster spark environment to process about 60M data to calculate median sales value
from 30 years of sales. Those medians will be shown using dashplotly python framework for creating dashboards.

## Requirements.
  1) Understanding in python language
  2) Understanding in linux platform and docker.
  3) Understanding in Big data.
  4) Understanding in Mathematics.

## Run Spark with 1 Master and 1 slave.

```
docker compose up --build 
```

## Run spark with 1 master and 3 slave

```
docker-compose up --build --scale spark-worker=3
```

