from fastapi import APIRouter, Request, Query
from app.utils.helpers import get_ist_date_str
from app.db.crud import save_intake, get_intake, last_7_days

router = APIRouter()

@router.post("/update")
def update_intake(data: dict, request: Request):
    save_intake(request.state.user_email, data["date"], data["totals"])
    return {"msg": "Intake saved"}

@router.get("/day")
def day_intake(date: str, request: Request):
    print(f"Fetching intake for date: {date}")
    return get_intake(request.state.user_email, date) or {"msg": "no data"}

@router.get("/last-7-days")
def seven_days(request: Request):
    return {"calories": last_7_days(request.state.user_email)}

@router.get("/today")
def today_intake(request: Request):
    today_date = get_ist_date_str()   # 👈 compute dynamically
    print(f"Today's date in IST: {today_date}")

    return (
        get_intake(request.state.user_email, today_date)
        or {"date": today_date, "msg": "no data"}
    )