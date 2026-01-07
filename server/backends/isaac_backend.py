import time
import numpy as np
from typing import Optional, Tuple, Dict, Any
from server.robot_backend import RobotBackend, BackendStatus
import threading

class IsaacSimBackend(RobotBackend):
    def __init__(self, name: str = "isaac_sim", host: str = "localhost", port: int = 3000):
        super().__init__(name)
        self.host = host
        self.port = port
        self.current_position = np.array([0.0, 0.0, 0.5])
        self.current_orientation = np.array([1.0, 0.0, 0.0, 0.0])
        self.command_count = 0
        self.last_error: Optional[str] = None
        self.lock = threading.Lock()
    
    def connect(self) -> bool:
        try:
            time.sleep(0.1)
            self.status = BackendStatus.CONNECTED
            self.last_update_time = time.time()
            return True
        except Exception as e:
            self.status = BackendStatus.ERROR
            self.last_error = str(e)
            return False
    
    def disconnect(self):
        self.status = BackendStatus.DISCONNECTED
    
    def send_target_pose(self, position: np.ndarray, orientation: np.ndarray, velocity_limit: float = 0.1) -> bool:
        if not self.is_connected():
            return False
        with self.lock:
            alpha = min(velocity_limit * 0.1, 1.0)
            self.current_position = self.current_position * (1 - alpha) + position * alpha
            self.current_orientation = orientation
            self.command_count += 1
            self.last_update_time = time.time()
        return True
    
    def get_current_pose(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        if not self.is_connected():
            return None, None
        with self.lock:
            return self.current_position.copy(), self.current_orientation.copy()
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "command_count": self.command_count,
            "current_position": self.current_position.tolist(),
            "current_orientation": self.current_orientation.tolist(),
            "last_error": self.last_error,
            "last_update": self.last_update_time,
            "endpoint": f"{self.host}:{self.port}",
        }
