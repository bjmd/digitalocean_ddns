FROM python:3.7

WORKDIR /opt 
ADD . /opt  
RUN pip install -r requirements.txt
RUN apt update
RUN apt install dnsutils -y

CMD ["python", "/opt/app.py"]`