from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SchedulerManager:
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None

    def init_scheduler(self) -> None:
        """Initialize the AsyncIOScheduler instance."""
        if self.scheduler is None:
            self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        """Start the scheduler."""
        if self.scheduler is None:
            self.init_scheduler()
        
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self) -> None:
        """Shutdown the scheduler gracefully."""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()

    def add_job(self, func, trigger: str, **trigger_args) -> None:
        """Add a job to the scheduler.
        
        Args:
            func: The function to execute
            trigger: The trigger type (e.g., 'cron', 'interval')
            **trigger_args: Arguments for the trigger
        """
        if self.scheduler is None:
            self.init_scheduler()
        
        self.scheduler.add_job(func, trigger, **trigger_args)
        logger.info(f"Added job {func.__name__} with trigger {trigger}")

    def add_daily_job(self, func, hour: int = 9, minute: int = 0) -> None:
        """Add a job that runs daily at the specified time.
        
        Args:
            func: The function to execute
            hour: The hour to run (24-hour format)
            minute: The minute to run
        """
        self.add_job(
            func,
            CronTrigger(hour=hour, minute=minute),
            id=f"{func.__name__}_daily",
            replace_existing=True
        )

# Global scheduler instance
scheduler_manager = SchedulerManager() 