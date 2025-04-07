import os

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "test.csv"
)

SAMPLE_SIZE = 20

TOPIC = "tw-data"

SERVERS = (
    ["127.0.0.1:9092", "127.0.0.1:9093", "127.0.0.1:9094"]
    if os.environ.get("RUNTIME") != "docker"
    else ["kafka1:19092", "kafka2:19093", "kafka3:19094"]
)
