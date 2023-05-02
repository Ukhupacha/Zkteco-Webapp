import tempfile
from datetime import date, datetime
from utils import *
from fastapi import FastAPI, Depends, Request, Form, status
from starlette.responses import RedirectResponse, FileResponse
from starlette.templating import Jinja2Templates

sys.path.append("zk")

templates = Jinja2Templates(directory="templates")

app = FastAPI()
zk = ZK('zkteco.intranet', port=4370, timeout=5, password=0, force_udp=False, ommit_ping=False)
user_list = get_user_list(zk)


# Dependency
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("base.html",
                                      {"request": request, "user_list": user_list})


@app.post("/attendance")
def add(request: Request,
        id_worker: int = Form(...),
        start_date: date = Form(...),
        end_date: date = Form(...),
        day_wage: int = Form(...)):
    user = [id_worker]
    start_date = datetime(start_date.year, start_date.month, start_date.day)
    end_date = datetime(end_date.year, end_date.month, end_date.day)
    attendance = filter_by_date(zk, user, start_date, end_date)
    user_history = attendance_to_dict(attendance)
    worked = count_days(user_history, day_wage)
    pdf = create_pdf(user_history, worked, user_list, start_date, end_date)
    pdf_temp = "attendance.pdf"
    pdf.output(pdf_temp)
    name = user_list[id_worker] + ".pdf"

    return FileResponse(pdf_temp, media_type="application/pdf", filename=name)
