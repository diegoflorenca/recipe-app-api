FROM python:3.9-alpine3.13
LABEL maintainer="https://github.com/diegoflorenca"

# The enviroment variable ensures that the python output is set straight to the terminal with utf8mb4.
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false

# A single line command that creates a virtual environment and installs the dependencies in it.
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    # Install dev requirements.
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    # Remove temporary files.
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    # Create a non-root user.
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol
        
# Set the path to the virtual environment.
ENV PATH="/py/bin:$PATH"

# Set the default user.
USER django-user