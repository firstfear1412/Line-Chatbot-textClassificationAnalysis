FROM python:3.11.4
COPY . .
# WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python","wsgi.py"]