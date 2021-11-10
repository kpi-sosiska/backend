FROM python:3.9
WORKDIR /backend
RUN apt install -y chromium-chromedriver
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ./entrypoint.sh
