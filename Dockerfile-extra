FROM python:3.9.7-slim
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0", "app:app"]