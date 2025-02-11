## Pre-requisites

Before getting started, please ensure that you have the following dependencies installed on your system:

- Python: 3.10 or greater [Installation guide](https://www.python.org/downloads/)
- Poetry: [Installation guide](https://python-poetry.org/docs/#installing-with-the-official-installer)



## Getting Started

To set up and run the app, please follow these steps:

1. Move to the directory where `pyproject.toml` is located:

2. Install the dependencies:

   ```shell
   poetry install
   ```

3. Activate the virtual environment:

   ```shell
   poetry shell
   ```

4. Change URL for the postgrsql database in the .env file.

5. Run Fast api app using following command:
   ```shell
      python -m app
   ```


## Creating database from migration files
### 1. Apply Migrations to Create Tables
To apply the migrations and create tables from the existing migration files, run the following command:
   ```shell
      alembic upgrade head
   ```

### 2. Generate a New Migration File
To generate a new migration file based on changes in the models, use the following command:

   ```shell
      alembic revision --autogenerate -m "migration message"
   ```

and then 
   ```shell
      alembic upgrade head
   ```

### 3. Run Migration through python code
You can also use the run_migration.py script to run migrations instead of using the Alembic commands directly.
   ```shell
      python app/run_migration.py 
   ```


## Author
[Shrawan sunar](https://github.com/polymorphisma)