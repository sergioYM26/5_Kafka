import json
import logging

from kafka import KafkaProducer
import config
import pandas as pd

# Configuración del logging (print más bonito)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Creamos el productor de Kafka con la configuración de los brokers
# Esto se puede cambiar en el fichero config.py
producer = KafkaProducer(
    bootstrap_servers=config.SERVERS,  # Servidores donde se encuentran el/los brokers de kafka
    value_serializer=lambda m: json.dumps(m).encode(
        "utf-8"
    ),  # Serializador de mensajes, en este caso json
)


def on_send_success(meta):
    """Callback para cuando se envía un mensaje correctamente.
    Parameters
    ----------
    meta : kafka.producer.record_metadata.RecordMetadata
        Metadata del mensaje enviado.
    """
    logging.info(
        f"Successfully sent message to Topic: {meta.topic} - Offset: {meta.offset}"
    )


def on_send_error(ex):
    """Callback para cuando se envía un mensaje y se produce un error.
    Parameters
    ----------
    ex : _ExcInfoType
        Excepción producida al enviar el mensaje.
    """
    logging.error(
        f"Error while producing message to kafka topic: {config.TOPIC}", exc_info=ex
    )


def load_data():
    """Función para leer los datos de un fichero csv y enviar una parte en kafka.

    Returns
    -------
    list
        Lista de diccionarios con los datos a enviar.
    """
    df = pd.read_csv(config.DATASET_PATH, sep=",").sample(n=config.SAMPLE_SIZE)
    df = df.drop(
        columns=["Population -2020", "Land Area (Km�)", "Density (P/Km�)", "sentiment"]
    )  # Tiramos algunas columnas que no sirven, además del sentimiento que es lo que vamos a clasificar

    return df.to_dict("records")


def main():
    """Función principal para cargar los datos y enviarlos usando el productor de Kafka."""
    data_to_send = load_data()
    for key, msg in enumerate(data_to_send):
        producer.send(  # Enviamos el mensaje, cada uno viene en json y hemos configurado el serializer
            config.TOPIC, key=str(key).encode("utf-8"), value=msg
        ).add_callback(on_send_success).add_errback(on_send_error)

    producer.flush()  # Recomendado ejecutar de vez en cuando para limpiar el buffer


main()
