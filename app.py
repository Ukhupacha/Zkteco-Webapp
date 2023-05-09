#!/usr/local/bin/python3
import uvicorn
import argparse
import matplotlib
import matplotlib.pyplot as plt
import locale
import base64
import io
import sys
from datetime import datetime, date
from utils import get_user_list, filter_by_date, attendance_to_dict, create_user_pdf, data_to_july, create_july_image
from pathlib import Path
from fastapi import FastAPI, Request, Form, Response,BackgroundTasks
from starlette.templating import Jinja2Templates
from zk import ZK

sys.path.append("zk")

locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

app = FastAPI()
zk = ZK('zkteco.intranet', port=4370, timeout=5, password=0, force_udp=False, ommit_ping=False)
user_list = get_user_list(zk)
matplotlib.use('agg')


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("base.html",
                                      {"request": request, "user_list": user_list})


@app.post("/pdf")
async def generate_report(background_tasks: BackgroundTasks,
                          id_worker: int = Form(...),  start_date: date = Form(...), end_date: date = Form(...)):
    user = [id_worker]
    start_date = datetime(start_date.year, start_date.month, start_date.day)
    end_date = datetime(end_date.year, end_date.month, end_date.day)
    attendance = filter_by_date(zk, user, start_date, end_date)
    user_history = attendance_to_dict(attendance)
    dates, data, days, errors, updated_history = data_to_july(user_history, start_date, end_date)
    pdf = create_user_pdf(updated_history, start_date, end_date, days, errors)
    pdf_string = pdf.output(dest='S').encode('latin-1')
    pdf_buff = io.BytesIO(pdf_string)
    background_tasks.add_task(pdf_buff.close)
    filename = user_list[id_worker] + '.pdf'
    headers = 'attachment; filename=' + filename
    headers = {'Content-Disposition': headers}
    return Response(pdf_buff.getvalue(), headers=headers, media_type='application/pdf')


@app.post("/attendance")
async def attendance_image(request: Request, id_worker: int = Form(...), start_date: date = Form(...),
                           end_date: date = Form(...), day_wage: int = Form(...)):
    user = [id_worker]
    start_date = datetime(start_date.year, start_date.month, start_date.day)
    end_date = datetime(end_date.year, end_date.month, end_date.day)
    attendance = filter_by_date(zk, user, start_date, end_date)
    user_history = attendance_to_dict(attendance)
    dates, data, days, errors, updated_history = data_to_july(user_history, start_date, end_date)

    axes = create_july_image(dates, data, days, errors, day_wage)
    fig = axes.get_figure()
    plt.axes(axes)
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='PNG')
    plt.close(fig)
    png = img_buf.getvalue()
    img_buf.close()
    base64_encoded_image = base64.b64encode(png).decode("utf-8")
    title = [user_list[id_worker], start_date.strftime("%d/%m/%y") + " - " + end_date.strftime("%d/%m/%y")]
    return templates.TemplateResponse("base.html",
                                      {"request": request,
                                       "user_list": user_list,
                                       "title": title,
                                       "img": base64_encoded_image})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Attendance app')
    parser.add_argument('-a', '--address', help='Host address', default='0.0.0.0')
    parser.add_argument('-p', '--port', type=int, help='Host port', default=80)

    args = parser.parse_args()
    uvicorn.run(app, host=args.address, port=args.port)
