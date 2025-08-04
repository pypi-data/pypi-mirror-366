import asyncio
import logging
from typing import Any

from opentelemetry import trace

from .deploy import Deployer
from .semaphore_manager import AppSemaphoreManager

logger = logging.getLogger("gitops_worker")

tracer = trace.get_tracer(__name__)


class DeployQueueWorker:
    """Concurrent deployment worker with per-app serialization.

    Multiple deployments can run simultaneously, but apps are updated
    sequentially using per-app semaphores. This ensures cluster consistency
    while allowing parallel deployments of different apps.
    """

    # Worker singleton
    _worker: "DeployQueueWorker | None" = None

    @classmethod
    def get_worker(cls) -> "DeployQueueWorker":
        if not cls._worker:
            cls._worker = cls()
        return cls._worker

    def __init__(self) -> None:
        self.queue: asyncio.Queue[Any] = asyncio.Queue()
        self.semaphore_manager = AppSemaphoreManager()
        self.active_deployments: set[asyncio.Task[None]] = set()

    async def enqueue(self, work: Any) -> None:
        """Enqueue an item of work for future processing.

        The `work` argument is the body of an incoming GitHub push webhook.
        """
        logger.info(f"Enqueued work, {self.queue.qsize() + 1} items in the queue.")
        await self.queue.put(work)

    async def run(self) -> None:
        """Run the worker.

        Manages concurrent deployments while maintaining per-app serialization.
        Each deployment runs as a separate task, allowing multiple deployments
        to proceed simultaneously.
        # TODO: Need to gracefully handle termination.
        """
        logger.info("Starting up concurrent deployer worker loop")
        while True:
            try:
                # Clean up completed tasks
                self.active_deployments = {task for task in self.active_deployments if not task.done()}

                # Process new work
                work = await self.queue.get()
                deployment_task = asyncio.create_task(self.process_deployment(work))
                self.active_deployments.add(deployment_task)

                # Log current status
                locked_apps = self.semaphore_manager.get_locked_apps()
                logger.info(
                    f"Active deployments: {len(self.active_deployments)}, " + f"Locked apps: {sorted(locked_apps)}"
                )

            except Exception as e:
                logger.error(str(e), exc_info=True)

    async def process_deployment(self, work: Any) -> None:
        """Process a single deployment in a separate task.

        This allows multiple deployments to run concurrently while
        maintaining per-app serialization through semaphores.
        """
        ref = work.get("ref")
        logger.info(f'Processing deployment for push to "{ref}".')

        if ref == "refs/heads/master":
            with tracer.start_as_current_span("gitops_process_webhook") as current_span:
                try:
                    deployer = await Deployer.from_push_event(work, self.semaphore_manager)
                    current_span.set_attribute("gitops.ref", ref)
                    current_span.set_attribute("gitops.after", work.get("after"))
                    current_span.set_attribute("gitops.before", work.get("before"))
                    current_span.set_attribute("gitops.author_email", deployer.author_email)
                    current_span.set_attribute("gitops.author_name", deployer.author_name)
                    current_span.set_attribute("gitops.commit_message", deployer.commit_message)
                    await deployer.deploy()

                except Exception as e:
                    logger.error(f"Deployment failed: {e}", exc_info=True)
                    raise
        else:
            logger.info(f'Ignoring push to "{ref}" (not master branch).')
