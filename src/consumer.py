import logging
import config
import json
import torch

from kafka import KafkaConsumer
from transformers import pipeline

# Configuración del logging (print más bonito)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Preparar el consumidor
consumer = KafkaConsumer(
    config.TOPIC,  # Nombre del topic al que nos queremos conectar
    group_id="py-group",  # Grupo de consumidores al que conectarnos, importante para mantener el offset
    bootstrap_servers=config.SERVERS,  # Servidores donde se encuentran el/los brokers de kafka
    auto_offset_reset="earliest",  # Importante! Cuando se conecta por primera vez al grupo, empieza a leer desde el principio
    value_deserializer=lambda x: json.loads(
        x.decode("utf-8")
    ),  # Deserializador de mensajes, en este caso json
)


def analyze_message(message):
    """Analiza el mensaje recibido en kafka y usa un modelo de lenguaje para analizar el sentimiento.

    Parameters
    ----------
    message : kafka.Message
        Mensaje recibido de kafka.
    """
    pipeline_ml = pipeline(
        "sentiment-analysis",
        model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",  # Para evitar warning
        device=torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        ),  # Intenta usar GPU si está disponible, si no CPU
    )

    sentiment_analysis = pipeline_ml(message.value["text"])[0]
    logging.info(
        f"Text analysis results for textID {message.value['textID']} with text: {message.value['text']} \n"
        + f"Sentiment: {sentiment_analysis['label']} - Score: {sentiment_analysis['score']}",
    )


def main():
    """Función principal para ejecutar el consumidor de Kafka."""
    logging.info("Iniciando el consumidor de kafka...")
    try:
        for message in consumer:
            analyze_message(message)
    except KeyboardInterrupt as _:
        logging.info("Saliendo del consumidor de kafka... Adiós!")
        consumer.close()


main()
