"""
Data Collection Orchestrator - investByYourself
Tech-009: ETL Pipeline Implementation - Phase 1

This module provides a unified interface for orchestrating multiple data collectors,
managing their execution, and coordinating data collection across different sources.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import structlog

from .alpha_vantage_collector import AlphaVantageCollector
from .base_collector import BaseDataCollector, DataCollectionError
from .fred_collector import FREDCollector
from .yahoo_finance_collector import YahooFinanceCollector

logger = structlog.get_logger(__name__)


@dataclass
class CollectionTask:
    """Represents a data collection task."""

    task_id: str
    source: str  # 'yahoo', 'alpha_vantage', 'fred'
    task_type: str  # 'profile', 'financials', 'market_data', etc.
    parameters: Dict[str, Any]
    priority: int = 1  # Higher number = higher priority
    scheduled_time: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"  # pending, running, completed, failed, cancelled


@dataclass
class CollectionResult:
    """Represents the result of a collection task."""

    task_id: str
    source: str
    task_type: str
    status: str  # success, failed, cancelled
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    retry_count: int = 0


class DataCollectionOrchestrator:
    """
    Orchestrates data collection across multiple sources.

    Features:
    - Unified interface for multiple data collectors
    - Task scheduling and prioritization
    - Concurrent execution with rate limiting
    - Error handling and retry mechanisms
    - Performance monitoring and metrics
    """

    def __init__(
        self,
        yahoo_api_key: Optional[str] = None,
        alpha_vantage_api_key: Optional[str] = None,
        fred_api_key: Optional[str] = None,
        max_concurrent_tasks: int = 10,
        enable_monitoring: bool = True,
    ):
        """Initialize the collection orchestrator."""
        self.max_concurrent_tasks = max_concurrent_tasks
        self.enable_monitoring = enable_monitoring

        # Initialize collectors
        self.collectors: Dict[str, BaseDataCollector] = {}
        self._initialize_collectors(yahoo_api_key, alpha_vantage_api_key, fred_api_key)

        # Task management
        self.pending_tasks: List[CollectionTask] = []
        self.running_tasks: Dict[str, CollectionTask] = {}
        self.completed_tasks: Dict[str, CollectionResult] = {}
        self.failed_tasks: Dict[str, CollectionResult] = {}

        # Execution control
        self.running = False
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

        # Performance metrics
        self.total_tasks_executed = 0
        self.successful_tasks = 0
        self.failed_tasks = 0
        self.total_execution_time = 0.0

        logger.info(
            "Data Collection Orchestrator initialized",
            max_concurrent_tasks=max_concurrent_tasks,
            collectors_available=list(self.collectors.keys()),
            enable_monitoring=enable_monitoring,
        )

    def _initialize_collectors(
        self,
        yahoo_api_key: Optional[str],
        alpha_vantage_api_key: Optional[str],
        fred_api_key: Optional[str],
    ):
        """Initialize available data collectors."""
        try:
            if yahoo_api_key:
                self.collectors["yahoo"] = YahooFinanceCollector()
                logger.info("Yahoo Finance collector initialized")

            if alpha_vantage_api_key:
                self.collectors["alpha_vantage"] = AlphaVantageCollector(
                    api_key=alpha_vantage_api_key
                )
                logger.info("Alpha Vantage collector initialized")

            if fred_api_key:
                self.collectors["fred"] = FREDCollector(api_key=fred_api_key)
                logger.info("FRED collector initialized")

            if not self.collectors:
                logger.warning("No data collectors were initialized")

        except Exception as e:
            logger.error(f"Error initializing collectors: {str(e)}")
            raise

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()

    async def start(self):
        """Start the orchestrator."""
        if self.running:
            logger.warning("Orchestrator is already running")
            return

        self.running = True
        logger.info("Data Collection Orchestrator started")

    async def stop(self):
        """Stop the orchestrator."""
        if not self.running:
            return

        # Cancel all running tasks
        for task_id in list(self.running_tasks.keys()):
            await self.cancel_task(task_id)

        # Wait for tasks to complete
        while self.running_tasks:
            await asyncio.sleep(0.1)

        self.running = False
        logger.info("Data Collection Orchestrator stopped")

    def add_task(
        self,
        source: str,
        task_type: str,
        parameters: Dict[str, Any],
        priority: int = 1,
        scheduled_time: Optional[datetime] = None,
    ) -> str:
        """
        Add a new collection task to the queue.

        Args:
            source: Data source ('yahoo', 'alpha_vantage', 'fred')
            task_type: Type of collection task
            parameters: Task-specific parameters
            priority: Task priority (higher = more important)
            scheduled_time: When to execute the task (None = immediate)

        Returns:
            Task ID for tracking
        """
        if source not in self.collectors:
            raise ValueError(f"Unknown data source: {source}")

        task_id = f"{source}_{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        task = CollectionTask(
            task_id=task_id,
            source=source,
            task_type=task_type,
            parameters=parameters,
            priority=priority,
            scheduled_time=scheduled_time,
        )

        # Insert based on priority (higher priority first)
        inserted = False
        for i, existing_task in enumerate(self.pending_tasks):
            if existing_task.priority < priority:
                self.pending_tasks.insert(i, task)
                inserted = True
                break

        if not inserted:
            self.pending_tasks.append(task)

        logger.info(
            f"Added collection task: {task_id}",
            source=source,
            task_type=task_type,
            priority=priority,
            scheduled_time=scheduled_time,
        )

        return task_id

    async def execute_task(self, task: CollectionTask) -> CollectionResult:
        """
        Execute a single collection task.

        Args:
            task: Collection task to execute

        Returns:
            Collection result
        """
        result = CollectionResult(
            task_id=task.task_id,
            source=task.source,
            task_type=task.task_type,
            status="running",
            start_time=datetime.now(),
        )

        try:
            logger.info(f"Executing task: {task.task_id}")

            # Get the appropriate collector
            collector = self.collectors[task.source]

            # Execute the collection
            data = await collector.execute_collection(**task.parameters)

            # Update result
            result.status = "success"
            result.data = data
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()

            logger.info(
                f"Task completed successfully: {task.task_id}",
                duration=result.duration,
                data_points=len(data.get("data", {})),
            )

        except Exception as e:
            result.status = "failed"
            result.error = str(e)
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()
            result.retry_count = task.retry_count

            logger.error(
                f"Task failed: {task.task_id}",
                error=str(e),
                retry_count=task.retry_count,
            )

            # Handle retries
            if task.retry_count < task.max_retries:
                await self._schedule_retry(task)

        return result

    async def _schedule_retry(self, task: CollectionTask):
        """Schedule a task for retry."""
        task.retry_count += 1
        task.status = "pending"

        # Add delay before retry (exponential backoff)
        delay = min(60 * (2**task.retry_count), 300)  # Max 5 minutes
        retry_time = datetime.now() + timedelta(seconds=delay)
        task.scheduled_time = retry_time

        # Add to pending tasks
        self.pending_tasks.append(task)

        logger.info(
            f"Scheduled retry for task: {task.task_id}",
            retry_count=task.retry_count,
            retry_time=retry_time,
        )

    async def execute_tasks(
        self, max_tasks: Optional[int] = None
    ) -> List[CollectionResult]:
        """
        Execute pending tasks up to the specified limit.

        Args:
            max_tasks: Maximum number of tasks to execute (None = all pending)

        Returns:
            List of collection results
        """
        if not self.running:
            raise RuntimeError("Orchestrator is not running")

        if max_tasks is None:
            max_tasks = len(self.pending_tasks)

        # Filter tasks that are ready to execute
        ready_tasks = []
        remaining_tasks = []

        for task in self.pending_tasks:
            if task.scheduled_time is None or task.scheduled_time <= datetime.now():
                ready_tasks.append(task)
            else:
                remaining_tasks.append(task)

        # Update pending tasks
        self.pending_tasks = remaining_tasks

        # Limit the number of tasks to execute
        ready_tasks = ready_tasks[:max_tasks]

        if not ready_tasks:
            logger.info("No tasks ready for execution")
            return []

        logger.info(f"Executing {len(ready_tasks)} tasks")

        # Execute tasks concurrently
        results = []
        async with asyncio.TaskGroup() as tg:
            for task in ready_tasks:
                tg.create_task(self._execute_task_with_semaphore(task))

        # Collect results
        for task in ready_tasks:
            if task.task_id in self.completed_tasks:
                results.append(self.completed_tasks[task.task_id])
            elif task.task_id in self.failed_tasks:
                results.append(self.failed_tasks[task.task_id])

        return results

    async def _execute_task_with_semaphore(self, task: CollectionTask):
        """Execute a task with concurrency control."""
        async with self.semaphore:
            # Mark task as running
            task.status = "running"
            self.running_tasks[task.task_id] = task

            try:
                # Execute the task
                result = await self.execute_task(task)

                # Update task tracking
                if result.status == "success":
                    self.completed_tasks[task.task_id] = result
                    self.successful_tasks += 1
                else:
                    self.failed_tasks[task.task_id] = result
                    self.failed_tasks += 1

                # Update metrics
                self.total_tasks_executed += 1
                if result.duration:
                    self.total_execution_time += result.duration

            finally:
                # Remove from running tasks
                if task.task_id in self.running_tasks:
                    del self.running_tasks[task.task_id]

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running or pending task.

        Args:
            task_id: ID of the task to cancel

        Returns:
            True if task was cancelled, False otherwise
        """
        # Check running tasks
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.status = "cancelled"

            # Create cancelled result
            result = CollectionResult(
                task_id=task_id,
                source=task.source,
                task_type=task.task_type,
                status="cancelled",
                start_time=datetime.now(),
                end_time=datetime.now(),
            )

            self.completed_tasks[task_id] = result
            del self.running_tasks[task_id]

            logger.info(f"Task cancelled: {task_id}")
            return True

        # Check pending tasks
        for i, task in enumerate(self.pending_tasks):
            if task.task_id == task_id:
                cancelled_task = self.pending_tasks.pop(i)
                cancelled_task.status = "cancelled"

                logger.info(f"Pending task cancelled: {task_id}")
                return True

        return False

    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get the status of a task."""
        if task_id in self.running_tasks:
            return self.running_tasks[task_id].status
        elif task_id in self.completed_tasks:
            return self.completed_tasks[task_id].status
        elif task_id in self.failed_tasks:
            return self.failed_tasks[task_id].status

        # Check pending tasks
        for task in self.pending_tasks:
            if task.task_id == task_id:
                return task.status

        return None

    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator performance metrics."""
        return {
            "orchestrator_status": "running" if self.running else "stopped",
            "total_tasks_executed": self.total_tasks_executed,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": (self.successful_tasks / self.total_tasks_executed * 100)
            if self.total_tasks_executed > 0
            else 0.0,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": (
                self.total_execution_time / self.total_tasks_executed
            )
            if self.total_tasks_executed > 0
            else 0.0,
            "pending_tasks": len(self.pending_tasks),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "collectors_available": list(self.collectors.keys()),
        }

    async def collect_company_data(
        self,
        symbols: List[str],
        data_types: List[str] = None,
        sources: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Collect company data for multiple symbols from multiple sources.

        Args:
            symbols: List of company symbols
            data_types: Types of data to collect (default: ['profile', 'financials'])
            sources: Data sources to use (default: all available)

        Returns:
            Collection results organized by symbol and data type
        """
        if data_types is None:
            data_types = ["profile", "financials"]

        if sources is None:
            sources = list(self.collectors.keys())

        results = {
            "metadata": {
                "collection_time": datetime.now().isoformat(),
                "symbols": symbols,
                "data_types": data_types,
                "sources": sources,
                "total_tasks": len(symbols) * len(data_types) * len(sources),
            },
            "results": {},
            "summary": {"successful": 0, "failed": 0, "total_duration": 0.0},
        }

        start_time = datetime.now()

        # Create collection tasks
        for symbol in symbols:
            results["results"][symbol] = {}

            for data_type in data_types:
                results["results"][symbol][data_type] = {}

                for source in sources:
                    if source in ["yahoo", "yahoo_finance"]:
                        parameters = {"symbol": symbol, "data_type": data_type}
                    elif source == "alpha_vantage":
                        if data_type == "profile":
                            function = "OVERVIEW"
                        elif data_type == "financials":
                            function = "INCOME_STATEMENT"
                        else:
                            function = "TIME_SERIES_DAILY"
                        parameters = {"symbol": symbol, "function": function}
                    elif source == "fred":
                        # FRED doesn't have company-specific data, skip
                        continue

                    # Add task
                    task_id = self.add_task(
                        source=source,
                        task_type=data_type,
                        parameters=parameters,
                        priority=1,
                    )

        # Execute all tasks
        await self.execute_tasks()

        # Collect results
        for symbol in symbols:
            for data_type in data_types:
                for source in sources:
                    if source == "fred":
                        continue

                    # Find completed task
                    for task_id, result in self.completed_tasks.items():
                        if (
                            result.source
                            in [
                                source,
                                "yahoo_finance" if source == "yahoo" else source,
                            ]
                            and result.task_type == data_type
                            and result.data
                            and result.data.get("data", {}).get("symbol") == symbol
                        ):
                            results["results"][symbol][data_type][source] = result.data
                            if result.status == "success":
                                results["summary"]["successful"] += 1
                            else:
                                results["summary"]["failed"] += 1
                            break

        end_time = datetime.now()
        results["summary"]["total_duration"] = (end_time - start_time).total_seconds()

        return results

    async def collect_economic_data(
        self, indicators: List[str] = None, sources: List[str] = None
    ) -> Dict[str, Any]:
        """
        Collect economic data from available sources.

        Args:
            indicators: Economic indicators to collect
            sources: Data sources to use (default: all available)

        Returns:
            Collection results for economic indicators
        """
        if sources is None:
            sources = list(self.collectors.keys())

        results = {
            "metadata": {
                "collection_time": datetime.now().isoformat(),
                "indicators": indicators,
                "sources": sources,
            },
            "results": {},
            "summary": {"successful": 0, "failed": 0, "total_duration": 0.0},
        }

        start_time = datetime.now()

        # Collect from FRED if available
        if "fred" in sources and indicators:
            try:
                fred_results = await self.collectors["fred"].collect_common_indicators(
                    indicators
                )
                results["results"]["fred"] = fred_results
                results["summary"]["successful"] += fred_results["summary"][
                    "successful"
                ]
                results["summary"]["failed"] += fred_results["summary"]["failed"]
            except Exception as e:
                logger.error(f"Error collecting FRED data: {str(e)}")
                results["summary"]["failed"] += 1

        end_time = datetime.now()
        results["summary"]["total_duration"] = (end_time - start_time).total_seconds()

        return results
