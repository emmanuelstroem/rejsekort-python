FROM python:alpine

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# RUN apk add --no-cache tzdata ca-certificates && \
#     addgroup -g 1000 -S rejsekort && \
#     adduser -u 1000 -S username -G rejsekort

# USER 1000:1000

COPY . .

EXPOSE 3000

CMD ["python", "app.py"]
