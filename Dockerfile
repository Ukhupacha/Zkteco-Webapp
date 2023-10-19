From python:3.8
MAINTAINER ukhupacha@gmail.com

RUN apt-get update
RUN apt-get install -y uvicorn locales locales-all inetutils-ping
ENV LC_ALL es_ES.UTF-8
ENV LANG es_ES.UTF-8
ENV LANGUAGE es_ES.UTF-8
ADD app.py /opt/zkteco/app.py
ADD utils.py /opt/zkteco/utils.py
ADD templates /opt/zkteco/templates
ADD zk /opt/zkteco/zk
ADD requirements.txt /opt/zkteco/requirements.txt
RUN pip3 install pip --upgrade
RUN pip3 install -r /opt/zkteco/requirements.txt

ENTRYPOINT ["/opt/zkteco/app.py"]
