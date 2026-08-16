from abc import ABC, abstractmethod
import time
import uuid

class JobBoardAdapter(ABC):
    @abstractmethod
    def publish(self, job):
        pass

class MockJobBoardAdapter(JobBoardAdapter):
    def __init__(self, channel_name):
        self.channel_name = channel_name

    def publish(self, job):
        time.sleep(0.5)
        fake_id = str(uuid.uuid4())[:8]
        return f"https://{self.channel_name}.example.com/jobs/{fake_id}"

ADAPTERS = {
    "linkedin": MockJobBoardAdapter("linkedin"),
    "internshala": MockJobBoardAdapter("internshala"),
    "indeed": MockJobBoardAdapter("indeed"),
}