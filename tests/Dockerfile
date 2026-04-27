FROM python:3.12-slim

WORKDIR /work

COPY tests/requirements.txt /work/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY tests/pytest.ini /work/pytest.ini
COPY tests/conftest.py /work/conftest.py
COPY tests/tests /work/tests

ENV API_BASE_URL=http://api-preprod:8000

CMD ["pytest", "-v", "--tb=short", "tests"]
