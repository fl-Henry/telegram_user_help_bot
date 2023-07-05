# build_docker-compose_yaml.py

from dotenv import dotenv_values
from jinja2 import Environment, FileSystemLoader


def create_docker_compose_yaml():
    # Load config data
    config = dotenv_values('../src/.env')

    environment = Environment(loader=FileSystemLoader("."))
    template = environment.get_template("docker-compose.yaml.jinja")

    filename = "docker-compose.yaml"
    content = template.render(
        pg_user=config['POSTGRES_USER'],
        pg_password=config['POSTGRES_PASSWORD'],
        pg_db=config['POSTGRES_DB'],
    )

    with open(filename, mode="w", encoding="utf-8") as message:
        message.write(content)


if __name__ == '__main__':
    create_docker_compose_yaml()
