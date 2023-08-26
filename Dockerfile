FROM python:3.6.9
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /neo_bundle
WORKDIR /neo_bundle
RUN pip install pip -U
RUN pip install gunicorn
COPY requirements.txt /neo_bundle/
RUN pip install -r requirements.txt
COPY . /neo_bundle/
EXPOSE 8002
RUN python manage.py collectstatic --no-input --clear
