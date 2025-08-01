"""
Scheduling utilities for the Demiurg framework.

This module provides helper functions for schedule parsing, validation,
and execution management.
"""

import re
from datetime import datetime, time, timedelta
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

import pytz
from croniter import croniter
from dateutil import parser as date_parser

if TYPE_CHECKING:
    from ..models import ScheduleConfig


def validate_cron_expression(expression: str) -> bool:
    """
    Validate a cron expression.
    
    Args:
        expression: Cron expression to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        croniter(expression)
        return True
    except (ValueError, TypeError):
        return False


def parse_natural_schedule(text: str) -> Optional[Dict[str, Any]]:
    """
    Parse natural language schedule descriptions.
    
    Examples:
        - "every day at 9am"
        - "every Monday at 2:30 PM"
        - "every 30 minutes"
        - "daily at noon"
        
    Args:
        text: Natural language schedule description
        
    Returns:
        Schedule configuration dict or None if unparseable
    """
    text = text.lower().strip()
    
    # Daily patterns
    daily_match = re.match(r'(?:every day|daily) at (\d{1,2}):?(\d{2})?\s*(am|pm)?', text)
    if daily_match:
        hour = int(daily_match.group(1))
        minute = int(daily_match.group(2) or '0')
        period = daily_match.group(3)
        
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
            
        return {
            'type': 'daily',
            'time': f"{hour:02d}:{minute:02d}"
        }
    
    # Weekly patterns
    weekdays = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    for day_name, day_num in weekdays.items():
        if day_name in text:
            time_match = re.search(r'at (\d{1,2}):?(\d{2})?\s*(am|pm)?', text)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or '0')
                period = time_match.group(3)
                
                if period == 'pm' and hour != 12:
                    hour += 12
                elif period == 'am' and hour == 12:
                    hour = 0
                    
                return {
                    'type': 'cron',
                    'params': {
                        'day_of_week': day_num,
                        'hour': hour,
                        'minute': minute
                    }
                }
    
    # Interval patterns
    interval_match = re.match(r'every (\d+)\s*(minute|hour|day)s?', text)
    if interval_match:
        value = int(interval_match.group(1))
        unit = interval_match.group(2)
        
        params = {}
        if unit == 'minute':
            params['minutes'] = value
        elif unit == 'hour':
            params['hours'] = value
        elif unit == 'day':
            params['days'] = value
            
        return {
            'type': 'interval',
            'params': params
        }
    
    # Special times
    special_times = {
        'noon': '12:00',
        'midnight': '00:00',
        'morning': '09:00',
        'afternoon': '14:00',
        'evening': '18:00'
    }
    
    for special, time_str in special_times.items():
        if special in text:
            return {
                'type': 'daily',
                'time': time_str
            }
    
    return None


def calculate_next_run(schedule: Union[str, Dict[str, Any]], timezone: str = 'UTC') -> datetime:
    """
    Calculate the next run time for a schedule.
    
    Args:
        schedule: Cron expression or schedule config
        timezone: Timezone name (default: UTC)
        
    Returns:
        Next run datetime
    """
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    
    if isinstance(schedule, str):
        # Cron expression
        cron = croniter(schedule, now)
        return cron.get_next(datetime)
    
    elif isinstance(schedule, dict):
        schedule_type = schedule.get('type', 'cron')
        
        if schedule_type == 'daily':
            # Parse time
            time_str = schedule.get('time', '00:00')
            hour, minute = map(int, time_str.split(':'))
            
            # Calculate next occurrence
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            
            return next_run
        
        elif schedule_type == 'interval':
            params = schedule.get('params', {})
            delta = timedelta(**params)
            return now + delta
        
        elif schedule_type == 'cron':
            params = schedule.get('params', {})
            # Build cron expression from params
            minute = params.get('minute', '*')
            hour = params.get('hour', '*')
            day = params.get('day', '*')
            month = params.get('month', '*')
            day_of_week = params.get('day_of_week', '*')
            
            cron_expr = f"{minute} {hour} {day} {month} {day_of_week}"
            cron = croniter(cron_expr, now)
            return cron.get_next(datetime)
    
    raise ValueError(f"Invalid schedule format: {schedule}")


def format_schedule_description(schedule: Union[str, Dict[str, Any]]) -> str:
    """
    Format a schedule into a human-readable description.
    
    Args:
        schedule: Schedule configuration
        
    Returns:
        Human-readable description
    """
    if isinstance(schedule, str):
        # Try to parse cron
        parts = schedule.split()
        if len(parts) == 5:
            minute, hour, day, month, dow = parts
            
            # Common patterns
            if minute == '0' and hour != '*' and day == '*' and month == '*' and dow == '*':
                return f"Daily at {hour}:00"
            elif minute != '*' and hour != '*' and day == '*' and month == '*' and dow == '*':
                return f"Daily at {hour}:{minute}"
            elif dow != '*' and minute != '*' and hour != '*':
                days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                return f"{days[int(dow)]} at {hour}:{minute}"
            
        return f"Cron: {schedule}"
    
    elif isinstance(schedule, dict):
        schedule_type = schedule.get('type')
        
        if schedule_type == 'daily':
            return f"Daily at {schedule.get('time', '00:00')}"
        
        elif schedule_type == 'interval':
            params = schedule.get('params', {})
            parts = []
            for unit, value in params.items():
                parts.append(f"{value} {unit}")
            return f"Every {' '.join(parts)}"
        
        elif schedule_type == 'cron':
            params = schedule.get('params', {})
            if 'day_of_week' in params:
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day = days[params['day_of_week']]
                time_str = f"{params.get('hour', 0)}:{params.get('minute', 0):02d}"
                return f"{day} at {time_str}"
    
    return str(schedule)


def merge_schedule_configs(base: 'ScheduleConfig', override: 'ScheduleConfig') -> 'ScheduleConfig':
    """
    Merge two schedule configurations.
    
    Args:
        base: Base configuration
        override: Override configuration
        
    Returns:
        Merged configuration
    """
    from ..models import ScheduleConfig
    
    # Start with base config
    merged_data = base.model_dump()
    
    # Override with non-None values
    override_data = override.model_dump(exclude_none=True)
    merged_data.update(override_data)
    
    # Merge tasks list
    if 'tasks' in override_data:
        # Create a mapping of task names
        base_tasks = {task.name: task for task in base.tasks}
        
        # Update or add tasks
        for override_task in override.tasks:
            if override_task.name in base_tasks:
                # Update existing task
                base_task = base_tasks[override_task.name]
                task_data = base_task.model_dump()
                task_data.update(override_task.model_dump(exclude_none=True))
                base_tasks[override_task.name] = type(base_task)(**task_data)
            else:
                # Add new task
                base_tasks[override_task.name] = override_task
        
        merged_data['tasks'] = list(base_tasks.values())
    
    return ScheduleConfig(**merged_data)


def create_schedule_from_yaml(yaml_config: Dict[str, Any]) -> 'ScheduleConfig':
    """
    Create a schedule configuration from YAML data.
    
    Args:
        yaml_config: YAML configuration dict
        
    Returns:
        ScheduleConfig instance
    """
    from ..models import ScheduleConfig, ScheduledTask
    
    # Parse tasks
    tasks = []
    for task_data in yaml_config.get('tasks', []):
        # Parse natural language schedules if present
        if isinstance(task_data.get('schedule'), str) and not validate_cron_expression(task_data['schedule']):
            parsed = parse_natural_schedule(task_data['schedule'])
            if parsed:
                task_data['schedule'] = parsed
        
        tasks.append(ScheduledTask(**task_data))
    
    # Create config
    config_data = yaml_config.copy()
    config_data['tasks'] = tasks
    
    return ScheduleConfig(**config_data)


class ScheduleStatePersistence:
    """
    Handle persistence of schedule state across restarts.
    """
    
    def __init__(self, agent_id: str, state_dir: str = "/tmp/demiurg_schedules"):
        """Initialize state persistence."""
        self.agent_id = agent_id
        self.state_file = Path(state_dir) / f"{agent_id}_schedule_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
    
    def save_state(self, scheduled_tasks: Dict[str, Any]):
        """Save current schedule state."""
        import json
        
        state = {
            'agent_id': self.agent_id,
            'timestamp': datetime.utcnow().isoformat(),
            'tasks': {}
        }
        
        for name, info in scheduled_tasks.items():
            job = info['job']
            state['tasks'][name] = {
                'type': info['type'],
                'config': info['config'],
                'schedule': info['schedule'],
                'last_run': job.last_run_time.isoformat() if job.last_run_time else None,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None
            }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load saved schedule state."""
        import json
        
        if not self.state_file.exists():
            return None
        
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schedule state: {e}")
            return None
    
    def clear_state(self):
        """Clear saved state."""
        if self.state_file.exists():
            self.state_file.unlink()


# Import for convenience
from pathlib import Path
import logging

logger = logging.getLogger(__name__)