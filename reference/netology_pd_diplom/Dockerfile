FROM python:3.11-slim

WORKDIR /app

COPY . /app/
COPY ./netology_pd_diplom/requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y curl && apt-get clean
RUN pip install -r requirements.txt

CMD python manage.py migrate \
    && python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='root').exists() or User.objects.create_superuser('root', 'root@example.com', 'root')" \
    && python manage.py initialize_db \
    && python manage.py collectstatic --no-input \
    && gunicorn prediction.wsgi:application --bind 0.0.0.0:8000 --log-level info


#FROM python:3.11-alpine
#
#WORKDIR /src/
#
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
#
#COPY ../.. .
#
#RUN apk add --update --no-cache --virtual .tmp-build-deps \
#    gcc libc-dev linux-headers postgresql-dev && \
#    pip install --no-cache-dir -r requirements.txt
#
#ENTRYPOINT ["/src/entrypoint.sh"]