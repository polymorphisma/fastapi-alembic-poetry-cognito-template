FROM python:3.10-slim-bullseye as requirements-stage

WORKDIR /tmp

# Install system dependencies
RUN pip install poetry

COPY . /tmp/

# we export pyproject.toml which is poetry-native to plain requirements.txt that we can install with pip
# as it's the recommended approach thanks to which we do not have to install poetry in production-stage image
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10-slim-bullseye as production-stage

# Install system dependencies
RUN apt-get update && apt-get -y install libpq-dev gcc g++ curl procps net-tools tini

# Set the working directory
WORKDIR /app

# Install the project dependencies
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

# Install the project dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the rest of the project files
COPY . /app/

# Run the application
CMD ["python", "-m", "app", "run"]
