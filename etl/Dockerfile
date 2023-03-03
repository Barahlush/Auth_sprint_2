FROM python:3.10-alpine

WORKDIR /opt/app

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip==22.3.1 && pip install --no-cache-dir -r requirements.txt
COPY . .

RUN /usr/bin/crontab ./cron-job.txt


EXPOSE 8001

# ENTRYPOINT ["crond", "-f"]
ENTRYPOINT ["python", "run_etl.py"]
