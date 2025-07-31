import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import numpy as np


class EpisodeLogger:
    """
    A logger for recording steps in an episode of an environment simulation.
    
    Stores observations, actions, rewards, next observations, and done flags,
    and supports saving to and loading from JSON files.
    
    Supports both in-memory storage and streaming mode for large episodes.
    """

    def __init__(self, log_dir: str = "logs", streaming: bool = False, max_memory_steps: int = 10000) -> None:
        """
        Initialize the EpisodeLogger.

        Args:
            log_dir (str): Directory where logs will be saved. Created if it does not exist.
            streaming (bool): If True, enables streaming mode for large episodes.
            max_memory_steps (int): Maximum steps to keep in memory before switching to streaming.
        """
        self.log_dir: str = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.episode: List[Dict[str, Any]] = []
        self.streaming: bool = streaming
        self.max_memory_steps: int = max_memory_steps
        self._stream_file: Optional[str] = None
        self._stream_handle: Optional[object] = None
        self._step_count: int = 0
        self._episode_start_time: Optional[datetime] = None
        self._streaming_active: bool = False
        
        # Set up logging
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Set up logging configuration for the episode logger."""
        self.logger = logging.getLogger(__name__)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _serialize_observation(self, obs: Any) -> Any:
        """
        Serialize the observation into a JSON-serializable format.

        Args:
            obs: Observation to serialize.

        Returns:
            JSON-serializable representation of the observation.
        """
        if isinstance(obs, np.ndarray):  # Handle NumPy arrays
            return obs.tolist()
        elif isinstance(obs, (np.integer, np.floating)):  # Handle NumPy scalars
            return obs.item()
        elif isinstance(obs, (list, tuple)):  # Handle lists and tuples
            return [self._serialize_observation(item) for item in obs]
        elif isinstance(obs, dict):  # Handle dictionaries
            return {key: self._serialize_observation(value) for key, value in obs.items()}
        return obs

    def log_step(
        self,
        observation: Any,
        action: Union[int, float, List[Any], Any],
        reward: float,
        next_observation: Any,
        done: bool,
    ) -> None:
        """
        Log a single step of the episode.

        Args:
            observation: Current observation (supports numpy arrays, lists, or other types).
            action: Action taken at this step.
            reward: Reward received after taking the action.
            next_observation: Observation after taking the action (supports numpy arrays, lists, or other types).
            done: Boolean flag indicating if the episode is done.
        """
        # Start episode timing on first step
        if self._step_count == 0:
            self._episode_start_time = datetime.utcnow()
            self.logger.debug("Started new episode")
        
        step_data = {
            "observation": self._serialize_observation(observation),
            "action": action,
            "reward": reward,
            "next_observation": self._serialize_observation(next_observation),
            "done": done,
        }
        
        # Handle streaming mode and memory management
        if self.streaming and not self._streaming_active and len(self.episode) >= self.max_memory_steps:
            self._start_streaming()
        elif not self.streaming and len(self.episode) >= self.max_memory_steps:
            if self._step_count == self.max_memory_steps:  # Only warn once
                self.logger.warning(f"Episode exceeded {self.max_memory_steps} steps, performance may be impacted. Consider using streaming mode.")
            
            # Simple memory management: keep only recent steps in memory for very large episodes
            if len(self.episode) > self.max_memory_steps * 2:
                self.logger.warning(f"Episode size ({len(self.episode)}) is very large. Truncating older steps from memory.")
                # Keep only the most recent max_memory_steps
                self.episode = self.episode[-self.max_memory_steps:]
        
        # Store step data
        if self._streaming_active:
            self._write_step_to_stream(step_data)
        else:
            self.episode.append(step_data)
        self._step_count += 1
        
        if done:
            episode_duration = datetime.utcnow() - self._episode_start_time if self._episode_start_time else None
            self.logger.debug(f"Episode completed with {self._step_count} steps in {episode_duration}")
            self._finalize_streaming()

    def _start_streaming(self) -> None:
        """Start streaming mode by creating a temporary file and writing existing steps."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self._stream_file = os.path.join(self.log_dir, f"temp_stream_{timestamp}.jsonl")
        
        try:
            self._stream_handle = open(self._stream_file, 'w')
            # Write existing steps to stream
            for step in self.episode:
                json.dump(step, self._stream_handle)
                self._stream_handle.write('\n')
            self._stream_handle.flush()
            
            # Clear memory and activate streaming
            self.episode.clear()
            self._streaming_active = True
            self.logger.info(f"Activated streaming mode, writing to {self._stream_file}")
        except (IOError, OSError) as e:
            self.logger.error(f"Failed to start streaming mode: {e}")
            if self._stream_handle:
                self._stream_handle.close()
            self._stream_handle = None
            self._stream_file = None

    def _write_step_to_stream(self, step_data: Dict[str, Any]) -> None:
        """Write a single step to the stream file."""
        if self._stream_handle:
            try:
                json.dump(step_data, self._stream_handle)
                self._stream_handle.write('\n')
                if self._step_count % 100 == 0:  # Flush periodically
                    self._stream_handle.flush()
            except (IOError, OSError) as e:
                self.logger.error(f"Failed to write step to stream: {e}")

    def _finalize_streaming(self) -> None:
        """Finalize streaming by closing the stream file."""
        if self._stream_handle:
            try:
                self._stream_handle.close()
            except (IOError, OSError) as e:
                self.logger.error(f"Error closing stream file: {e}")
            finally:
                self._stream_handle = None

    def save(self, tag: Optional[str] = None, include_metadata: bool = True) -> str:
        """
        Save the logged episode steps to a JSON file.

        Args:
            tag (Optional[str]): Optional tag to include in the filename.
            include_metadata (bool): Whether to include episode metadata in the saved file.

        Returns:
            str: The file path where the episode was saved.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        safe_tag = ""
        if tag:
            # Keep only alphanumeric characters, underscore and hyphen
            safe_tag = re.sub(r"[^a-zA-Z0-9_-]", "", tag)
            if safe_tag:
                safe_tag += "_"

        filename = f"episode_{safe_tag}{timestamp}.json"
        path = os.path.join(self.log_dir, filename)

        # Handle streaming vs in-memory data
        if self._streaming_active and self._stream_file:
            # Read streamed data and combine with any remaining in-memory data
            data_to_save = []
            try:
                with open(self._stream_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            data_to_save.append(json.loads(line))
                # Add any remaining in-memory steps
                data_to_save.extend(self.episode)
            except (IOError, OSError, json.JSONDecodeError) as e:
                self.logger.error(f"Error reading stream file: {e}")
                # Fallback to in-memory data only
                data_to_save = self.episode
        else:
            # Use episode data directly - no need to copy since we're not modifying it
            data_to_save = self.episode
        
        if include_metadata:
            metadata = {
                "step_count": self._step_count,
                "timestamp": timestamp,
            }
            if self._episode_start_time:
                episode_duration = datetime.utcnow() - self._episode_start_time
                metadata["duration_seconds"] = episode_duration.total_seconds()
            
            # Create final data structure with metadata
            final_data = {
                "metadata": metadata,
                "steps": data_to_save
            }
        else:
            final_data = data_to_save

        try:
            with open(path, "w") as f:
                json.dump(final_data, f, indent=2)
            self.logger.info(f"Saved episode with {self._step_count} steps to {filename}")
        except (IOError, OSError, PermissionError) as e:
            raise RuntimeError(f"Failed to save episode to {path}: {e}")

        # Clean up streaming file if it exists
        if self._stream_file and os.path.exists(self._stream_file):
            try:
                os.remove(self._stream_file)
            except OSError as e:
                self.logger.warning(f"Could not remove stream file {self._stream_file}: {e}")

        # Reset episode state
        self.episode.clear()
        self._step_count = 0
        self._episode_start_time = None
        self._streaming_active = False
        self._stream_file = None
        self._stream_handle = None
        return path

    def load(self, filepath: str) -> Dict[str, Any]:
        """
        Load a previously saved episode from a JSON file.

        Args:
            filepath (str): Path to the JSON file.

        Returns:
            Dict[str, Any]: Dictionary containing episode data. If metadata was saved,
                          returns {"metadata": {...}, "steps": [...]}. Otherwise,
                          returns {"steps": [...]} for backward compatibility.
        """
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                
            # Handle backward compatibility - if data is a list, wrap it
            if isinstance(data, list):
                return {"steps": data}
            elif isinstance(data, dict) and "steps" in data:
                return data
            else:
                # Assume it's old format with just steps
                return {"steps": data}
                
        except (IOError, OSError, FileNotFoundError) as e:
            raise RuntimeError(f"Failed to load episode from {filepath}: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in episode file {filepath}: {e}")
    
    def get_episode_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current episode.
        
        Returns:
            Dict[str, Any]: Dictionary containing episode statistics.
        """
        if not self.episode:
            return {"step_count": 0, "total_reward": 0.0, "is_complete": False}
        
        total_reward = sum(step["reward"] for step in self.episode)
        is_complete = self.episode[-1]["done"] if self.episode else False
        
        stats = {
            "step_count": len(self.episode),
            "total_reward": total_reward,
            "is_complete": is_complete,
        }
        
        if self._episode_start_time:
            current_duration = datetime.utcnow() - self._episode_start_time
            stats["duration_seconds"] = current_duration.total_seconds()
        
        return stats
