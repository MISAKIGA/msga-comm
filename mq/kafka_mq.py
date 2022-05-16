from kafka import KafkaProducer, KafkaConsumer


class Producer(object):
    def __init__(self, bootstrap_servers=None, **kwargs):
        if bootstrap_servers is None:
            bootstrap_servers = ['localhost:9092']

        self.bootstrap_servers = bootstrap_servers
        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers, **kwargs)

    def send(self, topic, msg):
        self.producer.send(topic, msg)

    def open(self):
        pass

    def close(self):
        self.producer.close()


class Consumer(object):
    def __init__(self, topic, group_id=None, bootstrap_servers=None, **kwargs):

        if bootstrap_servers is None:
            bootstrap_servers = ['localhost:9092']

        self.bootstrap_servers = bootstrap_servers
        self.consumer = KafkaConsumer(topic, group_id=group_id, bootstrap_servers=self.bootstrap_servers, **kwargs)

    def subscribe(self, topics):
        self.consumer.subscribe(topics=topics)
        for message in self.consumer:
            print("%s:%d:%d: key=%s value=%s" % (
                message.topic, message.partition, message.offset, message.key, message.value))

    def open(self):
        pass

    def close(self):
        self.consumer.close()
