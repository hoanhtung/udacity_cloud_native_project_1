FROM python:3.8
LABEL maintainer="Hoanh Tung"
COPY /techtrends /app
WORKDIR /app
RUN pip install -r requirements.txt && python3 init_db.py
CMD [ "python3", "app.py" ]
EXPOSE 3111
