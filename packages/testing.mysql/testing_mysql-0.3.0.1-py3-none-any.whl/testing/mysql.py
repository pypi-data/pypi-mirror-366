import docker
import logging
import sqlalchemy as sa
import time
import io
import os
import tarfile

logger = logging.getLogger(__name__)


class MySQL:
    kind = "database"

    def __init__(self, info={}):
        self.info = {
            "host": "localhost",
            "username": "someuser",
            "password": "somepasswd",
            "dbname": "somedb",
            "port": 3306,
        }
        self.info.update(**info)

    def url(self):
        return "mysql+pymysql://{username}:{password}@{host}:{port}/{dbname}".format(
            **self.info
        )

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


class DockerMySQL:
    kind = "database"

    def __start_db(self):
        return self.client.containers.run(
            "docker.io/mysql:latest",
            name=self.info.get("name"),
            environment={
                "MYSQL_DATABASE": self.info["dbname"],
                "MYSQL_PASSWORD": self.info["password"],
                "MYSQL_ROOT_PASSWORD": self.info["password"],
                "MYSQL_USER": self.info["username"],
            },
            ports={
                "3306/tcp": self.info["port"],
            },
            detach=True,
            auto_remove=True,
        )

    def __wait_until_mysql_reports_itself_ready(self):
        target_string = "MySQL init process done. Ready for start up."
        for log_chunk in self.container.logs(
            stream=True,
            follow=True,
        ):
            read = log_chunk.decode("utf-8")
            if target_string in read:
                break

    def __wait_until_mysql_responds_ping(self, wait_seconds=1):
        while True:
            (exit_code, _) = self.container.exec_run(
                [
                    "mysqladmin",
                    "ping",
                    "--silent",
                    "-h",
                    self.info["host"],
                    "-P",
                    self.info["port"],
                    f"-p{self.info['password']}",
                ]
            )
            if exit_code == 0:
                break
            time.sleep(wait_seconds)

    def wait_until_ready(self):
        self.__wait_until_mysql_reports_itself_ready()
        self.__wait_until_mysql_responds_ping(0.5)

    def __admin_url(self):
        return "mysql+pymysql://root:{password}@{host}:{port}/{dbname}".format(
            **self.info
        )

    def url(self):
        return "mysql+pymysql://{username}:{password}@{host}:{port}/{dbname}".format(
            **self.info
        )

    def connect(self):
        self.wait_until_ready()
        return self.engine.connect()

    def admin(self):
        """
        Returns an Engine to use the MySQL instance as root.
        """
        self.wait_until_ready()
        engine = sa.engine.create_engine(self.__admin_url())
        return engine

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def stop(self):
        self.container.stop()

    def copy_file_to_container(self, src, dst_dir):
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w|") as t, open(src, "rb") as f:
            info = t.gettarinfo(fileobj=f)
            info.name = os.path.basename(src)
            t.addfile(info, f)
        self.container.put_archive(dst_dir, stream.getvalue())

    def run_command(self, cmd):
        return self.container.exec_run(cmd)

    def run_critical_command(self, cmd):
        """
        Executes a command in a container and raises an error if the command fails.

        Arguments:
        cmd (str): The command to run inside the container.

        Returns:
        tuple: A tuple containing the exit code (int) and output (bytes) from the command execution.

        Raises:
        RuntimeError: If the command exits with a non-zero status.
        """
        exit_code, output = self.container.exec_run(cmd)
        if exit_code != 0:
            logger.info(output.decode("utf-8"))
            raise RuntimeError(f"Failed to run command on container: {cmd}")
        return exit_code, output

    def run_sql_file_as_root(self, sql_filename):
        self.wait_until_ready()
        self.copy_file_to_container(sql_filename, "/var/lib/mysql-files/")
        self.run_command(
            f"mysql -h localhost -u root -p{self.info.get('password')} {self.info.get('dbname')} "
            f"-e 'source /var/lib/mysql-files/{os.path.basename(sql_filename)}'"
        )
        self.run_command(f"rm /var/lib/mysql-files/{os.path.basename(sql_filename)}")

    def load_schema(self, schema_filename):
        self.run_sql_file_as_root(schema_filename)

    def load_data_on_table(self, filename, table):
        self.wait_until_ready()
        self.copy_file_to_container(filename, "/var/lib/mysql-files/")
        self.run_command(
            f"mysql -h localhost -u root -p{self.info['password']} {self.info.get('dbname')} -e 'LOAD DATA INFILE \"/var/lib/mysql-files/{os.path.basename(filename)}\" INTO TABLE {table};'"
        )
        self.run_command(f"rm /var/lib/mysql-files/{os.path.basename(filename)}")

    def __init__(self, info={}, docker_url="unix:///var/run/docker.sock"):
        self.info = {
            "host": "localhost",
            "username": "someuser",
            "password": "somepasswd",
            "dbname": "somedb",
            "port": "3307",
            "name": None,
        }
        self.info.update(**info)
        self.client = docker.client.from_env()
        self.container = self.__start_db()
        self.engine = sa.create_engine(self.url())
