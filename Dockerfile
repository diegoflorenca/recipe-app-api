
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
    /py/bin/pip install -r /tmp/requirements.txt && \
    # Install dev requirements.
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    # Remove temporary files.
    rm -rf /tmp && \
    # Create a non-root user.
    adduser \
        --disabled-password \
        --no-create-home \
        django-user
        
# Set the path to the virtual environment.
ENV PATH="/py/bin:$PATH"

# Set the default user.
USER django-user