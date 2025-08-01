"""Agent Service for CLI Operations.

This module provides high-level Agent service operations
for CLI commands, wrapping Docker Compose and process management functionality.
"""

import builtins
import contextlib
import os
import secrets
import signal
import subprocess
import time
from pathlib import Path

from docker.lib.compose_manager import DockerComposeManager


class AgentService:
    """High-level Agent service operations for CLI.

    Provides user-friendly Agent container and process management
    with integrated workspace validation and service orchestration.
    """

    def __init__(self) -> None:
        self.compose_manager = DockerComposeManager()
        self.agent_compose_file = "docker/agent/docker-compose.yml"
        self.agent_port = 38886
        self.agent_postgres_port = 35532
        self.logs_dir = Path("logs")
        self.pid_file = self.logs_dir / "agent-server.pid"
        self.log_file = self.logs_dir / "agent-server.log"

    def install_agent_environment(self, workspace_path: str) -> bool:
        """Install complete agent environment with isolated ports and database.

        Args:
            workspace_path: Path to workspace directory

        Returns:
            True if installation successful, False otherwise
        """
        workspace = Path(workspace_path).resolve()
        print(f"🤖 Installing agent environment in workspace: {workspace}")
        
        if not self._validate_workspace(workspace, check_env=False):
            print("❌ Workspace validation failed")
            return False

        print("✅ Workspace validation passed")

        # Create agent environment file
        print("📝 Creating agent environment file...")
        if not self._create_agent_env_file(str(workspace)):
            print("❌ Failed to create agent environment file")
            return False

        print("✅ Agent environment file created")

        # Setup agent PostgreSQL
        print("🐘 Setting up agent PostgreSQL...")
        if not self._setup_agent_postgres(str(workspace)):
            print("❌ Failed to setup agent PostgreSQL")
            return False

        print("✅ Agent PostgreSQL setup completed")

        # Generate agent API key
        print("🔑 Generating agent API key...")
        if self._generate_agent_api_key(str(workspace)):
            print("✅ Agent environment installation completed successfully!")
            return True
        else:
            print("❌ Failed to generate agent API key")
            return False

    def serve_agent(self, workspace_path: str) -> bool:
        """Start agent server in background (non-blocking).

        Args:
            workspace_path: Path to workspace directory

        Returns:
            True if started successfully, False otherwise
        """
        workspace = Path(workspace_path).resolve()
        print(f"🚀 Starting agent server in workspace: {workspace}")
        
        if not self._validate_agent_environment(workspace):
            print("❌ Agent environment validation failed")
            print("💡 Run 'uvx automagik-hive --agent-install' first to set up the environment")
            return False

        # Check if already running
        if self._is_agent_running():
            pid = self._get_agent_pid()
            print(f"✅ Agent server is already running (PID: {pid}, Port: {self.agent_port})")
            return True

        return self._start_agent_background(str(workspace))

    def stop_agent(self, workspace_path: str | None = None) -> bool:  # noqa: ARG002
        """Stop agent server cleanly.

        Args:
            workspace_path: Path to workspace directory (optional)

        Returns:
            True if stopped successfully, False otherwise
        """
        if not self._is_agent_running():
            print("🛑 Agent server is not running")
            return True
            
        if self._stop_agent_background():
            print("✅ Agent server stopped successfully")
            return True
        else:
            print("❌ Failed to stop agent server")
            return False

    def restart_agent(self, workspace_path: str) -> bool:
        """Restart agent server.

        Args:
            workspace_path: Path to workspace directory

        Returns:
            True if restarted successfully, False otherwise
        """
        self._stop_agent_background()
        time.sleep(2)
        return self.serve_agent(workspace_path)

    def show_agent_logs(
        self,
        workspace_path: str | None = None,  # noqa: ARG002
        tail: int = 50,
    ) -> bool:
        """Show agent logs (non-blocking).

        Args:
            workspace_path: Path to workspace directory (optional)
            tail: Number of lines to show

        Returns:
            True if logs displayed, False otherwise
        """
        if self.log_file.exists():
            try:
                result = subprocess.run(
                    ["tail", f"-{tail}", str(self.log_file)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    print(f"\n📝 Agent Server Logs (last {tail} lines):")
                    print("=" * 50)
                    if result.stdout.strip():
                        print(result.stdout.strip())
                    else:
                        print("No log content available")
                    return True
                else:
                    print(f"❌ Error reading log file (exit code: {result.returncode})")
                    return False
            except (OSError, subprocess.SubprocessError, Exception) as e:
                print(f"❌ Error executing tail command: {e}")
                return False
        else:
            print(f"❌ Log file not found: {self.log_file}")
            return False

    def get_agent_status(self, workspace_path: str | None = None) -> dict[str, str]:
        """Get agent environment status.

        Args:
            workspace_path: Path to workspace directory (optional)

        Returns:
            Dict with service status information
        """
        status = {}

        # Check agent server status
        if self._is_agent_running():
            pid = self._get_agent_pid()
            status["agent-server"] = f"✅ Running (PID: {pid}, Port: {self.agent_port})"
        else:
            status["agent-server"] = "🛑 Stopped"

        # Check agent postgres status
        workspace = workspace_path or "."
        postgres_status = self.compose_manager.get_service_status(
            "postgres-agent", str(Path(workspace).resolve())
        )

        if postgres_status.name == "RUNNING":
            status["agent-postgres"] = f"✅ Running (Port: {self.agent_postgres_port})"
        else:
            status["agent-postgres"] = "🛑 Stopped"

        return status

    def reset_agent_environment(self, workspace_path: str) -> bool:
        """Reset agent environment (destructive reinstall).

        Args:
            workspace_path: Path to workspace directory

        Returns:
            True if reset successful, False otherwise
        """
        workspace = Path(workspace_path).resolve()

        # Stop everything first
        self._cleanup_agent_environment(str(workspace))

        # Reinstall
        return self.install_agent_environment(str(workspace))

    def _validate_workspace(self, workspace: Path, check_env: bool = True) -> bool:  # noqa: ARG002
        """Validate workspace directory and required files."""
        if not workspace.exists():
            print(f"❌ Workspace directory does not exist: {workspace}")
            return False

        if not workspace.is_dir():
            print(f"❌ Workspace path is not a directory: {workspace}")
            return False

        # Check for agent docker-compose.yml
        agent_compose_file = workspace / self.agent_compose_file
        if not agent_compose_file.exists():
            print(f"❌ Agent docker-compose file not found: {agent_compose_file}")
            return False

        # Check for .env.example file
        env_example = workspace / ".env.example"
        if not env_example.exists():
            print(f"❌ .env.example file not found: {env_example}")
            return False

        return True

    def _validate_agent_environment(self, workspace: Path) -> bool:
        """Validate agent environment is properly set up."""
        agent_env = workspace / ".env.agent"
        if not agent_env.exists():
            print(f"❌ Agent environment file missing: {agent_env}")
            return False

        # Check if venv exists
        venv_path = workspace / ".venv"
        if not venv_path.exists():
            print(f"❌ Python virtual environment missing: {venv_path}")
            return False
            
        return True

    def _create_agent_env_file(self, workspace_path: str) -> bool:
        """Create .env.agent file with proper port configuration."""
        workspace = Path(workspace_path)
        env_example = workspace / ".env.example"
        env_agent = workspace / ".env.agent"

        try:
            if not env_example.exists():
                return False
        except (OSError, PermissionError):
            return False

        try:
            # Copy .env.example to .env.agent
            with open(env_example) as src, open(env_agent, "w") as dst:
                content = src.read()
                # Update ports for agent environment
                content = content.replace(
                    "HIVE_API_PORT=8886", f"HIVE_API_PORT={self.agent_port}"
                )
                content = content.replace(
                    "localhost:5532", f"localhost:{self.agent_postgres_port}"
                )
                content = content.replace("/hive", "/hive_agent")
                content = content.replace(
                    "http://localhost:8886", f"http://localhost:{self.agent_port}"
                )
                dst.write(content)

            return True
        except OSError:
            return False

    def _setup_agent_postgres(self, workspace_path: str) -> bool:
        """Setup agent PostgreSQL container."""
        workspace = Path(workspace_path)

        # Generate credentials
        if not self._generate_agent_postgres_credentials(str(workspace)):
            return False

        # Extract database URL from .env.agent
        env_agent = workspace / ".env.agent"
        try:
            with open(env_agent) as f:
                content = f.read()

            # Find database URL
            for line in content.split("\n"):
                if line.startswith("HIVE_DATABASE_URL="):
                    db_url = line.split("=", 1)[1]
                    break
            else:
                return False

            # Parse database URL
            # postgresql+psycopg://user:pass@localhost:35532/hive_agent
            url_part = db_url.split("://", 1)[1]  # user:pass@localhost:35532/hive_agent
            credentials_part = url_part.split("@", 1)[0]  # user:pass
            postgres_user = credentials_part.split(":", 1)[0]
            postgres_password = credentials_part.split(":", 1)[1]
            postgres_db = url_part.split("/")[-1]  # hive_agent

            # Set environment variables for docker-compose
            env = os.environ.copy()
            env.update(
                {
                    "POSTGRES_USER": postgres_user,
                    "POSTGRES_PASSWORD": postgres_password,
                    "POSTGRES_DB": postgres_db,
                    "POSTGRES_UID": str(os.getuid() if hasattr(os, "getuid") else 1000),
                    "POSTGRES_GID": str(os.getgid() if hasattr(os, "getgid") else 1000),
                }
            )

            # Create data directory
            data_dir = workspace / "data" / "postgres-agent"
            data_dir.mkdir(parents=True, exist_ok=True)

            # Start container
            cmd = [
                "docker",
                "compose",
                "-f",
                self.agent_compose_file,
                "up",
                "-d",
                "postgres-agent",
            ]

            result = subprocess.run(
                cmd, cwd=workspace, env=env, capture_output=True, text=True, check=False
            )

            return result.returncode == 0

        except OSError:
            return False

    def _generate_agent_postgres_credentials(self, workspace_path: str) -> bool:
        """Generate PostgreSQL credentials for agent environment."""
        workspace = Path(workspace_path)
        env_agent = workspace / ".env.agent"

        try:
            # Generate random credentials
            postgres_user = secrets.token_urlsafe(12)[:16]
            postgres_pass = secrets.token_urlsafe(12)[:16]
            postgres_db = "hive_agent"

            # Update .env.agent file
            with open(env_agent) as f:
                content = f.read()

            # Replace database URL
            new_url = f"postgresql+psycopg://{postgres_user}:{postgres_pass}@localhost:{self.agent_postgres_port}/{postgres_db}"

            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("HIVE_DATABASE_URL="):
                    lines[i] = f"HIVE_DATABASE_URL={new_url}"
                    break

            with open(env_agent, "w") as f:
                f.write("\n".join(lines))

            return True
        except OSError:
            return False

    def _generate_agent_api_key(self, workspace_path: str) -> bool:
        """Generate API key for agent environment."""
        workspace = Path(workspace_path)
        env_agent = workspace / ".env.agent"

        try:
            api_key = f"hive_agent_{secrets.token_urlsafe(32)}"

            # Update .env.agent file
            with open(env_agent) as f:
                content = f.read()

            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("HIVE_API_KEY="):
                    lines[i] = f"HIVE_API_KEY={api_key}"
                    break

            with open(env_agent, "w") as f:
                f.write("\n".join(lines))

            return True
        except OSError:
            return False

    def _start_agent_background(self, workspace_path: str) -> bool:
        """Start agent server in background."""
        workspace = Path(workspace_path)
        self.logs_dir.mkdir(exist_ok=True)

        try:
            # Prepare environment
            env = os.environ.copy()

            # Load .env.agent variables
            env_agent = workspace / ".env.agent"
            with open(env_agent) as f:
                for env_line in f:
                    stripped_line = env_line.strip()
                    if (
                        stripped_line
                        and not stripped_line.startswith("#")
                        and "=" in stripped_line
                    ):
                        key, value = stripped_line.split("=", 1)
                        env[key] = value

            # Start server process
            with open(self.log_file, "w") as log_f:
                process = subprocess.Popen(
                    ["uv", "run", "python", "api/serve.py"],
                    cwd=workspace,
                    env=env,
                    stdout=log_f,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )

            # Save PID
            with open(self.pid_file, "w") as pid_f:
                pid_f.write(str(process.pid))

            # Wait a moment to check if it started successfully
            time.sleep(3)

            if self._is_agent_running():
                pid = self._get_agent_pid()
                print(f"✅ Agent server started successfully (PID: {pid}, Port: {self.agent_port})")

                # Show startup logs
                try:
                    result = subprocess.run(
                        ["head", "-20", str(self.log_file)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        print(f"\n📝 Startup Logs:")
                        print("-" * 40)
                        print(result.stdout.strip())
                    else:
                        print(f"📝 No startup logs available yet")
                except (OSError, subprocess.SubprocessError):
                    print(f"📝 Could not read startup logs")

                return True
            return False

        except OSError:
            return False

    def _stop_agent_background(self) -> bool:
        """Stop agent server running in background."""
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file) as f:
                pid = int(f.read().strip())

            # Check if process is running
            try:
                os.kill(pid, 0)  # Signal 0 just checks if process exists
            except ProcessLookupError:
                self.pid_file.unlink(missing_ok=True)
                return False

            # Try graceful shutdown first
            os.kill(pid, signal.SIGTERM)

            # Wait up to 5 seconds for graceful shutdown
            for _ in range(50):
                try:
                    os.kill(pid, 0)
                    time.sleep(0.1)
                except ProcessLookupError:
                    break
            else:
                # Force kill if still running
                with contextlib.suppress(ProcessLookupError):
                    os.kill(pid, signal.SIGKILL)

            self.pid_file.unlink(missing_ok=True)
            return True

        except OSError:
            return False

    def _is_agent_running(self) -> bool:
        """Check if agent server is running."""
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # Signal 0 just checks if process exists
            return True
        except (ProcessLookupError, ValueError, OSError):
            self.pid_file.unlink(missing_ok=True)
            return False

    def _get_agent_pid(self) -> int | None:
        """Get agent server PID if running."""
        if not self.pid_file.exists():
            return None

        try:
            with open(self.pid_file) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # Check if process exists
            return pid
        except (ProcessLookupError, ValueError, OSError):
            self.pid_file.unlink(missing_ok=True)
            return None

    def _cleanup_agent_environment(self, workspace_path: str) -> bool:
        """Clean up existing agent environment."""
        workspace = Path(workspace_path)

        # Stop agent server
        try:
            self._stop_agent_background()
        except Exception:
            pass  # Continue cleanup even if stop fails

        # Stop agent containers
        with contextlib.suppress(builtins.BaseException):
            subprocess.run(
                ["docker", "compose", "-f", self.agent_compose_file, "down"],
                cwd=workspace,
                capture_output=True,
                check=False,
            )

        # Remove containers
        with contextlib.suppress(builtins.BaseException):
            subprocess.run(
                [
                    "docker",
                    "container",
                    "rm",
                    "hive-agents-agent",
                    "hive-postgres-agent",
                ],
                capture_output=True,
                check=False,
            )

        # Clean up files
        try:
            (workspace / ".env.agent").unlink(missing_ok=True)
            (workspace / "data" / "postgres-agent").rmdir() if (
                workspace / "data" / "postgres-agent"
            ).exists() else None
        except (OSError, FileNotFoundError):
            pass

        return True
