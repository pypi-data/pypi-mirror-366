from pathlib import Path
from typing import Tuple

import yaml

from ..base.models import AgentConfig, BuildConfig, ConcurrencyConfig, PlatformConfig


class ConfigParser:
    @staticmethod
    def load_config(config_path: str = "agent.yaml") -> AgentConfig:
        """Load and parse agent configuration from YAML"""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file {config_path} not found")

        with open(path, "r") as file:
            data = yaml.safe_load(file)

        # Parse nested configurations
        build_config = BuildConfig(**data.get("build", {}))
        platform_config = PlatformConfig(**data["platform"])
        concurrency_config = ConcurrencyConfig(**data.get("concurrency", {}))

        return AgentConfig(
            build=build_config,
            agent=data["agent"],
            platform=platform_config,
            concurrency=concurrency_config,
        )

    @staticmethod
    def get_agent_class_info(agent_path: str) -> Tuple[str, str]:
        """Parse agent path like 'main.py:DemoAgent'"""
        module_path, class_name = agent_path.split(":")
        return module_path, class_name
