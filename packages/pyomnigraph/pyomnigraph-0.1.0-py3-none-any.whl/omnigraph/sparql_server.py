"""
Created on 2025-05-27

@author: wf
"""
import psutil
import re
import time
import traceback
import webbrowser
from pathlib import Path
from typing import List

import requests
from lodstorage.query import Endpoint
from lodstorage.rdf_format import RdfFormat
from lodstorage.sparql import SPARQL
from tqdm import tqdm

from basemkit.docker_util import DockerUtil
from lodstorage.prefix_config import PrefixConfigs
from omnigraph.server_config import ServerConfig, ServerEnv, ServerLifecycleState, ServerStatus
from basemkit.shell import ShellResult
from omnigraph.software import SoftwareList


class Response:
    """
    wrapper for responses including errors
    """

    @property
    def success(self) -> bool:
        if self.error is not None:
            return False
        if self.response is not None:
            return self.response.status_code in [200, 204]
        return False

    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error


class SparqlServer:
    """
    Base class for dockerized SPARQL servers
    """

    def __init__(self, config: ServerConfig, env: ServerEnv):
        """
        Initialize the SPARQL server manager.

        """
        self.env=env
        self.log = env.log
        self.config = config
        self.name = self.config.name
        self.debug = env.debug
        self.verbose = env.verbose
        self.shell = env.shell
        self.rdf_format = RdfFormat.by_label(self.config.rdf_format)
        self.current_status = None
        self.docker_util = DockerUtil(
            shell=self.shell,
            container_name=self.config.container_name,
            log=self.log,
            verbose=self.verbose,
            debug=self.debug
        )

        # Subclasses must set these URLs
        if self.config.sparql_url:
            is_fuseki = self.config.server == "jena"
            self.sparql = SPARQL(self.config.sparql_url, isFuseki=is_fuseki)
            if (
                hasattr(self.config, "auth_password")
                and self.config.auth_password
                and hasattr(self.config, "auth_user")
                and self.config.auth_user
            ):
                self.sparql.addAuthentication(self.config.auth_user, self.config.auth_password)

    @property
    def full_name(self) -> str:
        full_name = f"{self.name} {self.config.container_name}"
        return full_name

    @property
    def flag(self) -> str:
        flag = "🟢️" if self.config.active else "🛑"
        if self.current_status:
            state = self.current_status.at.value
            flag += str(state)
        return flag

    def as_endpoint_conf(self, prefix_configs: PrefixConfigs, prefix_sets: List[str]) -> Endpoint:
        """
        Convert server configuration to Endpoint configuration.

        Args:
            prefix_configs: PrefixConfigs instance with prefix definitions
            prefix_sets: List of prefix set names to include

        Returns:
            Endpoint: Endpoint configuration object
        """
        endpoint = Endpoint()

        # Basic endpoint properties
        endpoint.name = self.config.name
        endpoint.lang = "sparql"
        endpoint.endpoint = self.config.sparql_url
        endpoint.website = self.config.web_url
        endpoint.database = self.config.server
        endpoint.method = "POST"

        # Authentication if configured
        if (
            hasattr(self.config, "auth_user")
            and self.config.auth_user
            and hasattr(self.config, "auth_password")
            and self.config.auth_password
        ):
            endpoint.auth = "BASIC"
            endpoint.user = self.config.auth_user
            endpoint.password = self.config.auth_password

        # Get prefixes from provided prefix sets
        declarations = prefix_configs.get_selected_declarations(prefix_sets)
        endpoint.prefixes = declarations

        return endpoint

    def avail_mem_gb(self)->float:
        avail_mem = psutil.virtual_memory().available / (1024 ** 3)
        return avail_mem

    def handle_exception(self, context: str, ex: Exception):
        """
        handle the given exception
        """
        container_name = self.config.container_name
        self.log.log("❌", container_name, f"Exception {context}: {ex}")
        if self.debug:
            # extract exception type, and trace back
            ex_type = type(ex)
            ex_tb = ex.__traceback__
            # print exception stack details
            traceback.print_exception(ex_type, ex, ex_tb)

    def make_request(self, method: str, url: str, **kwargs) -> Response:
        """
        Helper function for making HTTP requests with consistent error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments for requests

        Returns:
            Response
        """
        try:
            #  add auth if we have auth_password and auth_user
            if (
                hasattr(self.config, "auth_password")
                and self.config.auth_password
                and hasattr(self.config, "auth_user")
                and self.config.auth_user
            ):
                kwargs.setdefault("auth", (self.config.auth_user, self.config.auth_password))
            # for Jena Fuseki we do this via url
            # Only set timeout if not already provided
            kwargs.setdefault("timeout", self.config.timeout)
            response = requests.request(method, url, **kwargs)
            response = Response(response)
        except Exception as ex:
            self.handle_exception(f"request {url}", ex)
            response = Response(None, ex)
        return response

    def get_web_url(self) -> str:
        """
        Return the service-specific Web UI URL.
        Subclasses may override.
        """
        return self.config.web_url

    def webui(self):
        """
        open my webui
        """
        web_url = self.get_web_url()
        webbrowser.open(web_url)

    def status_info(self) -> str:
        """
        Return one-line summary of server status e.g. for CLI use.
        """
        self.status()
        summary = self.current_status.get_summary(self.debug)
        info = f"{self.flag}{summary}"
        return info

    def status(self) -> ServerStatus:
        """
        Check server status using a single docker inspect call.

        Returns:
            ServerStatus: object with detailed container state
        """
        server_status = ServerStatus(at=ServerLifecycleState.UNKNOWN)
        state = self.docker_util.inspect()

        if state:
            server_status.exists = True
            server_status.running = state.get("Running", False)
            server_status.docker_status = state.get("Status")
            server_status.docker_exit_code = state.get("ExitCode")
            self.refresh_logs(server_status)
            if server_status.running:
                server_status.at = ServerLifecycleState.UP
                self.refresh_logs(server_status)
            else:
                if server_status.docker_status == "exited" and server_status.docker_exit_code not in (0, None):
                    server_status.at = ServerLifecycleState.ERROR
                elif server_status.docker_status == "created":
                    server_status.at = ServerLifecycleState.STARTING
                else:
                    server_status.at = ServerLifecycleState.STOPPED
        else:
            server_status.exists = False
            server_status.running = False

        self.current_status = server_status
        return server_status

    def refresh_logs(self, server_status=ServerStatus):
        """
        refresh the logs for the given server status
        """
        proc = self.shell.run(f"docker logs {self.config.container_name}", tee=False)
        logs = f"stdout:{proc.stdout}\nstderr:{proc.stderr}"
        server_status.logs = logs

    def add_triple_count2_server_status(self, server_status=ServerStatus):
        """
        add triple count to server status
        """
        try:
            triple_count = self.count_triples()
            server_status.triple_count = triple_count
        except Exception as ex:
            server_status.error = ex

    # delegates
    def run_shell_command(self, command: str, success_msg: str = None, error_msg: str = None) -> ShellResult:
        """
        Helper function for running shell commands with consistent error handling.
        """
        return self.docker_util.run_shell_command(command, success_msg, error_msg)

    def docker_cmd(self, cmd: str, options: str = "", args: str = "") -> str:
        """create the given docker command with the given options"""
        return self.docker_util.docker_cmd(cmd, options, args)

    def run_docker_cmd(self, cmd: str, options: str = "", args: str = "") -> ShellResult:
        """run the given docker commmand with the given options"""
        return self.docker_util.run_docker_cmd(cmd, options, args)

    def logs(self) -> ShellResult:
        """show the logs of the container"""
        return self.docker_util.logs()

    def docker_info(self) -> ShellResult:
        """Check if Docker is responsive on the host system."""
        return self.docker_util.docker_info()

    def stop(self) -> ShellResult:
        """stop the server container"""
        return self.docker_util.stop()

    def rm(self) -> ShellResult:
        """remove the server container."""
        return self.docker_util.rm()

    def bash(self) -> bool:
        """bash into the server container."""
        return self.docker_util.bash()

    def pre_create(self):
        """
        abstract pre docker create step
        implement a special version if need be
        """

    def post_create(self):
        """
        abstract post docker create step
        implement a special version if need be
        """

    def docker_create(self) -> bool:
        """
        Create and start a new Docker container for the configured server.

        Returns:
            bool: True if the container was created and is running, False otherwise.
        """
        container_name = self.config.container_name
        server_name = self.config.name
        self.log.log("✅", container_name, f"Creating new {server_name} container {container_name}...")
        try:
            self.pre_create()
            operation_success = True
        except Exception as ex:
            self.handle_exception("pre_create", ex)
            operation_success = False
        if operation_success:
            base_data_dir = self.config.base_data_dir
            create_cmd = self.config.get_docker_run_command(data_dir=base_data_dir)
            create_result = self.docker_util.run_shell_command(
                create_cmd,
                error_msg=f"Failed to create container {container_name}",
            )

            operation_success = create_result.success
            container_id = create_result.proc.stdout.strip()

            if not re.fullmatch(r"[0-9a-f]{12,}", container_id):
                self.log.log(
                    "❌",
                    container_name,
                    f"Creating new {server_name} container failed – invalid container ID '{container_id}' from command: {create_cmd}",
                )
                operation_success = False

        if operation_success:
            try:
                self.post_create()
            except Exception as ex:
                self.handle_exception("pre_create", ex)
                operation_success = False

        if operation_success:
            server_status = self.status()
            if not server_status.running:
                self.log.log(
                    "❌",
                    container_name,
                    f"Container exited with status='{server_status.docker_status}', exit_code={server_status.docker_exit_code}",
                )
                if server_status.logs:
                    self.log.log("ℹ️", container_name, f"Logs:\n{server_status.logs.strip()}")
                operation_success = False

        return operation_success

    def start(self, show_progress: bool = True) -> bool:
        """
        Start SPARQL server in Docker container.

        Args:
            show_progress: Show progress bar while waiting

        Returns:
            True if started successfully
        """
        container_name = self.config.container_name
        server_name = self.config.name
        start_success = False
        try:
            docker_status = self.docker_info()
            operation_success = docker_status.success
            if operation_success:
                server_status = self.status()

                if server_status.running:
                    self.log.log(
                        "✅",
                        container_name,
                        f"Container {container_name} is already running",
                    )
                    operation_success = True
                elif server_status.exists:
                    self.log.log(
                        "✅",
                        container_name,
                        f"Container {container_name} exists, starting...",
                    )
                    start_cmd = f"docker start {container_name}"
                    start_result = self.docker_util.run_shell_command(
                        start_cmd,
                        error_msg=f"Failed to start container {container_name}",
                    )
                    operation_success = start_result
                else:
                    operation_success = self.docker_create()

            if operation_success:
                start_success = self.wait_until_ready(show_progress=show_progress)
            else:
                start_success = False

        except Exception as ex:
            self.handle_exception(f"starting {server_name}", ex)
            start_success = False
        return start_success

    def count_triples(self) -> int:
        """
        Count total triples in the SPARQL server.

        Returns:
            Number of triples
        """
        count_query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
        try:
            result = self.sparql.getValue(count_query, "count")
            triple_count = int(result) if result else 0
        except Exception as ex:
            self.handle_exception("count_triples", ex)
            triple_count = -1
        return triple_count

    def wait_until_ready(self, show_progress: bool = False) -> bool:
        """
        Wait for server to be ready.

        Args:
            timeout: Maximum seconds to wait
            show_progress: Show progress bar while waiting

        Returns:
            True if ready within timeout
        """
        container_name = self.config.container_name
        base_url = self.config.base_url
        timeout = self.config.ready_timeout

        self.log.log(
            "✅",
            container_name,
            f"Waiting for {self.full_name} to start ... ",
        )

        pbar = None
        if show_progress:
            pbar = tqdm(total=timeout, desc=f"Waiting for {self.full_name}", unit="s")

        ready_status = False
        for secs in range(timeout):
            server_status = self.status()
            if server_status.at == ServerLifecycleState.READY:
                if show_progress and pbar:
                    pbar.close()
                self.log.log(
                    "✅",
                    container_name,
                    f"{self.full_name} ready at {base_url} after {secs}s",
                )
                ready_status = True
                break

            if show_progress and pbar:
                pbar.update(1)
            time.sleep(1)

        if not ready_status:
            if show_progress and pbar:
                pbar.close()
            self.log.log(
                "⚠️",
                container_name,
                f"Timeout waiting for {self.full_name} to start after {timeout}s",
            )

        return ready_status

    def get_clear_query(self) -> str:
        """
        the clear query to be used
        may be overriden by specific SPARQL server implementations
        """
        clear_query = "DELETE { ?s ?p ?o } WHERE { ?s ?p ?o }"
        return clear_query

    def clear(self) -> int:
        """
        delete all triples
        """
        container_name = self.config.container_name
        count_triples = self.count_triples()
        msg = f"deleting {count_triples} triples ..."
        protected=count_triples >= self.config.unforced_clear_limit
        if protected and not self.env.force:
            self.log.log("❌", container_name, f"{msg} needs force option")
        else:
            clear_query = self.get_clear_query()
            try:
                _reponse, ex = self.sparql.insert(clear_query)
                if ex:
                    self.handle_exception("DELETE", ex)
                new_count = self.count_triples()
                if new_count == 0:
                    self.log.log("✅", container_name, f"deleted {count_triples} triples")
                else:
                    self.log.log("❌", container_name, f"delete failed: {new_count} triples remain")
                count_triples = new_count
            except Exception as ex:
                self.handle_exception("clear triples", ex)
        return count_triples

    def upload_request(self, file_content: bytes) -> Response:
        """Default upload request for Blazegraph-style servers."""
        response = self.make_request(
            "POST",
            self.config.upload_url,
            headers={"Content-Type": self.rdf_format.mime_type},
            data=file_content,
            timeout=self.config.upload_timeout,
        )
        return response

    def load_file(self, filepath: str, upload_request=None) -> bool:
        """
        Load a single RDF file into the RDF server.
        """
        container_name = self.config.container_name
        load_success = False

        if upload_request is None:
            upload_request_callback = self.upload_request
        else:
            upload_request_callback = upload_request

        try:
            with open(filepath, "rb") as f:
                file_content = f.read()

            response = upload_request_callback(file_content)

            if response.success:  # Changed from result["success"]
                self.log.log("✅", container_name, f"Loaded {filepath}")
                load_success = True
            else:
                if response.error:
                    error_msg = str(response.error)
                else:
                    status_code = response.response.status_code
                    content = response.response.text
                    error_msg = f"HTTP {status_code} → {content}"
                self.log.log("❌", container_name, f"Failed to load {filepath}: {error_msg}")
                load_success = False

        except Exception as ex:
            self.handle_exception(f"loading {filepath}", ex)
            load_success = False

        return load_success

    def load_dump_files(self, file_pattern: str = None) -> int:
        """
        Load all dump files matching pattern.

        Args:
            file_pattern: Glob pattern for dump files
            use_bulk: Use bulk loader if True, individual files if False

        Returns:
            Number of files loaded successfully
        """
        dump_path: Path = Path(self.config.dumps_dir)
        if file_pattern is None:
            file_pattern = f"*{self.rdf_format.extension}"
        files = sorted(dump_path.glob(file_pattern))
        loaded_count = 0
        container_name = self.config.container_name

        if not files:
            self.log.log("⚠️", container_name, f"No files found matching pattern: {file_pattern}")
        else:
            self.log.log("✅", container_name, f"Found {len(files)} files to load")
            pbar = tqdm(files, dynamic_ncols=True)
            for filepath in pbar:
                pbar.set_description(f"Mem: {self.avail_mem_gb():.1f} GB → {filepath.name}")
                file_result = self.load_file(filepath)
                if file_result:
                    loaded_count += 1
                else:
                    self.log.log("❌", container_name, f"Failed to load: {filepath}")

        return loaded_count

    def check_needed_software(self) -> int:
        """
        Check if needed software for this server configuration is installed
        """
        container_name = self.config.container_name
        if self.config.needed_software is None:
            return
        software_list = SoftwareList.from_dict2(self.config.needed_software)  # @UndefinedVariable
        missing = software_list.check_installed(self.log, self.shell, verbose=True)
        if missing > 0:
            self.log.log("❌", container_name, "Please install the missing commands before running this script.")
        return missing
