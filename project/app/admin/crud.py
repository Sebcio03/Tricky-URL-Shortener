from sqlalchemy.orm import Session, joinedload

from app.urls.models import CrawledData


def get_all_crawled_data(db: Session):
    return db.query(CrawledData).all()


def get_crawled_data_by_id(db: Session, data_id):
    return (
        db.query(CrawledData)
        .filter(CrawledData.id == data_id)
        .options(joinedload("emails"))
        .first()
    )
