FROM python:3.12

RUN pip install -U pip setuptools wheel
RUN pip install pdm

COPY pyproject.toml pdm.lock README.md /bitespeed/
COPY ./ /bitespeed/

WORKDIR /bitespeed
RUN pdm install --prod --no-editable

EXPOSE 8000

CMD ["pdm", "run", "python", "-m", "uvicorn", "--factory", "--port", "8000", "bitespeed.app:create_app"]
