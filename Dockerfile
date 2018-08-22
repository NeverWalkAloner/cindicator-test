# Dockerfile
FROM python:3.7
WORKDIR /app
COPY polls polls
COPY polls_service polls_service
COPY manage.py requirements.txt /app/
RUN pip install -r requirements.txt && \
        python manage.py collectstatic --noinput
EXPOSE 8001
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--reload", "True", "polls_service.wsgi"]
