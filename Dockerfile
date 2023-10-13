FROM node:20-alpine3.18 as npm_builder
WORKDIR /code
ENV NODE_ENV=production
COPY ./autokat /code/autokat
COPY ./package.json /code/package.json
COPY ./package-lock.json /code/package-lock.json
COPY ./requirements.txt /code/requirements.txt
RUN npm ci && npm run build

FROM python:3.11-slim-bookworm
COPY --from=npm_builder /code /code
WORKDIR /code
RUN bash -c 'pip install --no-cache-dir --upgrade -r <(sed s/opencv-contrib-python/opencv-contrib-python-headless/g requirements.txt)'
ENV POINTER=dummy
CMD ["uvicorn", "autokat.server:app", "--host", "0.0.0.0", "--port", "8000"]