from typing import Dict, List

from .interfaces import AnalysisPlugin
from .schemas import DatasetProfile


class AnalysisRegistry:
    """
    Registers and manages scientific analysis plugins.
    """

    def __init__(self):
        self._plugins: Dict[str, AnalysisPlugin] = {}

    def register(self, plugin: AnalysisPlugin):
        self._plugins[plugin.name] = plugin

    def get(self, name: str):
        return self._plugins.get(name)

    def all(self) -> List[AnalysisPlugin]:
        return list(self._plugins.values())

    def applicable(
        self,
        profile: DatasetProfile,
    ) -> List[AnalysisPlugin]:

        applicable_plugins = []

        for plugin in self._plugins.values():
            if not plugin.validate(profile):
                continue

            minimum_samples = getattr(plugin, "minimum_samples", None)
            if minimum_samples is not None and profile.rows < minimum_samples:
                continue

            applicable_plugins.append(plugin)

        return applicable_plugins