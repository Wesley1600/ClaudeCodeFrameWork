"""
Scheduler for periodic pulse updates.
"""

from datetime import datetime, time, timedelta
from typing import Callable, Optional
import threading
import time as time_module
from pathlib import Path
import json


class PulseScheduler:
    """
    Manages scheduling of pulse updates.
    """

    def __init__(
        self,
        schedule_time: time = time(6, 0),  # 6:00 AM default
        frequency: str = "daily",  # daily, weekly, manual
        enabled: bool = True,
    ):
        self.schedule_time = schedule_time
        self.frequency = frequency
        self.enabled = enabled
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.callback: Optional[Callable] = None
        self.last_run_file = Path.home() / ".agent_pulse" / "last_run.json"
        self.last_run_file.parent.mkdir(parents=True, exist_ok=True)

    def set_callback(self, callback: Callable) -> None:
        """
        Set the callback function to run on schedule.

        Args:
            callback: Function to call when pulse should run
        """
        self.callback = callback

    def start(self) -> None:
        """Start the scheduler."""
        if not self.enabled or not self.callback:
            print("Scheduler not enabled or no callback set")
            return

        if self.running:
            print("Scheduler already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print(f"Scheduler started: {self.frequency} at {self.schedule_time}")

    def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Scheduler stopped")

    def _run_loop(self) -> None:
        """Main scheduler loop."""
        while self.running:
            if self._should_run():
                print(f"[{datetime.now()}] Running scheduled pulse...")
                try:
                    if self.callback:
                        self.callback()
                    self._update_last_run()
                except Exception as e:
                    print(f"Error running scheduled pulse: {e}")

            # Check every minute
            time_module.sleep(60)

    def _should_run(self) -> bool:
        """Check if pulse should run now."""
        if not self.enabled:
            return False

        now = datetime.now()
        current_time = now.time()

        # Check if it's approximately the scheduled time (within 1 minute)
        scheduled_datetime = datetime.combine(now.date(), self.schedule_time)
        time_diff = abs((now - scheduled_datetime).total_seconds())

        if time_diff > 60:  # Not within scheduled time window
            return False

        # Check if we've already run recently
        last_run = self._get_last_run()
        if last_run:
            if self.frequency == "daily":
                # Don't run if we ran in the last 12 hours
                if (now - last_run).total_seconds() < 12 * 3600:
                    return False
            elif self.frequency == "weekly":
                # Don't run if we ran in the last 6 days
                if (now - last_run).total_seconds() < 6 * 24 * 3600:
                    return False

        return True

    def _get_last_run(self) -> Optional[datetime]:
        """Get the timestamp of the last run."""
        if not self.last_run_file.exists():
            return None

        try:
            with open(self.last_run_file, 'r') as f:
                data = json.load(f)
                return datetime.fromisoformat(data["last_run"])
        except Exception:
            return None

    def _update_last_run(self) -> None:
        """Update the last run timestamp."""
        with open(self.last_run_file, 'w') as f:
            json.dump({"last_run": datetime.now().isoformat()}, f)

    def run_now(self) -> None:
        """Manually trigger a pulse run."""
        if self.callback:
            print("Running pulse manually...")
            try:
                self.callback()
                self._update_last_run()
                print("Pulse completed successfully")
            except Exception as e:
                print(f"Error running pulse: {e}")
        else:
            print("No callback set")

    def get_next_run_time(self) -> Optional[datetime]:
        """Get the next scheduled run time."""
        if not self.enabled:
            return None

        now = datetime.now()
        next_run = datetime.combine(now.date(), self.schedule_time)

        # If scheduled time has passed today, schedule for tomorrow
        if now.time() > self.schedule_time:
            next_run += timedelta(days=1)

        # For weekly frequency, adjust accordingly
        if self.frequency == "weekly":
            # Schedule for next week if we ran recently
            last_run = self._get_last_run()
            if last_run and (now - last_run).days < 6:
                days_since_last = (now - last_run).days
                days_until_next = 7 - days_since_last
                next_run = now + timedelta(days=days_until_next)
                next_run = datetime.combine(next_run.date(), self.schedule_time)

        return next_run

    def get_status(self) -> dict:
        """Get scheduler status."""
        last_run = self._get_last_run()
        next_run = self.get_next_run_time()

        return {
            "enabled": self.enabled,
            "running": self.running,
            "frequency": self.frequency,
            "schedule_time": self.schedule_time.isoformat(),
            "last_run": last_run.isoformat() if last_run else None,
            "next_run": next_run.isoformat() if next_run else None,
        }
