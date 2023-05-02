# -*- coding: utf-8 -*-
import sys
import argparse

sys.path.append("zk")
from os.path import abspath, expanduser
from utils import *


def main():
    parser = argparse.ArgumentParser(description='ZK Basic Reading Tests')
    parser.add_argument('-a', '--address',
                        help='ZK device Address [zkteco.intranet]', default='zkteco.intranet')
    parser.add_argument('-p', '--port', type=int,
                        help='ZK device port [4370]', default=4370)
    parser.add_argument('-T', '--timeout', type=int,
                        help='Default [10] seconds (0: disable timeout)', default=10)
    parser.add_argument('-P', '--password', type=int,
                        help='Device code/password', default=0)
    parser.add_argument('-f', '--force-udp', action="store_true",
                        help='Force UDP communication')
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='Print debug information')
    parser.add_argument('-u', '--updatetime', action="store_true",
                        help='Update Date/Time')

    args = parser.parse_args()

    zk = ZK(args.address, port=args.port, timeout=args.timeout, password=args.password,
            force_udp=args.force_udp, verbose=args.verbose)

    try:

        # Return List of Users and ZK Connection
        userList= get_user_list(zk)

        # Configuration file
        pathFile = abspath(expanduser("~/.config/zkteco/config.ini"))
        config = config_file(pathFile)

        # Filter by user/group
        users, payment = get_group_and_pay(userList, config)

        # Filter by date input
        start_date, end_date = input_date()

        history = filter_by_date(zk, users, start_date, end_date)

        # Attendance to dict by date
        employees = attendance_to_dict(history)

        # Count worked days and error days and payment
        worked = count_days(employees, payment)

        # Create PDF file
        pdf = create_pdf(employees, worked, userList, start_date, end_date)

        # Save document

        root = tk.Tk()
        root.withdraw()

        extra = datetime.today().strftime('%d-%m-%Y')
        output = 'Asistencias' + '-' + extra
        file_path = filedialog.asksaveasfilename(filetypes=[("pdf", ".pdf")],
                                                 defaultextension=".pdf",
                                                 initialdir="~/Documentos",
                                                 initialfile=output)
        pdf.output(file_path)

        # Bye
        input("Verificar documento y cerrar esta ventana\n")

    except Exception as e:
        print("Process terminate : {}".format(e))
    finally:
        if zk:
            zk.disconnect()


if __name__ == "__main__":
    main()
