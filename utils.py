import sys
import july
import matplotlib.pyplot as plt
from july.utils import date_range
from fpdf import FPDF
from datetime import timedelta
from zk import ZK

sys.path.append("zk")


def get_user_list(zk: ZK) -> dict:
    """
        Get users from ZK object and returns dictionary of user
        :param zk: ZK object to user as connection
        :return: dict user_list
        """

    print('Connecting to device ...')
    zk.connect()
    zk.disable_device()
    print('Firmware Version: : {}'.format(zk.get_firmware_version()))

    # print '--- Get User ---'
    users = zk.get_users()
    print('Usuario ID\tNombre')
    user_list = {}
    for user in users:
        # privilege = 'User'
        # if user.privilege == const.USER_ADMIN:
        #    privilege = 'Admin'
        print('    {}\t\t{}'.format(user.user_id, user.name))
        user_list[int(user.user_id)] = user.name

    print('Enabling device ...')
    zk.enable_device()
    return user_list


def filter_by_date(zk: ZK, users, start_date, end_date=None):
    """
        :param zk: ZK object
        :param users: list of users to filter by
        :param start_date: start date
        :param end_date: end date
        :return history: History of attendance objects and dates
        """
    final_date = None
    if end_date is not None:
        final_date = end_date + timedelta(days=1)

    # users = [4]

    # Obtain history
    zk.disable_device()
    history = zk.get_user_history(users=users, start_date=start_date, end_date=final_date)
    zk.enable_device()

    return history


def attendance_to_dict(history):
    """
        :param history: Attendances
        :return employees: dict of employees [employees][date][in|out]['hours']
        """
    employees = {}
    for i in history:
        # name = userList[int(i)]
        # print(name)
        for j in history[i]:
            date = j[0].date()
            date_time = j[0].time()
            status = j[1]
            punch = j[2]
            # print(j)
            if i not in employees:
                employees[i] = {}
            if date not in employees[i]:
                employees[i][date] = {}
            if date in employees[i]:
                if punch in employees[i][date]:
                    if punch == 0:
                        if 1 not in employees[i][date]:
                            employees[i][date][1] = max(date_time, employees[i][date][punch])
                        employees[i][date][punch] = min(date_time, employees[i][date][punch])

                    if punch == 1:
                        if 0 not in employees[i][date]:
                            employees[i][date][int(0)] = min(date_time, employees[i][date][punch])
                        employees[i][date][punch] = max(date_time, employees[i][date][punch])

                else:
                    employees[i][date][punch] = date_time
                if (0 in employees[i][date]) and (1 in employees[i][date]):
                    t2 = employees[i][date][1]
                    t1 = employees[i][date][0]
                    t2 = timedelta(hours=t2.hour, minutes=t2.minute, seconds=t2.second)
                    t1 = timedelta(hours=t1.hour, minutes=t1.minute, seconds=t1.second)
                    hours = t2 - t1
                    employees[i][date]['Hours'] = float(hours.seconds / 3600)
    return employees


def create_user_pdf(update_history, start_date, end_date, days, errors):
    """
        Create PDF file from employees and worked days
        :param update_history: user dict with update history
        :param start_date: start date to generate
        :param end_date: end date to generate
        :param days: int days worked
        :param errors: int days with errors
        """
    # Initiate PDF
    pdf = FPDF()
    pdf.set_left_margin(1)
    pdf.set_right_margin(1)
    pdf.add_page()
    # Initiate Spaces on PDF
    h = 6
    space = 30
    week = 7
    pdf.set_font("Arial", style='BIU', size=15)
    title = 'Reporte de Asistencias ' + start_date.strftime("%d/%m/%y") + " - " + end_date.strftime("%d/%m/%y")
    pdf.cell(0, 10, txt=title, ln=1, align='C')

    # Created PDF object with
    for employee, date in update_history.items():

        pdf.set_font("Arial", style='BIU', size=11)
        header = str(days) + " días - " + str(errors) + " errores"
        pdf.cell(0, 6, txt=header, ln=1, border=1, align='C')
        count = 0

        for key, value in date.items():
            count += 1
            pdf.set_font("Arial", size=8)
            if count % week == 0:
                ln = 1
            else:
                ln = 0
            date = key.strftime("%d/%m")
            if 'Hours' in value:
                if value['Hours'] > 9:
                    pdf.set_text_color(0, 0, 0)
                elif value['Hours'] > 4:
                    pdf.set_text_color(255, 0, 0)
                else:
                    pdf.set_text_color(0, 0, 255)
                input = value[0].strftime("%H:%M")
                output = value[1].strftime("%H:%M")
                text = date + ' ' + input + '-' + output
                pdf.cell(space, h, txt=text, ln=ln, align='C')
            else:
                pdf.set_text_color(0, 0, 0)
                if 0 in value:
                    t = value[0].strftime("%H:%M")
                elif 1 in value:
                    t = value[1].strftime("%H:%M")
                else:
                    t = ' no marcó'
                error = date + ' ' + t
                pdf.set_font("Arial", style='B', size=8)
                pdf.cell(space, h, txt=error, ln=ln, align='C')

        pdf.cell(0, 4, txt=' ', ln=1, align='C')
        pdf.cell(0, 4, txt=' ', ln=1, align='C')

    return pdf


def data_to_july(user_history, start_date, end_date):
    """
    Verifies that all dates have a value
    :param user_history: dict of user_history[i][date]['Hours']
    :param start_date: start of date
    :param end_date: end of date
    :return dates, data, days, errors
    """

    dates = date_range(start_date, end_date)
    data = []
    days = 0
    errors = 0
    updated_history = {}
    for key, value in user_history.items():
        updated_history[key] = {}
        for date in dates:
            if date in value:
                if 'Hours' in value[date]:
                    if value[date]['Hours'] > 12:
                        data.append(float(-15))
                        days += 1.5
                    elif value[date]['Hours'] > 9:
                        data.append(float(-10))
                        days += 1
                    elif value[date]['Hours'] > 4:
                        data.append(float(-5))
                        days += 0.5
                    else:
                        data.append(float(5))
                        errors += 1
                else:
                    data.append(float(10))
                    errors += 1
                updated_history[key][date] = user_history[key][date]
            else:
                data.append(float(0))
                updated_history[key][date] = {}

    return dates, data, days, errors, updated_history


def create_july_image(dates, data, days, errors, day_wage):
    """
    Creates a plot image with the july library.
    :param dates: list of dates
    :param data: list of data point for each date
    :param days: int of days worked
    :param errors: int of errors
    :param day_wage: wage per day
    :return axes: matplotlib axes
    """
    figsize = (5, 5)
    title = str(days) + " días (S./ " + str(day_wage * days) + ") - " + str(errors) + " errores"

    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    axes = july.heatmap(dates, data, month_grid=True,
                        horizontal=False, date_label=True,
                        frame_on=True, cmax=15, cmin=-15,
                        title=title, cmap='coolwarm', ax=ax)
    return axes
