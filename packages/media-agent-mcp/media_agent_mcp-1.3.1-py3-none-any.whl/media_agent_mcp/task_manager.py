#!/usr/bin/env python3
"""Task Manager for Media Agent MCP Server.

This module provides task tracking and data management functionality.
It maintains local data for tasks with simplified structure:
- task_id: unique identifier
- create_time: creation timestamp
- update_time: last update timestamp
- image_prompt: array of prompts
- image_generated: array of generated image URLs
- image_select: array of selected image URLs
- video_prompt: array of video prompts
- video_generation: array of generated video URLs
- video_select: array of selected video URLs
- video_concat: array of concatenated video URLs
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class TaskManager:
    """Manages task data and tracking for MCP operations."""
    
    def __init__(self, data_file: str = "task_data.json"):
        """Initialize TaskManager with data file path.
        
        Args:
            data_file: Path to the JSON file for storing task data
        """
        self.data_file = Path(data_file)
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._load_data()
    
    def _load_data(self):
        """Load existing task data from file."""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                logger.info(f"Loaded task data from {self.data_file}")
            else:
                logger.info("No existing task data file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading task data: {e}")
            self.tasks = {}
    
    def _save_data(self):
        """Save current task data to file."""
        try:
            # Ensure directory exists
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved task data to {self.data_file}")
        except Exception as e:
            logger.error(f"Error saving task data: {e}")
    
    def record_task_data(self, task_id: str, attribute: str, value: Any):
        """Record data for a specific task and attribute.
        
        Args:
            task_id: Unique identifier for the task
            attribute: Type of operation (image_prompt, image_generated, etc.)
            value: Data to record for this operation
        """
        if not task_id:
            return
        
        # Initialize task if not exists
        if task_id not in self.tasks:
            self.tasks[task_id] = {
                'task_id': task_id,
                'create_time': datetime.now().isoformat(),
                'update_time': datetime.now().isoformat(),
                'image_prompt': [],
                'image_generated': [],
                'image_select': [],
                'video_prompt': [],
                'video_generation': [],
                'video_select': [],
                'video_concat': []
            }
        
        # Add value to the appropriate array
        if attribute in self.tasks[task_id] and isinstance(self.tasks[task_id][attribute], list):
            self.tasks[task_id][attribute].append(value)
        else:
            # Handle unknown attributes by creating them as arrays
            self.tasks[task_id][attribute] = [value]
        
        # Update timestamp
        self.tasks[task_id]['update_time'] = datetime.now().isoformat()
        
        # Save to file
        self._save_data()
        
        logger.info(f"Recorded data for task {task_id}, attribute {attribute}: {value}")
    
    def get_task_data(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get all data for a specific task.
        
        Args:
            task_id: Unique identifier for the task
            
        Returns:
            Dictionary containing all recorded data for the task, or None if not found
        """
        return self.tasks.get(task_id)
    
    def get_task_attribute_data(self, task_id: str, attribute: str) -> List[Any]:
        """Get data for a specific task and attribute.
        
        Args:
            task_id: Unique identifier for the task
            attribute: Type of operation to retrieve
            
        Returns:
            List of recorded values for the attribute
        """
        if task_id in self.tasks and attribute in self.tasks[task_id]:
            return self.tasks[task_id][attribute]
        return []
    
    def list_tasks(self) -> List[str]:
        """Get list of all task IDs.
        
        Returns:
            List of task IDs
        """
        return list(self.tasks.keys())
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task and all its data.
        
        Args:
            task_id: Unique identifier for the task to delete
            
        Returns:
            True if task was deleted, False if task didn't exist
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_data()
            logger.info(f"Deleted task {task_id}")
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about tasks and operations.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_tasks': len(self.tasks),
            'attributes': {
                'image_prompt': 0,
                'image_generated': 0,
                'image_select': 0,
                'video_prompt': 0,
                'video_generation': 0,
                'video_select': 0,
                'video_concat': 0
            }
        }
        
        for task_data in self.tasks.values():
            for attr in stats['attributes']:
                if attr in task_data and isinstance(task_data[attr], list):
                    stats['attributes'][attr] += len(task_data[attr])
        
        return stats

# Global task manager instance
_task_manager = None

def get_task_manager() -> TaskManager:
    """Get the global task manager instance.
    
    Returns:
        TaskManager instance
    """
    global _task_manager
    if _task_manager is None:
        # Store data file in the project directory
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_file = data_dir / "task_data.json"
        _task_manager = TaskManager(str(data_file))
    return _task_manager

def record_task_operation(task_id: Optional[str], operation_type: str, data: Any):
    """Convenience function to record task operation.
    
    Args:
        task_id: Optional task ID
        operation_type: Type of operation
        data: Data to record
    """
    if task_id:
        task_manager = get_task_manager()
        task_manager.record_task_data(task_id, operation_type, data)