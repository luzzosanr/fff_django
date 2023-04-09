FROM python:3.9-alpine

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
RUN pip install -r /requirements.txt
RUN apk del .tmp

RUN mkdir /app
COPY ./app /app
WORKDIR /app
COPY ./scripts/ /scripts

RUN chmod +x /scripts/entrypoint.sh

RUN mkdir -p /vol/web/static
RUN adduser -D user
RUN chown -R user:user /vol
RUN chmod -R 755 /vol/web
RUN chown -R user:user logs
RUN chmod -R 755 logs
USER user

CMD ["entrypoint.sh"]