from datetime import datetime
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app import settings

from .models import CrawledData, EmailModel, ImageModel, UrlModel


def get_user_urls(db: Session, user_id: int):
    return db.query(UrlModel).filter(UrlModel.user_id == user_id).all()


def get_url(db: Session, user_id: int, shorten: str):
    return (
        db.query(UrlModel)
        .filter(UrlModel.user_id == user_id, UrlModel.shorten == shorten)
        .options(joinedload("entries"))
        .first()
    )


def get_url_redirection(db: Session, shorten: str):
    return db.query(UrlModel).filter(UrlModel.shorten == shorten).first()


def create_url_shortener(db: Session, user_id: int, url: dict):
    url["user_id"] = user_id
    model = UrlModel(**url)
    db.add(model)
    if not model.shorten:
        db.flush()
        db.refresh(model)
        model.shorten = settings.hashids.encode(model.id)
    db.commit()
    db.refresh(model)
    return model


def get_or_create_email(db: Session, value: str):
    email = db.query(EmailModel).filter(EmailModel.value == value).first()
    if not email:
        email = EmailModel(value=value)
        db.add(email)
        db.commit()
    return email


def get_or_create_image(db: Session, image: str):
    try:
        image = db.query(ImageModel).filter(ImageModel.value == image).first()
    except IntegrityError:
        image = ImageModel(value=image)
        db.add(image)
        db.commit()
        db.refresh(image)
    return image


def create_crawdled_data(db: Session, title, html, **entry_data):
    file_name = f"{title}-{uuid4()}.html"
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
    )
    try:
        s3_client.put_object(
            Body=bytes(html.encode("utf-8")),
            Bucket=settings.AWS_BUCKET_NAME,
            Key=file_name,
        )
    except ClientError as e:
        print(e)
    entry = CrawledData(html=settings.AWS_BUCKET_HOST + file_name, **entry_data)
    db.add(entry)
    db.commit()
    return entry
