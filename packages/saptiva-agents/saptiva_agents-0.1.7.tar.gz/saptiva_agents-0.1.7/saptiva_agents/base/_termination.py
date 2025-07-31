from autogen_agentchat.base import TerminatedException, TerminationCondition
from autogen_agentchat.base._termination import AndTerminationConditionConfig, AndTerminationCondition, \
    OrTerminationConditionConfig, OrTerminationCondition


class TerminatedException(TerminatedException):
    pass


class TerminationCondition(TerminationCondition):
    pass


class AndTerminationCondition(AndTerminationCondition):
    pass


class OrTerminationCondition(OrTerminationCondition):
    pass
