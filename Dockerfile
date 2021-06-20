FROM python:3.9
WORKDIR /backend
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic
ENTRYPOINT ./entrypoint.sh
