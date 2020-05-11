FROM docker.io/resin/rpi-raspbian:latest

WORKDIR /usr/camerapi

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD ['python3', './main.py']