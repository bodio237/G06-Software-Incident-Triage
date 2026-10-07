from ticket_app.analysis_models import Analysis, Request
from ticket_app.analysis_provider import AnalysisProvider, InvalidModelOutput


class AnalysisService:
    def __init__(self, provider: AnalysisProvider, policy: dict):
        self.provider = provider
        self.policy = policy

    def analyze(self, request: Request) -> Analysis:
        result = self.provider.analyze(request, self.policy)

        if result.category not in self.policy["categories"]:
            raise InvalidModelOutput(
                "Category outside the scenario contract"
            )

        # Enforce the scenario's priority policy after model inference.
        # High priority requires an explicit high-priority signal.
        text = f"{request.subject} {request.text}".lower()

        high_priority_words = [
            word.lower()
            for word in self.policy.get("high_priority_words", [])
        ]

        has_high_priority_signal = any(
            word in text for word in high_priority_words
        )

        if has_high_priority_signal:
            priority = "high"
        else:
            # Medium is the default priority. The model must not downgrade
            # a normal request to low without an explicit low-priority rule.
            priority = "medium"

        if result.priority != priority:
            result = result.model_copy(
                update={"priority": priority}
            )

        return result