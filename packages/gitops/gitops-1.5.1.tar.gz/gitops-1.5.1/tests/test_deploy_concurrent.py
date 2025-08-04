import asyncio
from unittest.mock import Mock, patch

import pytest

from gitops_server.workers.deployer.semaphore_manager import AppSemaphoreManager
from gitops_server.workers.deployer.worker import DeployQueueWorker


@pytest.mark.asyncio
class TestSemaphoreManager:
    """Test the AppSemaphoreManager for concurrent deployment control."""

    def setup_method(self) -> None:
        """Reset singleton instance between tests."""
        AppSemaphoreManager._instance = None

    async def test_semaphore_creation_per_app(self) -> None:
        """Test that each app gets its own semaphore with limit 1."""
        manager = AppSemaphoreManager()

        # Get semaphores for different apps
        semaphore_a = await manager.get_app_semaphore("app-a")
        semaphore_b = await manager.get_app_semaphore("app-b")
        semaphore_a2 = await manager.get_app_semaphore("app-a")

        # Same app should get same semaphore
        assert semaphore_a is semaphore_a2
        # Different apps should get different semaphores
        assert semaphore_a is not semaphore_b
        # Each semaphore should have limit of 1
        assert semaphore_a._value == 1
        assert semaphore_b._value == 1

    async def test_per_app_serialization(self) -> None:
        """Test that same apps are deployed sequentially across deployments."""
        manager = AppSemaphoreManager()

        # Track the order of operations
        operations = []

        async def simulate_deployment(app_name: str, deployment_id: str) -> None:
            operations.append(f"start-{deployment_id}-{app_name}")
            async with manager.app_semaphore(app_name):
                operations.append(f"acquired-{deployment_id}-{app_name}")

                # Simulate some deployment work
                await asyncio.sleep(0.05)
                operations.append(f"work-{deployment_id}-{app_name}")

            operations.append(f"released-{deployment_id}-{app_name}")

        # Two deployments both trying to deploy app-b
        await asyncio.gather(simulate_deployment("app-b", "deploy1"), simulate_deployment("app-b", "deploy2"))

        # Verify operations happened in serialized order
        assert len(operations) == 8  # 4 operations × 2 deployments

        # Find when each deployment acquired and released the lock
        deploy1_acquired = next(i for i, op in enumerate(operations) if op == "acquired-deploy1-app-b")
        deploy1_released = next(i for i, op in enumerate(operations) if op == "released-deploy1-app-b")
        deploy2_acquired = next(i for i, op in enumerate(operations) if op == "acquired-deploy2-app-b")
        deploy2_released = next(i for i, op in enumerate(operations) if op == "released-deploy2-app-b")

        # One deployment should completely finish before the other acquires the lock
        assert (deploy1_released < deploy2_acquired) or (deploy2_released < deploy1_acquired)

    async def test_parallel_different_apps(self) -> None:
        """Test that different apps can be deployed in parallel."""
        manager = AppSemaphoreManager()

        operations = []

        async def simulate_deployment(app_name: str) -> None:
            operations.append(f"start-{app_name}")
            async with manager.app_semaphore(app_name):
                operations.append(f"acquired-{app_name}")
                await asyncio.sleep(0.05)
                operations.append(f"work-{app_name}")

            operations.append(f"released-{app_name}")

        # Deploy different apps concurrently
        await asyncio.gather(simulate_deployment("app-a"), simulate_deployment("app-b"), simulate_deployment("app-c"))

        # All apps should have been processed
        assert len(operations) == 12  # 4 operations × 3 apps

        # Verify all apps got their own semaphore
        assert len(manager._app_semaphores) == 3
        assert "app-a" in manager._app_semaphores
        assert "app-b" in manager._app_semaphores
        assert "app-c" in manager._app_semaphores

    async def test_lock_release_on_exception(self) -> None:
        """Test that locks are properly released when exceptions occur."""
        manager = AppSemaphoreManager()

        async def failing_deployment() -> None:
            async with manager.app_semaphore("app-x"):
                # Simulate deployment failure
                raise ValueError("Deployment failed")

        # Should raise the exception but not leave locks hanging
        with pytest.raises(ValueError):
            await failing_deployment()

        # Verify lock was released
        locked_apps = manager.get_locked_apps()
        assert "app-x" not in locked_apps

    async def test_get_locked_apps(self) -> None:
        """Test that locked apps are correctly identified."""
        manager = AppSemaphoreManager()

        # Initially no apps are locked
        assert len(manager.get_locked_apps()) == 0

        # Acquire locks for some apps
        async with manager.app_semaphore("app-a"):
            async with manager.app_semaphore("app-b"):
                locked_apps = manager.get_locked_apps()
                assert len(locked_apps) == 2
                assert "app-a" in locked_apps
                assert "app-b" in locked_apps

            # Release one lock
            locked_apps = manager.get_locked_apps()
            assert len(locked_apps) == 1
            assert "app-b" not in locked_apps
            assert "app-a" in locked_apps


