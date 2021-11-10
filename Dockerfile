FROM python:3.9
WORKDIR /backend
RUN apt update -y && apt install -y chromium-browser
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ./entrypoint.sh
