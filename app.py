#!/usr/bin/python3
import uvicorn
import argparse
import matplotlib.pyplot as plt
import base64
from PIL import Image
from datetime import date, datetime
from utils import *
from pathlib import Path
from fastapi import FastAPI, Depends, Request, Form, status
from starlette.responses import RedirectResponse, FileResponse
from starlette.templating import Jinja2Templates

sys.path.append("zk")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

app = FastAPI()
zk = ZK('zkteco.intranet', port=4370, timeout=5, password=0, force_udp=False, ommit_ping=False)
user_list = get_user_list(zk)
image_path = 'image.png'
pdf_path = 'pdf.pdf'


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
    # worked = count_days(user_history, day_wage)
    # pdf = create_pdf(user_history, worked, user_list, start_date, end_date)
    dates, data = data_to_july(user_history, start_date, end_date)
    figsize = (5, 5)
    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    axes = july.heatmap(dates, data, month_grid=True,
                        horizontal=False, date_label=True,
                        title='Asistencias', cmap="github", ax=ax)
    plt.axes(axes)
    plt.savefig(image_path)
    im = Image.open(image_path)
    rgb_im = im.convert('RGB')
    rgb_im.save('image.jpg')
    file = open('image.png', 'rb')
    data = file.read()
    encoded_image = base64.b64encode(data).decode("utf-8")
    return templates.TemplateResponse("base.html",
                                      {"request": request, "img": encoded_image})

    """
    pdf = create_image_pdf(image_path)

    pdf.output(pdf_path)
    name = user_list[id_worker] + ".pdf"

    return FileResponse(pdf_path, media_type="application/pdf", filename=name)
    """

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Attendance app')
    parser.add_argument('-a', '--address',
                        help='Host address', default='0.0.0.0')
    parser.add_argument('-p', '--port', type=int,
                        help='Host port', default=80)

    args = parser.parse_args()
    uvicorn.run(app, host=args.address, port=args.port)