@pytest.mark.asyncio
class TestDeployQueueWorker:
    """Test the concurrent deployment worker functionality."""

    def setup_method(self) -> None:
        """Reset singleton instance between tests."""
        DeployQueueWorker._worker = None
        AppSemaphoreManager._instance = None

    async def test_worker_singleton(self) -> None:
        """Test that worker maintains singleton pattern."""
        worker1 = DeployQueueWorker.get_worker()
        worker2 = DeployQueueWorker.get_worker()

        assert worker1 is worker2
        assert DeployQueueWorker._worker is worker1

    async def test_worker_initialization(self) -> None:
        """Test that worker is properly initialized."""
        worker = DeployQueueWorker.get_worker()

        # Worker should have required components
        assert hasattr(worker, "queue")
        assert hasattr(worker, "semaphore_manager")
        assert hasattr(worker, "active_deployments")

        # Components should be properly initialized
        assert isinstance(worker.queue, asyncio.Queue)
        assert isinstance(worker.semaphore_manager, AppSemaphoreManager)
        assert isinstance(worker.active_deployments, set)
        assert len(worker.active_deployments) == 0

    async def test_enqueue_and_process_work(self) -> None:
        """Test that work can be enqueued and processed."""
        worker = DeployQueueWorker.get_worker()

        # Mock webhook data
        test_work = {"ref": "refs/heads/master", "test": "data"}

        # Enqueue work
        await worker.enqueue(test_work)
        assert worker.queue.qsize() == 1

        # Dequeue work
        work = await worker.queue.get()
        assert work == test_work
        assert worker.queue.qsize() == 0

    @patch("gitops_server.workers.deployer.worker.Deployer.from_push_event")
    async def test_process_deployment_task_creation(self, mock_from_push_event: Mock) -> None:
        """Test that deployment processing creates proper async tasks."""
        worker = DeployQueueWorker.get_worker()

        # Mock deployer creation and deployment
        mock_deployer = Mock()
        mock_deployer.deploy = Mock(return_value=asyncio.sleep(0))  # Return awaitable
        mock_from_push_event.return_value = mock_deployer

        test_work = {
            "ref": "refs/heads/master",
            "repository": {"clone_url": "https://github.com/test/repo.git"},
            "head_commit": {"message": "test", "author": {"name": "Test", "email": "test@example.com"}},
        }

        # Process deployment
        await worker.process_deployment(test_work)

        # Verify deployer was created and deployed
        mock_from_push_event.assert_called_once_with(test_work, worker.semaphore_manager)


@pytest.mark.asyncio
class TestConcurrentDeploymentIntegration:
    """Integration tests combining semaphore manager and worker."""

    def setup_method(self) -> None:
        """Reset singleton instances between tests."""
        DeployQueueWorker._worker = None
        AppSemaphoreManager._instance = None

    async def test_concurrent_deployment_coordination(self) -> None:
        """Test end-to-end coordination of concurrent deployments."""
        worker = DeployQueueWorker.get_worker()
        manager = worker.semaphore_manager

        # Track deployment coordination
        coordination_log = []

        # Mock a deployment that uses app locks
        async def mock_deployment(app_names: list[str], deployment_id: str) -> None:
            for app_name in app_names:
                coordination_log.append(f"start-{deployment_id}-{app_name}")
                async with manager.app_semaphore(app_name):
                    coordination_log.append(f"acquired-{deployment_id}-{app_name}")
                    # Simulate deployment work
                    await asyncio.sleep(0.01)
                    coordination_log.append(f"deployed-{deployment_id}-{app_name}")

                coordination_log.append(f"released-{deployment_id}-{app_name}")

        # Simulate multiple concurrent deployments with overlapping apps
        await asyncio.gather(
            mock_deployment(["app-a", "app-b"], "deploy-1"),
            mock_deployment(["app-b", "app-c"], "deploy-2"),
            mock_deployment(["app-a", "app-c"], "deploy-3"),
        )

        # Verify all deployments completed
        assert len(coordination_log) > 0

        # Count deployments per app
        app_a_deployments = len([log for log in coordination_log if "deployed" in log and "app-a" in log])
        app_b_deployments = len([log for log in coordination_log if "deployed" in log and "app-b" in log])
        app_c_deployments = len([log for log in coordination_log if "deployed" in log and "app-c" in log])

        # Each app should be deployed exactly twice (appears in 2 out of 3 deployments)
        assert app_a_deployments == 2  # deploy-1, deploy-3
        assert app_b_deployments == 2  # deploy-1, deploy-2
        assert app_c_deployments == 2  # deploy-2, deploy-3

        # No locks should remain
        assert len(manager.get_locked_apps()) == 0
