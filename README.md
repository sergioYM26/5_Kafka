# 5_Kafka
Trabajo del módulo cinco del máster de datahack

## Introducción
Este proyecto implementa un ejemplo básico de uso para el trabajo del módulo de kafka.

Se ha decidido usar un dataset fijo para la implementación del ejercicio porque la API de `Twitter` (ahora `X`) tiene limitados los permisos de lectura para cuentas gratuitas.

Se ha descargado y se va a usar el dataset extraído de [kaggle](https://www.kaggle.com/datasets/abhi8923shriv/sentiment-analysis-dataset/data?select=test.csv).

> Nota: Se ha probado con una GPU Nvidia, dudo del comportamiento en un entorno que no tenga. Se ha intentado implementar para que si no hay escoja CPU.

## Planteamiento

Esta implementación se compone de un productor, tres brokers de kafka usando el docker compose que hemos visto en clase y un consumidor:

1. El productor:
    1. Lee desde el fichero `data/test.csv` datos de tweets preparados para análisis sentimental. Este dataset ha sido extraído de [kaggle](https://www.kaggle.com/datasets/abhi8923shriv/sentiment-analysis-dataset/data?select=test.csv).
    2. "Procesa" el dataset seleccionando una muestra aleatoria (para no destrozar el ordenador) y tirando columnas que no nos interesan.
    3. Envía a través de kafka los mensajes serializados como `json`.
2. Los brokers:
    1. No tienen configuración adicional, los topics se crean cuando el productor envía un primer mensaje o el consumidor se pone a escuchar.
3. El consumidor:
    1. Lee los mensajes del topic configurado.
    2. Para cada uno, llama a un modelo de machine learning que clasifica el sentimiento del tweet (campo `text` del mensaje) y le da un score que se imprime por pantalla.

## Uso
Hay dos maneras de ejecutar el proyecto, con el runner de docker o con el intérprete de python local.

El problema es que las dependencias para ejecutar el modelo son bastante pesadas y tardan mucho en instalar y por ende la imagen en construirse, para evitar esto, el servicio de `runner` está comentado por defecto, si se quiere usar hay que descomentarlo en `images/docker-compose-cluser-kafka.yml`.

Si algo falla, recomiendo mirar el fichero de configuración `src/config.py` y cambiar cualquier valor que se vea fuera de lugar.

### Local

1. Creamos el entorno virtual.
```bash
python3 -m venv .venv && source .venv/bin/activate
```

2. Instalamos las dependencias.
```bash
pip install kafka-python==2.1.5 'transformers[torch]==4.51.0' pandas==2.2.3
```

3. Levantamos el cluster de kafka.
```bash
cd images/
docker compose -f docker-compose-cluster-kafka.yml up
```

3. a. Creamos el topic en uno de los brokers de kafka (el productor debería crearlo, pero no lo hace :/, si se ejecuta primero el consumidor se puede omitir este paso).
```bash
docker exec -it kafka-broker-1 bash

kafka-topics --bootstrap-server kafka1:19092 --create --topic tw-data --partitions 1
```

4. Ejecutamos el productor para que envíe los mensajes.
```bash
cd src/
python3 producer.py
```

5. Ejecutamos el consumidor (puede ser en otra consola) para recibirlos y analizar el sentimiento de los tweets.
```bash
cd src/
python3 consumer.py
```

Se pueden repetir los pasos 4 y 5 las veces que se quiera.

### En contenedor docker
0. Descomentamos las líneas correspondientes al runner en `images/docker-compose-cluser-kafka.yml`.
```yaml
runner:
  build:
    context: ../
    dockerfile: images/Dockerfile
  container_name: runner
  restart: always
```

1. Construimos las dependencias y levantamos el cluster.
```bash
cd images/
docker compose -f docker-compose-cluster-kafka.yml build
docker compose -f docker-compose-cluster-kafka.yml up
```

1. a. Creamos el topic en uno de los brokers de kafka (el productor debería crearlo, pero no lo hace :/, si se ejecuta primero el consumidor se puede omitir este paso).
```bash
docker exec -it kafka-broker-1 bash

kafka-topics --bootstrap-server kafka1:19092 --create --topic tw-data --partitions 1
```

2. Entramos al contenedor.
```bash
docker exec -it runner bash
```

3. Ejecutamos el productor para que envíe los mensajes.
```bash
cd src/
python3 producer.py
```

4. Ejecutamos el consumidor (puede ser en otra consola) para recibirlos y analizar el sentimiento de los tweets.
```bash
cd src/
python3 consumer.py
```

Se pueden repetir los pasos 3 y 4 las veces que se quiera.
