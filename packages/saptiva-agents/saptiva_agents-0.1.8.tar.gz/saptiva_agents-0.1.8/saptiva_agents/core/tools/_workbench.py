from autogen_core.tools import ToolResult, Workbench


class ToolResult(ToolResult):
    """
    A result of a tool execution by a workbench.
    """
    pass



class Workbench(Workbench):
    """
    A workbench is a component that provides a set of tools that may share
    resources and state.

    A workbench is responsible for managing the lifecycle of the tools and
    providing a single interface to call them. The tools provided by the workbench
    may be dynamic and their availabilities may change after each tool execution.

    A workbench can be started by calling the :meth:`~autogen_core.tools.Workbench.start` method
    and stopped by calling the :meth:`~autogen_core.tools.Workbench.stop` method.
    It can also be used as an asynchronous context manager, which will automatically
    start and stop the workbench when entering and exiting the context.
    """
    pass
