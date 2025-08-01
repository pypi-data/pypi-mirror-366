"""
Main CLI Entry Point for Automagik Hive.

This module provides the primary CLI interface for the UVX transformation,
with PostgreSQL container management integration as the foundation.
"""

import sys
import argparse
from typing import Optional
from pathlib import Path

from cli.commands.postgres import PostgreSQLCommands
from cli.commands.init import InitCommands
from cli.commands.workspace import WorkspaceCommands
from lib.utils.version_reader import get_cli_version_string


def create_parser() -> argparse.ArgumentParser:
    """
    Create the main CLI argument parser.
    
    Returns:
        ArgumentParser configured with core commands
    """
    parser = argparse.ArgumentParser(
        prog="automagik-hive",
        description="Automagik Hive CLI - UVX Development Environment (T1.5 Implementation)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Core Commands:
  # Workspace initialization and startup
  uvx automagik-hive --init                    # Interactive workspace initialization
  uvx automagik-hive ./my-workspace             # Start existing workspace server
  uvx automagik-hive --help                    # Show this help message
  uvx automagik-hive --version                 # Show version information

  # PostgreSQL container management
  uvx automagik-hive --postgres-status         # Check PostgreSQL container status
  uvx automagik-hive --postgres-start          # Start PostgreSQL container
  uvx automagik-hive --postgres-stop           # Stop PostgreSQL container
  uvx automagik-hive --postgres-restart        # Restart PostgreSQL container
  uvx automagik-hive --postgres-logs           # Show PostgreSQL container logs
  uvx automagik-hive --postgres-health         # Check PostgreSQL health

  # With specific workspace
  uvx automagik-hive --postgres-status ./my-workspace
  uvx automagik-hive --postgres-logs ./my-workspace --tail 100

Note: T1.5 Core Command Implementation - Essential UVX functionality ready.
        """
    )
    
    # Core workspace commands (T1.5)
    core_group = parser.add_argument_group("Core Workspace Commands")
    core_group.add_argument(
        "--init",
        action="store_true",
        help="Interactive workspace initialization with API key collection"
    )
    core_group.add_argument(
        "--serve",
        action="store_true",
        help="Start FastAPI server directly (used internally)"
    )
    
    # PostgreSQL container management commands
    postgres_group = parser.add_argument_group("PostgreSQL Container Management")
    postgres_group.add_argument(
        "--postgres-status",
        action="store_true",
        help="Check PostgreSQL container status and connection info"
    )
    postgres_group.add_argument(
        "--postgres-start", 
        action="store_true",
        help="Start PostgreSQL container"
    )
    postgres_group.add_argument(
        "--postgres-stop",
        action="store_true", 
        help="Stop PostgreSQL container"
    )
    postgres_group.add_argument(
        "--postgres-restart",
        action="store_true",
        help="Restart PostgreSQL container"
    )
    postgres_group.add_argument(
        "--postgres-logs",
        action="store_true",
        help="Show PostgreSQL container logs"
    )
    postgres_group.add_argument(
        "--postgres-health",
        action="store_true",
        help="Check PostgreSQL health and connectivity"
    )
    
    # Common options
    parser.add_argument(
        "workspace",
        nargs="?",
        default=None,
        help="Path to workspace directory (for startup) or workspace name (for init)"
    )
    parser.add_argument(
        "--tail",
        type=int,
        default=50,
        help="Number of log lines to show (default: 50)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8886,
        help="Port to bind server to (default: 8886)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=get_cli_version_string()
    )
    
    return parser


def main() -> int:
    """
    Main CLI entry point.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Initialize command handlers
    init_commands = InitCommands()
    workspace_commands = WorkspaceCommands()
    postgres_commands = PostgreSQLCommands()
    
    # Handle core workspace commands (T1.5)
    if args.init:
        success = init_commands.init_workspace(args.workspace)
        return 0 if success else 1
        
    # Handle direct server startup
    elif args.serve:
        try:
            import subprocess
            print(f"🚀 Starting Automagik Hive server on {args.host}:{args.port}")
            print("📋 Server logs will appear below...")
            print("⏹️ Press Ctrl+C to stop the server\n")
            
            result = subprocess.run([
                "uv", "run", "uvicorn", "api.serve:app",
                "--host", args.host,
                "--port", str(args.port),
                "--reload"
            ])
            return 0
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            return 0
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return 1
        
    # Handle workspace startup command (T1.5)
    elif args.workspace and not any([
        args.postgres_status, args.postgres_start, args.postgres_stop,
        args.postgres_restart, args.postgres_logs, args.postgres_health
    ]):
        # This is a workspace startup command
        workspace_path = args.workspace
        if Path(workspace_path).is_dir() or workspace_path.startswith("./") or workspace_path.startswith("/"):
            success = workspace_commands.start_workspace(workspace_path)
            return 0 if success else 1
        else:
            print(f"❌ Workspace path '{workspace_path}' not found or invalid")
            print("💡 Use 'uvx automagik-hive --init' to create a new workspace")
            return 1
            
    # Handle PostgreSQL commands
    elif args.postgres_status:
        success = postgres_commands.postgres_status(args.workspace or ".")
        return 0 if success else 1
        
    elif args.postgres_start:
        success = postgres_commands.postgres_start(args.workspace or ".")
        return 0 if success else 1
        
    elif args.postgres_stop:
        success = postgres_commands.postgres_stop(args.workspace or ".")
        return 0 if success else 1
        
    elif args.postgres_restart:
        success = postgres_commands.postgres_restart(args.workspace or ".")
        return 0 if success else 1
        
    elif args.postgres_logs:
        success = postgres_commands.postgres_logs(args.workspace or ".", args.tail)
        return 0 if success else 1
        
    elif args.postgres_health:
        success = postgres_commands.postgres_health(args.workspace or ".")
        return 0 if success else 1
        
    else:
        # No command specified, show help
        parser.print_help()
        print("\n🧞 Welcome to Automagik Hive CLI!")
        print("✅ T1.5 Core Command Implementation - UVX Ready!")
        print("🚀 Try: uvx automagik-hive --init")
        print("🏁 Or: uvx automagik-hive ./my-workspace")
        return 0


def app() -> int:
    """
    Main application entry point for typer integration.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    return main()


if __name__ == "__main__":
    sys.exit(main())