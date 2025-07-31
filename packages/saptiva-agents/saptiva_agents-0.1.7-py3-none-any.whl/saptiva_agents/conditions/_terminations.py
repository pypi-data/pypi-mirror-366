from autogen_agentchat.conditions import (StopMessageTermination, MaxMessageTermination, TokenUsageTermination,
                                          TimeoutTermination, ExternalTermination, SourceMatchTermination,
                                          TextMessageTermination, FunctionCallTermination, FunctionalTermination)


class StopMessageTermination(StopMessageTermination):
    pass


class MaxMessageTermination(MaxMessageTermination):
    pass


class TokenUsageTermination(TokenUsageTermination):
    pass


class TimeoutTermination(TimeoutTermination):
    pass


class ExternalTermination(ExternalTermination):
    pass


class SourceMatchTermination(SourceMatchTermination):
    pass


class TextMessageTermination(TextMessageTermination):
    pass


class FunctionCallTermination(FunctionCallTermination):
    pass


class FunctionalTermination(FunctionalTermination):
    pass
