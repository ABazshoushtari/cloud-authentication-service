from config import get_rabbitMQ_connection


def publish_username(username: str):
    connection = get_rabbitMQ_connection()

    channel = connection.channel()
    channel.queue_declare(queue='username')
    channel.basic_publish(
        exchange='',
        routing_key='username',
        body=username
    )
    connection.close()

#
# import pika
#
# connection = pika.BlockingConnection(
#     pika.ConnectionParameters(host='localhost'))
# channel = connection.channel()
#
# channel.queue_declare(rabbitMQ='hello')
#
# channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
# print(" [x] Sent 'Hello World!'")
# connection.close()