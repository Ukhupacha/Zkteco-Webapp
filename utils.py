import sys
import os
import configparser
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from fpdf import FPDF
from datetime import datetime, timedelta
from zk import ZK, const
sys.path.append("zk")

groups = {
        1: "escogedoras",
        2: "varones",
        3: "secretaria"
}

def getusers(zk: ZK) -> dict:
        """
        Get users from ZK object and returns dictionary of user
        :param zk: ZK object to user as connection
        :return: dict, connection zk
        """

        print('Connecting to device ...')
        zk.connect()
        zk.disable_device()
        print('Firmware Version: : {}'.format(zk.get_firmware_version()))

        # print '--- Get User ---'
        users = zk.get_users()
        print('Usuario ID\tNombre')
        userlist = {}
        for user in users:
                # privilege = 'User'
                # if user.privilege == const.USER_ADMIN:
                #    privilege = 'Admin'
                print('    {}\t\t{}'.format(user.user_id, user.name))
                userlist[int(user.user_id)] = user.name

        print('Enabling device ...')
        zk.enable_device()
        return userlist, zk

def configfile(pathFile):
        """
        Creates config file if it doesn't exist, reads it if it exists
        :param pathFile: Path and name of the config file
        :return configfile: Parsed config file
        """
        # Configuration file
        path = os.path.dirname(pathFile)
        config = configparser.ConfigParser()

        if not os.path.exists(path):
                print("Creating config path " + path)
                os.makedirs(path)

        if not os.path.exists(pathFile):
                escogedoras = input("Ingresar los numeros de escogedoras:\n")
                varones = input("Ingreasar los numeros de los varones:\n")
                secrataria = input("Ingresar los numeros de secretaria:\n")
                config['Usuarios'] = {'escogedoras': escogedoras, 'varones': varones, 'secretaria': secrataria}

                escogedoras = input("Ingresar pago escogedoras:\n")
                varones = input("Ingresar pago varones:\n")
                secrataria = input("Ingresar pago secretaria:\n")
                config['Pagos'] = {'escogedoras': escogedoras, 'varones': varones, 'secretaria': secrataria}
                with open(pathFile, 'w') as configfile:
                        config.write(configfile)

        # Read the file
        config.read(pathFile)
        return config

def getgroupandpay(userList, config):
        """
        :param userList: List of users
        :return users:
        """
        print("Ingrese un tipo de grupo a generar:")
        for group in groups:
                print("{}.- {}".format(group, groups[group]))
        group = int(input())
        print("Grupo escogido:\t" + str(groups[group]))
        users = config.get('Usuarios', str(groups[group]))
        payment = config.get('Pagos', str(groups[group]))
        users = [int(i) for i in users.split(',')]
        names = [userList[i] for i in users]
        print("Usuarios ID:\t" + str(users))
        print("Nombres:\t" + str(names))
        return users, payment



def filterdate(zk:ZK, users):
        """
        :param zk: ZK object
        :param users: list of users to filter by
        :return history: History of attendance objects
        """
        while True:
                try:
                        startdate = input("Ingrese fecha inicial (dd/mm/yyyy):\n")
                        startdate = datetime.strptime(startdate, '%d/%m/%Y')
                except ValueError:
                        continue
                else:
                        break

        while True:
                try:
                        enddate = input("Ingrese fecha final (dd/mm/yyyy):\n")
                        enddate = datetime.strptime(enddate, '%d/%m/%Y') + timedelta(days=1)
                except ValueError:
                        continue
                else:
                        break


        #startdate = datetime.strptime("24/04/2023", '%d/%m/%Y')
        #enddate = datetime.strptime("28/04/2023", '%d/%m/%Y')  + timedelta(days=1)
        #users = [4]

        # Obtain history
        zk.disable_device()
        history = zk.get_user_history(users=users, start_date=startdate, end_date=enddate)
        zk.enable_device()

        return history


def attendance2dict(history):
        """
        :param history: Attendances
        :return employees: dict of employees [employees][date][in|out]['hours']
        """
        employees = {}
        for i in history:
                #name = userList[int(i)]
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

def countdays(employees, payment):
        """
        Count days worked and error days
        :param employees: dictionary of employees punch days
        :param payment: salary per day
        :return worked: [employees][days, errors]
        """
        # First pass for counting days
        worked = {}
        for employee, date in employees.items():
                days = 0
                errors = 0
                for key, value in date.items():
                    if 'Hours' in value:
                        if value['Hours'] > 9:
                            days += 1
                        elif value['Hours'] > 4:
                            days += 0.5
                    else:
                        errors += 1
                worked[employee] = [days, errors, float(int(days)*int(payment))]
        #print(worked)
        return worked


def createpdf(employees, worked, userList):
        """
        Create PDF file from employees and worked days
        :param employees: dict of employees
        :param worked: dict of worked days, error days
        """
        root = tk.Tk()
        root.withdraw()
        # Initiate PDF
        pdf = FPDF()
        pdf.set_left_margin(1)
        pdf.set_right_margin(1)
        pdf.add_page()
        # Initiate Spaces on PDF
        h = 6
        space = 35
        week = 6
        pdf.set_font("Arial", style='BIU', size=20)
        pdf.cell(0, 10, txt='Reporte de Asistencias', ln=1, align='C')

        # Created PDF object with
        for employee, date in employees.items():

                pdf.set_font("Arial", style='BIU', size=11)
                header = userList[int(employee.split()[0])] + " (" + str(worked[employee][0]) + \
                         " días S/. " + str(worked[employee][2]) + ") - (" + str(worked[employee][1]) + " errores)"
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
                                input = value[0].strftime("%H:%M")
                                output = value[1].strftime("%H:%M")
                                text = date + ' ' + input + '-' + output
                                pdf.cell(space, h, txt=text, ln=ln, align='C')
                        else:
                                if 0 in value:
                                        t = value[0].strftime("%H:%M")
                                if 1 in value:
                                        t = value[1].strftime("%H:%M")

                                error = date + ' ' + t
                                pdf.set_font("Arial", style='B', size=8)
                                pdf.cell(space, h, txt=error, ln=ln, align='C')

                pdf.cell(0, 4, txt=' ', ln=1, align='C')
                pdf.cell(0, 4, txt=' ', ln=1, align='C')

        # Save document
        extra = datetime.today().strftime('%d-%m-%Y')
        output = 'Asistencias' + '-' + extra
        file_path = filedialog.asksaveasfilename(filetypes=[("pdf", ".pdf")],
                                                 defaultextension=".pdf",
                                                 initialdir="~/Documentos",
                                                 initialfile=output)
        pdf.output(file_path)