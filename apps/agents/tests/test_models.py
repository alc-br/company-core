import pytest
from apps.agents.models import Agent


class TestAgent:
    def test_str(self):
        agent = Agent(name="Test Agent")
        assert "Test Agent" in str(agent)
