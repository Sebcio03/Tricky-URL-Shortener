from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException,
                     Request, status)
from fastapi.responses import RedirectResponse
from sqlalchemy.orm.session import Session

from app.database import get_db
from app.urls.crud import get_url_redirection

from .tasks import register_entry

router = APIRouter(tags=["Redirect"])


@router.get("/{shorten}", response_class=RedirectResponse)
async def handle_redirection(
    shorten: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    url = get_url_redirection(db, shorten)

    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    url.clicks += 1
    db.commit()

    background_tasks.add_task(register_entry, request, url.id)
    return url.redirect_to
