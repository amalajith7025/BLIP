from __future__ import annotations

from collections import OrderedDict

from app.analysis.capabilities.schemas import BusinessPurpose

from .schemas import BusinessGoal


class BusinessGoalRegistry:
    """
    Deterministic metadata registry for business goals.
    """

    def __init__(self):
        self._goals: OrderedDict[str, BusinessGoal] = OrderedDict()

    def register(self, goal: BusinessGoal) -> None:
        self._validate_goal(goal)
        self._goals[goal.goal_id] = goal

    def register_many(self, goals: list[BusinessGoal]) -> None:
        for goal in goals:
            self.register(goal)

    def get_by_id(self, goal_id: str) -> BusinessGoal | None:
        return self._goals.get(goal_id)

    def list_available(self) -> list[BusinessGoal]:
        return list(self._goals.values())

    def search_by_business_purpose(
        self,
        business_purpose: BusinessPurpose,
    ) -> list[BusinessGoal]:
        return [
            goal
            for goal in self._goals.values()
            if goal.business_purpose == business_purpose
        ]

    def get_required_capabilities(self, goal_id: str) -> list[str]:
        goal = self._get_or_raise(goal_id)
        return list(goal.required_analytical_capabilities)

    def get_optional_capabilities(self, goal_id: str) -> list[str]:
        goal = self._get_or_raise(goal_id)
        return list(goal.optional_analytical_capabilities)

    def _get_or_raise(self, goal_id: str) -> BusinessGoal:
        goal = self._goals.get(goal_id)
        if goal is None:
            raise KeyError(f"Business goal '{goal_id}' is not registered")
        return goal

    @staticmethod
    def _validate_goal(goal: BusinessGoal) -> None:
        if not goal.goal_id.strip():
            raise ValueError("goal_id is required")

        if not goal.name.strip():
            raise ValueError("name is required")

        if not goal.required_analytical_capabilities:
            raise ValueError("required_analytical_capabilities must not be empty")