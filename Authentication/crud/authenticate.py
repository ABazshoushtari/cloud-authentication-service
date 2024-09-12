from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, Request, Form, File, UploadFile
import schemas.schemas
from models.models import User
import boto3
import logging
from botocore.exceptions import ClientError
import base64

from rabbitMQ.publisher import publish_username


#
# def create_user(
#         db: Session,
#         user_in: schemas.schemas.AuthenticationRequest,
#         client_ip: str
# ):
#     user: User = User(
#         national_id=encode_base64(user_in.national_id),
#         email=user_in.email,
#         last_name=user_in.last_name,
#         ip=client_ip,
#     )
#
#     try:
#         db.add(user)
#         db.commit()
#         publish_username(username=f"{user.id}N{user.national_id}")
#     except Exception:
#         db.rollback()
#         raise
#
#     return user


def create_user_formfile(
        image1: UploadFile,
        image2: UploadFile,
        client_ip: str,
        db: Session,
        national_id: str = Form(...),
        email: str = Form(...),
        last_name: str = Form(...)
):
    user: User = User(
        national_id=encode_base64(national_id),
        email=email,
        last_name=last_name,
        ip=client_ip,
    )

    try:
        db.add(user)
        db.commit()
        img1_format = image1.filename.split(".")[-1]
        img2_format = image2.filename.split(".")[-1]
        user.image1 = str(user.id) + "_1" + f".{img1_format}"
        user.image2 = str(user.id) + "_2" + f".{img2_format}"
        image1.filename = user.image1
        image2.filename = user.image2
        db.commit()
        publish_username(username=f"{user.id}")
    except Exception:
        db.rollback()
        raise
    add_to_s3(image1)
    add_to_s3(image2)
    return user


def get_user_status(
        db: Session,
        national_id,
) -> User:  #schemas.schemas.UserStatusResponse:
    user: User = db.query(User).filter(User.national_id == encode_base64(national_id)).first()

    # return schemas.schemas.UserStatusResponse(state=user.state)
    return user

def encode_base64(input_str: str):
    encoded_bytes = base64.b64encode(input_str.encode('utf-8'))
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string


def decode_base64(input_str: str):
    encoded_bytes = input_str.encode('utf-8')
    decoded_bytes = base64.b64decode(encoded_bytes)
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string


def add_to_s3(image: UploadFile):
    try:
        s3_resource = boto3.resource(
            's3',
            endpoint_url='S3_ENDPOINT_URL',
            aws_access_key_id='ACCESS_KEY',
            aws_secret_access_key='SECRET_KEY'
        )
    except Exception as exc:
        logging.error(exc)
    else:
        try:
            bucket = s3_resource.Bucket('hw1-cloudcomputing-ali')
            object_name = image.filename
            bucket.put_object(
                ACL='public-read',
                Body=image.file,
                Key=object_name
            )
        except ClientError as e:
            logging.error(e)
