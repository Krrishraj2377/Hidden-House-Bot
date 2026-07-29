FROM python:3.10.8

# Hide pip root warning
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /Hidden-House

COPY requirements.txt .

# Upgrade pip + install requirements
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
