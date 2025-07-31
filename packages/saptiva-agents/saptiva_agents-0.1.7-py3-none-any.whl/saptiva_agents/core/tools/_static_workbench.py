from autogen_core.tools import StaticWorkbench


class StaticWorkbench(StaticWorkbench):
    """
    A workbench that provides a static set of tools that do not change after
    each tool execution.

    Args:
        tools (List[BaseTool[Any, Any]]): A list of tools to be included in the workbench.
            The tools should be subclasses of :class:`~saptiva_agents.tools.BaseTool`.
    """
    pass
