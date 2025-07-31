from autogen_agentchat.agents import CodeExecutorAgent


class CodeExecutorAgent(CodeExecutorAgent):
    """An agent that extracts and executes code snippets found in received messages and returns the output.

    It is typically used within a team with another agent that generates code snippets to be executed.
    """
    pass