import requests
from fastapi import Request
from ua_parser import user_agent_parser

from app.database import SessionLocal

from .models import EntryModel


def register_entry(request: Request, url_id: int):

    user_agent = request.headers["User-Agent"]
    ip = request.client.host
    ua = user_agent_parser.Parse(user_agent)

    data = requests.get(f"http://ip-api.com/json/{ip}?fields=58049").json()

    if data["status"] == "success":
        lat = data["lat"]
        lon = data["lon"]
        country = data["country"]
    else:
        lat = 0
        lon = 0
        country = None

    entry = EntryModel(
        url_id=url_id,
        full_user_agent=user_agent,
        referer=request.headers.get("Referer"),
        os=ua.get("os").get("family"),
        browser=ua.get("user_agent").get("family"),
        ip=ip,
        lat=lat,
        lon=lon,
        country=country,
    )
    db = SessionLocal()
    db.add(entry)
    db.commit()
