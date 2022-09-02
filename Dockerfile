FROM python:3.8
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt
ADD app.py /app
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8000", "app:app"]
