"""
Docker Sandbox Executor for Python Analysis Scripts
Provides secure, isolated execution environment with resource limits
"""
import asyncio
import json
import logging
import os
import shutil
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import docker
from docker.errors import ContainerError, ImageNotFound, APIError

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of sandbox execution"""
    success: bool
    stdout: str
    stderr: str
    outputs: Dict[str, Any]  # Generated files (plots, data, etc.)
    execution_time: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


class SandboxExecutor:
    """Manages Docker sandbox for Python script execution"""

    IMAGE_NAME = "python-analysis-sandbox:latest"
    TIMEOUT_SECONDS = 300  # 5 minutes max execution

    def __init__(self,
                 sandbox_dir: Optional[Path] = None,
                 build_image: bool = False):
        """
        Initialize sandbox executor

        Args:
            sandbox_dir: Directory containing Dockerfile (default: current dir)
            build_image: Whether to build Docker image on initialization
        """
        self.docker_client = docker.from_env()
        self.sandbox_dir = sandbox_dir or Path(__file__).parent

        if build_image:
            self._build_image()
        else:
            self._ensure_image_exists()

    def _build_image(self):
        """Build Docker image from Dockerfile"""
        logger.info(f"Building Docker image: {self.IMAGE_NAME}")
        try:
            image, build_logs = self.docker_client.images.build(
                path=str(self.sandbox_dir),
                tag=self.IMAGE_NAME,
                rm=True,
                forcerm=True
            )
            logger.info(f"Successfully built image: {self.IMAGE_NAME}")
            for log in build_logs:
                if 'stream' in log:
                    logger.debug(log['stream'].strip())
        except Exception as e:
            logger.error(f"Failed to build Docker image: {e}")
            raise

    def _ensure_image_exists(self):
        """Check if Docker image exists, build if not"""
        try:
            self.docker_client.images.get(self.IMAGE_NAME)
            logger.debug(f"Docker image {self.IMAGE_NAME} found")
        except ImageNotFound:
            logger.warning(f"Image {self.IMAGE_NAME} not found, building...")
            self._build_image()

    async def execute(self,
                     script: str,
                     data: Optional[Dict[str, Any]] = None,
                     timeout: Optional[int] = None) -> ExecutionResult:
        """
        Execute Python script in sandbox with optional data

        Args:
            script: Python code to execute
            data: Optional data dict to pass to script (as data.pkl)
            timeout: Execution timeout in seconds (default: 300)

        Returns:
            ExecutionResult with outputs and status
        """
        execution_id = str(uuid.uuid4())[:8]
        timeout = timeout or self.TIMEOUT_SECONDS

        # Create temporary workspace
        workspace = tempfile.mkdtemp(prefix=f"sandbox_{execution_id}_")
        workspace_path = Path(workspace)

        try:
            # Prepare execution environment
            data_dir = workspace_path / "data"
            outputs_dir = workspace_path / "outputs"
            data_dir.mkdir(exist_ok=True)
            outputs_dir.mkdir(exist_ok=True)

            # Write script
            script_path = workspace_path / "script.py"
            script_path.write_text(script)

            # Write data if provided
            if data:
                import pickle
                data_file = data_dir / "data.pkl"
                with open(data_file, 'wb') as f:
                    pickle.dump(data, f)

            # Execute in container
            result = await self._run_container(
                workspace_path=workspace_path,
                execution_id=execution_id,
                timeout=timeout
            )

            return result

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                outputs={},
                execution_time=0.0,
                error=str(e)
            )
        finally:
            # Cleanup workspace
            try:
                shutil.rmtree(workspace)
            except Exception as e:
                logger.warning(f"Failed to cleanup workspace {workspace}: {e}")

    async def _run_container(self,
                            workspace_path: Path,
                            execution_id: str,
                            timeout: int) -> ExecutionResult:
        """Run Docker container with script"""
        import time
        start_time = time.time()

        container = None
        try:
            # Container configuration
            volumes = {
                str(workspace_path / "script.py"): {
                    'bind': '/sandbox/script.py',
                    'mode': 'ro'
                },
                str(workspace_path / "data"): {
                    'bind': '/sandbox/data',
                    'mode': 'ro'
                },
                str(workspace_path / "outputs"): {
                    'bind': '/sandbox/outputs',
                    'mode': 'rw'
                }
            }

            # Security and resource limits
            container = self.docker_client.containers.run(
                image=self.IMAGE_NAME,
                command=["python", "-u", "/sandbox/script.py"],
                volumes=volumes,
                network_mode='none',
                mem_limit='2g',
                memswap_limit='2g',
                cpu_period=100000,
                cpu_quota=200000,  # 2 CPU cores max
                security_opt=['no-new-privileges'],
                read_only=True,
                tmpfs={'/tmp': 'size=512M'},
                detach=True,
                remove=False,
                name=f"sandbox_{execution_id}"
            )

            # Wait for completion with timeout
            try:
                exit_code = container.wait(timeout=timeout)
                logs = container.logs(stdout=True, stderr=True).decode('utf-8', errors='replace')

                # Split stdout/stderr (simplified)
                stdout = logs
                stderr = ""

            except Exception as e:
                logger.error(f"Container execution error: {e}")
                container.stop(timeout=5)
                raise

            execution_time = time.time() - start_time

            # Collect outputs
            outputs = self._collect_outputs(workspace_path / "outputs")

            # Determine success
            success = exit_code.get('StatusCode', 1) == 0 if isinstance(exit_code, dict) else exit_code == 0

            return ExecutionResult(
                success=success,
                stdout=stdout,
                stderr=stderr,
                outputs=outputs,
                execution_time=execution_time,
                metadata={
                    'execution_id': execution_id,
                    'exit_code': exit_code
                }
            )

        except ContainerError as e:
            logger.error(f"Container error: {e}")
            return ExecutionResult(
                success=False,
                stdout=e.stdout.decode('utf-8', errors='replace') if e.stdout else "",
                stderr=e.stderr.decode('utf-8', errors='replace') if e.stderr else str(e),
                outputs={},
                execution_time=time.time() - start_time,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                outputs={},
                execution_time=time.time() - start_time,
                error=str(e)
            )
        finally:
            # Cleanup container
            if container:
                try:
                    container.remove(force=True)
                except Exception as e:
                    logger.warning(f"Failed to remove container: {e}")

    def _collect_outputs(self, outputs_dir: Path) -> Dict[str, Any]:
        """Collect generated outputs from sandbox"""
        outputs = {}

        if not outputs_dir.exists():
            return outputs

        for file_path in outputs_dir.iterdir():
            if file_path.is_file():
                filename = file_path.name

                # Read based on file type
                if filename.endswith('.json'):
                    with open(file_path, 'r') as f:
                        outputs[filename] = json.load(f)

                elif filename.endswith(('.png', '.jpg', '.jpeg')):
                    with open(file_path, 'rb') as f:
                        outputs[filename] = f.read()

                elif filename.endswith('.html'):
                    with open(file_path, 'r') as f:
                        outputs[filename] = f.read()

                elif filename.endswith('.csv'):
                    with open(file_path, 'r') as f:
                        outputs[filename] = f.read()

                else:
                    # Generic text file
                    try:
                        with open(file_path, 'r') as f:
                            outputs[filename] = f.read()
                    except UnicodeDecodeError:
                        with open(file_path, 'rb') as f:
                            outputs[filename] = f.read()

        return outputs

    def cleanup_all(self):
        """Clean up all sandbox containers"""
        try:
            containers = self.docker_client.containers.list(
                filters={'name': 'sandbox_'},
                all=True
            )
            for container in containers:
                logger.info(f"Removing container: {container.name}")
                container.remove(force=True)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Convenience async function
async def execute_in_sandbox(script: str,
                            data: Optional[Dict[str, Any]] = None,
                            timeout: int = 300) -> ExecutionResult:
    """
    Execute Python script in sandbox (convenience function)

    Args:
        script: Python code to execute
        data: Optional data to pass to script
        timeout: Max execution time in seconds

    Returns:
        ExecutionResult
    """
    executor = SandboxExecutor()
    return await executor.execute(script, data, timeout)
