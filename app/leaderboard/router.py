from typing import List, Optional
from datetime import date as DateType
from fastapi import APIRouter, Depends, Query

from app.leaderboard import service
from app.leaderboard.schemas import LeaderboardRow, Scope
from app.database import get_db
from app.users.dependencies import get_current_user


router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get(
    "/",
    response_model=List[LeaderboardRow],
    summary="Pobierz ranking (z opcjonalnym filtrem dat i zakresem)",
)
def get_leaderboard(
    date_from: Optional[DateType] = Query(
        None, alias="from", description="Od kiedy (YYYY-MM-DD)"
    ),
    date_to: Optional[DateType] = Query(
        None, alias="to", description="Do kiedy wlacznie (YYYY-MM-DD)"
    ),
    scope: Scope = Query(
        "global",
        description="'global' = wszyscy uzytkownicy, 'friends' = tylko obserwowani + ja",
    ),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    return service.get_leaderboard(
        db, str(current_user["id"]), scope, date_from, date_to
    )
