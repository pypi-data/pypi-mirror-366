import re
import docker
from typing import List, Union, Optional, Any
from docker.errors import DockerException, NotFound, APIError
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import os
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class DockerClient:
    def __init__(self, capture: bool = False):
        self.capture = capture
        self.captured_output: List[str] = []

    def _handle_docker_error(self, e: Exception, container_id: Optional[str] = None):
        """Handle Docker errors and display user-friendly messages"""
        if isinstance(e, NotFound):
            if container_id:
                console.print(
                    Panel(
                        f"[bold red]Container not found![/bold red]\n\n"
                        f"No container with name or ID '[cyan]{container_id}[/cyan]' was found.\n\n"
                        f"[dim]Try running:[/dim]\n"
                        f"• [bold]dtool ps -a[/bold] to see all containers\n"
                        f"• [bold]dtool ps[/bold] to see running containers",
                        title="🐳 Container Error",
                        border_style="red",
                    )
                )
            else:
                console.print(
                    Panel(
                        "[bold red]Resource not found![/bold red]\n\n"
                        "The requested Docker resource was not found.",
                        title="🐳 Docker Error",
                        border_style="red",
                    )
                )
        elif isinstance(e, APIError):
            console.print(
                Panel(
                    f"[bold red]Docker API Error![/bold red]\n\n"
                    f"{str(e)}\n\n"
                    f"[dim]This usually indicates a Docker daemon issue.[/dim]",
                    title="🐳 Docker Error",
                    border_style="red",
                )
            )
        elif isinstance(e, DockerException):
            console.print(
                Panel(
                    f"[bold red]Docker Error![/bold red]\n\n" f"{str(e)}",
                    title="🐳 Docker Error",
                    border_style="red",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold red]Unexpected Error![/bold red]\n\n" f"{str(e)}",
                    title="⚠️ Error",
                    border_style="red",
                )
            )

    def is_daemon_running(self) -> bool:
        """
        Check if the Docker daemon is running.
        Returns True if running, False otherwise.
        """
        try:
            client = docker.from_env()
            client.ping()
            return True
        except DockerException:
            return False

    def list_containers(
        self, all: bool = True, filter: Union[str, bool] = False, regex: bool = True
    ) -> List[Any]:
        try:
            client = docker.from_env()
            if filter and isinstance(filter, str):
                containers = client.containers.list(all=all)
                if not regex:
                    return [
                        c
                        for c in containers
                        if c.name == filter or c.id == filter or c.id.startswith(filter)
                    ]
                return [
                    c
                    for c in containers
                    if re.search(filter, c.name, re.IGNORECASE)
                    or re.search(filter, c.id, re.IGNORECASE)
                ]
            else:
                containers = client.containers.list(all=all)
                return list(containers)

        except (NotFound, APIError, DockerException) as e:
            self._handle_docker_error(e)
            return []
        except Exception as e:
            self._handle_docker_error(e)
            return []

    def print_containers_rich(self, containers: List):
        if not containers:
            console.print("[bold yellow]No containers found.[/bold yellow]")
            return

        table = Table(title="Docker Containers", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=12)
        table.add_column("Name", style="green")
        table.add_column("Image", style="blue")
        table.add_column("Status", style="yellow")
        table.add_column("Ports", style="dim")

        for container in containers:
            container_id = container.short_id
            name = container.name
            image = container.image.tags[0] if container.image.tags else container.image.id[:12]
            status = container.status

            ports = []
            if container.ports:
                for container_port, host_bindings in container.ports.items():
                    if host_bindings:
                        for binding in host_bindings:
                            host_port = binding["HostPort"]
                            port_mapping = f"{host_port}:{container_port}"
                            ports.append(port_mapping)
                    else:
                        ports.append(container_port)
            ports_str = ", ".join(ports) if ports else ""

            status_color = "green" if status == "running" else "red"

            table.add_row(
                container_id,
                name,
                image,
                f"[{status_color}]{status}[/{status_color}]",
                ports_str,
            )

        console.print(table)

    def find_container(self, container_pattern: str, all: bool = True):
        """
        Smart container finder with exact match and regex fallback
        Returns tuple (container, multiple_matches_list)
        """
        try:
            client = docker.from_env()
            containers = client.containers.list(all=all)

            if not containers:
                return None, []

            for container in containers:
                if (
                    container.id == container_pattern
                    or container.id.startswith(container_pattern)
                    or container.name == container_pattern
                ):
                    return container, []

            import re

            matches = []
            pattern = re.compile(container_pattern, re.IGNORECASE)

            for container in containers:
                if pattern.search(container.name) or pattern.search(container.id):
                    matches.append(container)

            if len(matches) == 1:
                return matches[0], []
            elif len(matches) > 1:
                return None, matches
            else:
                return None, []

        except (NotFound, APIError, DockerException) as e:
            self._handle_docker_error(e)
            return None, []
        except Exception as e:
            self._handle_docker_error(e)
            return None, []

    def interactive_container_selection(self, containers: List, action: str = "manage"):
        """
        Show interactive selection when multiple containers match
        """
        import questionary

        if not containers:
            return None

        choices = []
        for c in containers:
            status_emoji = "🟢" if c.status == "running" else "🔴"
            image_name = c.image.tags[0] if c.image.tags else c.image.id[:12]
            choices.append(f"{status_emoji} {c.name} ({c.short_id}) - {image_name}")

        choices.append("❌ Cancel")

        selected = questionary.select(
            f"Multiple containers found. Select one to {action}:",
            choices=choices,
            style=questionary.Style(
                [
                    ("qmark", "fg:#673ab7 bold"),
                    ("question", "bold"),
                    ("answer", "fg:#f44336 bold"),
                    ("pointer", "fg:#673ab7 bold"),
                    ("highlighted", "fg:#673ab7 bold"),
                    ("selected", "fg:#cc5454"),
                    ("separator", "fg:#cc5454"),
                    ("instruction", "fg:#abb2bf"),
                    ("text", "fg:#61afef"),
                ]
            ),
        ).ask()

        if selected == "❌ Cancel":
            return None

        for i, c in enumerate(containers):
            status_emoji = "🟢" if c.status == "running" else "🔴"
            image_name = c.image.tags[0] if c.image.tags else c.image.id[:12]
            container_display = f"{status_emoji} {c.name} ({c.short_id}) - {image_name}"
            if container_display == selected:
                return c

        return None

    def spawn_shell(self, container_pattern: str, shell: str = "/bin/sh"):
        try:
            container, multiple_matches = self.find_container(container_pattern, all=False)

            if container is None and not multiple_matches:
                console.print(
                    Panel(
                        f"[bold red]No container found![/bold red]\n\n"
                        f"No running container matches '[cyan]{container_pattern}[/cyan]'.\n\n"
                        f"[dim]Try:[/dim]\n"
                        f"• [bold]dtool ps[/bold] to see running containers\n"
                        f"• [bold]dtool ps -a[/bold] to see all containers",
                        title="🐳 Container Search",
                        border_style="red",
                    )
                )
                return

            if multiple_matches:
                container = self.interactive_container_selection(multiple_matches, "spawn shell in")
                if container is None:
                    console.print("[yellow]Operation cancelled.[/yellow]")
                    return

            self._spawn_shell_in_container(container, shell)

        except (NotFound, APIError, DockerException) as e:
            self._handle_docker_error(e, container_pattern)
        except Exception as e:
            self._handle_docker_error(e, container_pattern)

    def _spawn_shell_in_container(self, container, shell: str = "/bin/sh"):
        """Internal method to spawn shell in a specific container object"""
        try:
            if container.status != "running":
                console.print(
                    Panel(
                        f"[bold red]Container not running![/bold red]\n\n"
                        f"Container '[cyan]{container.name}[/cyan]' ([dim]{container.short_id}[/dim]) is currently [red]{container.status}[/red].\n\n"
                        f"[dim]Try starting it first:[/dim]\n"
                        f"• [bold]dtool start {container.name}[/bold]",
                        title="🐳 Container Status",
                        border_style="red",
                    )
                )
                return

            console.print(
                f"\n[bold green]Entering {shell} in container[/bold green] [cyan]{container.name}[/cyan] [dim]({container.short_id})[/dim]\n"
            )

            cmd = ["docker", "exec", "-it", container.id, shell]

            os.execvp("docker", cmd)

        except Exception as e:
            self._handle_docker_error(e)

    def exec_cmd(self, container_pattern: str, command: str):
        try:
            container, multiple_matches = self.find_container(container_pattern, all=False)

            if container is None and not multiple_matches:
                console.print(
                    Panel(
                        f"[bold red]No container found![/bold red]\n\n"
                        f"No running container matches '[cyan]{container_pattern}[/cyan]'.\n\n"
                        f"[dim]Try:[/dim]\n"
                        f"• [bold]dtool ps[/bold] to see running containers\n"
                        f"• [bold]dtool ps -a[/bold] to see all containers",
                        title="🐳 Container Search",
                        border_style="red",
                    )
                )
                return

            if multiple_matches:
                container = self.interactive_container_selection(
                    multiple_matches, "execute command in"
                )
                if container is None:
                    console.print("[yellow]Operation cancelled.[/yellow]")
                    return

            self._exec_cmd_in_container(container, command)

        except (NotFound, APIError, DockerException) as e:
            self._handle_docker_error(e, container_pattern)
        except Exception as e:
            self._handle_docker_error(e, container_pattern)

    def _exec_cmd_in_container(self, container, command: str):
        """Internal method to execute command in a specific container object"""
        try:
            if container.status != "running":
                console.print(
                    Panel(
                        f"[bold yellow]Container not running![/bold yellow]\n\n"
                        f"Container '[cyan]{container.name}[/cyan]' ([dim]{container.short_id}[/dim]) is currently [red]{container.status}[/red].\n\n"
                        f"[dim]Try starting it first:[/dim]\n"
                        f"• [bold]dtool start {container.name}[/bold]",
                        title="🐳 Container Status",
                        border_style="yellow",
                    )
                )
                return

            client = docker.from_env()
            exec_instance = client.api.exec_create(
                container.id, command.split(), tty=True, stdin=True
            )
            output = client.api.exec_start(exec_instance["Id"], stream=True)
            for line in output:
                print(line.decode("utf-8"), end="")
                if self.capture:
                    self.captured_output.append(line.decode("utf-8"))
        except Exception as e:
            self._handle_docker_error(e)

    def fetch_logs(self, container_pattern: str, follow: bool = False):
        try:
            container, multiple_matches = self.find_container(container_pattern, all=True)

            if container is None and not multiple_matches:
                console.print(
                    Panel(
                        f"[bold red]No container found![/bold red]\n\n"
                        f"No container matches '[cyan]{container_pattern}[/cyan]'.\n\n"
                        f"[dim]Try:[/dim]\n"
                        f"• [bold]dtool ps -a[/bold] to see all containers",
                        title="🐳 Container Search",
                        border_style="red",
                    )
                )
                return

            if multiple_matches:
                container = self.interactive_container_selection(multiple_matches, "view logs from")
                if container is None:
                    console.print("[yellow]Operation cancelled.[/yellow]")
                    return

            self._fetch_logs_from_container(container, follow)

        except (NotFound, APIError, DockerException) as e:
            self._handle_docker_error(e, container_pattern)
        except Exception as e:
            self._handle_docker_error(e, container_pattern)

    def _fetch_logs_from_container(self, container, follow: bool = False):
        """Internal method to fetch logs from a specific container object"""
        try:
            if container.status != "running":
                console.print(
                    Panel(
                        f"[bold yellow]Container not running![/bold yellow]\n\n"
                        f"Container '[cyan]{container.name}[/cyan]' ([dim]{container.short_id}[/dim]) is currently [red]{container.status}[/red].\n\n"
                        f"[dim]Note: You can still view logs from stopped containers.[/dim]",
                        title="🐳 Container Status",
                        border_style="yellow",
                    )
                )

            if follow:
                logs = container.logs(stream=True, follow=True)
                for log in logs:
                    print(log.decode("utf-8"), end="")
            else:
                logs = container.logs()
                print(logs.decode("utf-8"), end="")
        except Exception as e:
            self._handle_docker_error(e)

    def start_container(self, container_id: str):
        try:
            client = docker.from_env()
            container = client.containers.get(container_id)
            if container.status == "running":
                console.print(
                    Panel(
                        f"[bold yellow]Container already running![/bold yellow]\n\n"
                        f"Container '[cyan]{container.name}[/cyan]' ([dim]{container.short_id}[/dim]) is already running.",
                        title="🐳 Container Status",
                        border_style="yellow",
                    )
                )
                return

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task(f"Starting container {container.name}...", total=None)
                container.start()
                progress.update(
                    task,
                    description=f"[bold green]✓[/bold green] Started container {container.name}",
                )

            console.print(
                f"[bold green]Started container[/bold green] [cyan]{container.name}[/cyan] [dim]({container.short_id})[/dim]"
            )

            container.reload()
            self.print_containers_rich(containers=[container])
        except (NotFound, APIError, DockerException) as e:
            self._handle_docker_error(e, container_id)
        except Exception as e:
            self._handle_docker_error(e, container_id)

    def stop_container(self, container_id: str, force: bool = False):
        try:
            client = docker.from_env()
            container = client.containers.get(container_id)
            if container.status != "running":
                console.print(
                    Panel(
                        f"[bold yellow]Container not running![/bold yellow]\n\n"
                        f"Container '[cyan]{container.name}[/cyan]' ([dim]{container.short_id}[/dim]) is currently [red]{container.status}[/red].",
                        title="🐳 Container Status",
                        border_style="yellow",
                    )
                )
                return

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task(f"Stopping container {container.name}...", total=None)
                container.stop(force=force)
                progress.update(
                    task,
                    description=f"[bold green]✓[/bold green] Stopped container {container.name}",
                )

            console.print(
                f"[bold red]Stopped container[/bold red] [cyan]{container.name}[/cyan] [dim]({container.short_id})[/dim]"
            )

            container.reload()
            self.print_containers_rich(containers=[container])
        except (NotFound, APIError, DockerException) as e:
            self._handle_docker_error(e, container_id)
        except Exception as e:
            self._handle_docker_error(e, container_id)

    def restart_container(self, container_id: str, force: bool = False):
        try:
            client = docker.from_env()
            container = client.containers.get(container_id)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task(f"Restarting container {container.name}...", total=None)
                container.restart(force=force)
                progress.update(
                    task,
                    description=f"[bold green]✓[/bold green] Restarted container {container.name}",
                )

            console.print(
                f"[bold green]Restarted container[/bold green] [cyan]{container.name}[/cyan] [dim]({container.short_id})[/dim]"
            )

            container.reload()
            self.print_containers_rich(containers=[container])
        except (NotFound, APIError, DockerException) as e:
            self._handle_docker_error(e, container_id)
        except Exception as e:
            self._handle_docker_error(e, container_id)

    def remove_container(self, container_id: str, force: bool = False):
        try:
            client = docker.from_env()
            container = client.containers.get(container_id)
            if container.status == "running" and not force:
                console.print(
                    Panel(
                        f"[bold red]Container is running![/bold red]\n\n"
                        f"Container '[cyan]{container.name}[/cyan]' ([dim]{container.short_id}[/dim]) is currently running.\n\n"
                        f"[dim]Options:[/dim]\n"
                        f"• [bold]dtool stop {container_id}[/bold] then remove it\n"
                        f"• Use [bold]--force[/bold] flag to force removal",
                        title="🐳 Container Status",
                        border_style="red",
                    )
                )
                return

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task(f"Removing container {container.name}...", total=None)
                container.remove(force=force)
                progress.update(
                    task,
                    description=f"[bold green]✓[/bold green] Removed container {container.name}",
                )

            console.print(
                f"[bold red]Removed container[/bold red] [cyan]{container.name}[/cyan] [dim]({container.short_id})[/dim]"
            )
        except (NotFound, APIError, DockerException) as e:
            self._handle_docker_error(e, container_id)
        except Exception as e:
            self._handle_docker_error(e, container_id)
