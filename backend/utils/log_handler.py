"""
Session-based log handler for capturing and streaming backend logs
"""
import logging
from typing import Dict, List
from collections import deque
from datetime import datetime


class SessionLogHandler(logging.Handler):
    """Custom log handler that stores logs per session"""
    
    def __init__(self, max_logs_per_session=200):
        super().__init__()
        self.session_logs: Dict[str, deque] = {}
        self.max_logs = max_logs_per_session
        self.current_session = None
        
        # Set format
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.setFormatter(formatter)
    
    def set_session(self, session_id: str):
        """Set the current session ID for log routing"""
        self.current_session = session_id
        if session_id not in self.session_logs:
            self.session_logs[session_id] = deque(maxlen=self.max_logs)
    
    def emit(self, record):
        """Emit a log record to the current session's buffer"""
        try:
            if self.current_session:
                log_entry = self.format(record)
                self.session_logs[self.current_session].append(log_entry)
        except Exception:
            self.handleError(record)
    
    def get_logs(self, session_id: str, last_n: int = None) -> List[str]:
        """Get logs for a specific session"""
        if session_id not in self.session_logs:
            return []
        
        logs = list(self.session_logs[session_id])
        
        if last_n:
            return logs[-last_n:]
        return logs
    
    def clear_session(self, session_id: str):
        """Clear logs for a session"""
        if session_id in self.session_logs:
            del self.session_logs[session_id]


# Global handler instance
_global_handler = None


def get_session_handler() -> SessionLogHandler:
    """Get or create the global session log handler"""
    global _global_handler
    if _global_handler is None:
        _global_handler = SessionLogHandler()
        
        # Attach to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(_global_handler)
        root_logger.setLevel(logging.INFO)
    
    return _global_handler

