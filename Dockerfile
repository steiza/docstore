FROM python:3.10-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /usr/src/app/storage

VOLUME [ "/usr/src/app/storage" ]

CMD [ "python3", "docstore" ]