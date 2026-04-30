from src.repositories.monitor_repository import MonitorRepository


class MonitorService:
    def __init__(self, monitor_repository: MonitorRepository) -> None:
        self.monitor_repository = monitor_repository
