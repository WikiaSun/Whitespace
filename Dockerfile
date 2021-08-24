FROM python:3.8-slim

WORKDIR /whitespace

RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --ignore-pipfile

COPY . .

CMD ["pipenv", "run", "start"]