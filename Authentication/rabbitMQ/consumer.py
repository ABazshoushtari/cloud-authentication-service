from config import get_rabbitMQ_connection, get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import Depends
import requests
from config import get_db
from models.models import User

db = next(get_db())


def consume_username():
    while True:
        try:
            connection = get_rabbitMQ_connection()
            channel = connection.channel()
            channel.queue_declare(queue='username')

            channel.basic_consume('username', callback, auto_ack=True)
            print(' [*] Waiting for messages:')
            channel.start_consuming()

            connection.close()
        except Exception:
            print("Consumer failed. restarting.")


def callback(ch, method, properties, body):
    print(" [x] Received " + str(body))
    # parse str(body) and get id
    user_id = int(str(body).split("'")[1])
    user = db.query(User).filter(User.id == user_id).first()
    user.state = "accepted"  # will change later if auth fails
    # get img1 and img2 fields from db
    user_img1_filename = user.image1
    user_img2_filename = user.image2
    # dont download from S3, give below url to IMGGA:

    image1_url = 'https://hw1-cloudcomputing-ali.s3.ir-thr-at1.arvanstorage.ir/hw1-cloudcomputing-ali/' + user_img1_filename
    image2_url = 'https://hw1-cloudcomputing-ali.s3.ir-thr-at1.arvanstorage.ir/hw1-cloudcomputing-ali/' + user_img2_filename

    print(image1_url)
    print(image2_url)

    face_id_1 = face_detection(image1_url)
    face_id_2 = face_detection(image2_url)

    if not (face_id_1 and face_id_2):
        user.state = "rejected"
    elif not face_similarity(face_id_1, face_id_2):
        user.state = "rejected"

    # update state in db
    db.commit()

    # send email
    send_email(user.email, user.state)

    print(" [@] Proccessed User request with user id : " + str(user.id))


def face_detection(image_url: str):
    api_key = 'API_KEY'
    api_secret = 'API_SECRET'

    response = requests.get(
        'https://api.imagga.com/v2/faces/detections?image_url=' + image_url + "&return_face_id=1",
        auth=(api_key, api_secret))
    print(response.json())
    if len(response.json()["result"]["faces"]) < 1:
        return None
    face_id = response.json()["result"]["faces"][0]["face_id"]
    return face_id


def face_similarity(first_face_id: str, second_face_id: str):
    api_key = 'API_KEY'
    api_secret = 'API_SECRET'

    response = requests.get(
        'https://api.imagga.com/v2/faces/similarity?face_id=%s&second_face_id=%s' % (first_face_id, second_face_id),
        auth=(api_key, api_secret))
    if float(response.json()["result"]["score"]) < 80:
        return False
    return True


def send_email(email: str, state: str):
    if state == "accepted":
        authorization_report = "Your Authorization request accepted successfully."
    else:
        authorization_report = "Your Authorization request rejected."
    return requests.post(
        "https://api.mailgun.net/v3/sandbox90f355c2726b4e8789a7ec98994be7d9.mailgun.org/messages",
        auth=("api", "API_KEY"),
        data={"from": "Excited User <mailgun@sandbox90f355c2726b4e8789a7ec98994be7d9.mailgun.org>",
              "to": [email],
              "subject": "Authorization State",
              "text": authorization_report})
