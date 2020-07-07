FROM python:3.7

WORKDIR /opt 
ADD app.py /opt
ADD requirements.txt /opt
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "/opt/app.py" ]