FROM python:3.8-slim
WORKDIR /app
RUN apt-get update -y
RUN pip install --upgrade pip

COPY ./ .
RUN pip3 install python-dotenv    
ENV GOOGLE_APPLICATION_CREDENTIALS=./key.json
RUN pip install --upgrade google-api-python-client
RUN pip install google-cloud-bigquery
RUN pip install pandas
RUN pip install pyarrow
WORKDIR /app





ARG jenkinschiper
ARG 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
RUN ls
ENV PYTHONUNBUFFERED=1

RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip --no-cache-dir install PyYAML