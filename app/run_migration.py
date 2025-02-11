import subprocess


def run_migration():
    subprocess.run(["alembic", "upgrade", "head"], check=True)
