from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor


class LocalCommandLineCodeExecutor(LocalCommandLineCodeExecutor):
    """A code executor class that executes code through a local command line
    environment.

    .. danger::

        This will execute code on the local machine. If being used with LLM generated code, caution should be used.

    Each code block is saved as a file and executed in a separate process in
    the working directory, and a unique file is generated and saved in the
    working directory for each code block.
    The code blocks are executed in the order they are received.
    Command line code is sanitized using regular expression match against a list of dangerous commands in order to prevent self-destructive
    commands from being executed which may potentially affect the users environment.
    Currently the only supported languages is Python and shell scripts.
    For Python code, use the language "python" for the code block.
    For shell scripts, use the language "bash", "shell", or "sh" for the code
    block.

    .. note::

        On Windows, the event loop policy must be set to `WindowsProactorEventLoopPolicy` to avoid issues with subprocesses.

        .. code-block:: python

            import sys
            import asyncio

            if sys.platform == "win32":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    Args:
        timeout (int): The timeout for the execution of any single code block. Default is 60.
        work_dir (str): The working directory for the code execution. If None,
            a default working directory will be used. The default working
            directory is the current directory ".".
        functions (List[Union[FunctionWithRequirements[Any, A], Callable[..., Any]]]): A list of functions that are available to the code executor. Default is an empty list.
        functions_module (str, optional): The name of the module that will be created to store the functions. Defaults to "functions".
        virtual_env_context (Optional[SimpleNamespace], optional): The virtual environment context. Defaults to None.

    Example:

    How to use `LocalCommandLineCodeExecutor` with a virtual environment different from the one used to run the autogen application:
    Set up a virtual environment using the `venv` module, and pass its context to the initializer of `LocalCommandLineCodeExecutor`. This way, the executor will run code within the new environment.

        .. code-block:: python

            import venv
            from pathlib import Path
            import asyncio

            from autogen_core import CancellationToken
            from autogen_core.code_executor import CodeBlock
            from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor


            async def example():
                work_dir = Path("coding")
                work_dir.mkdir(exist_ok=True)

                venv_dir = work_dir / ".venv"
                venv_builder = venv.EnvBuilder(with_pip=True)
                venv_builder.create(venv_dir)
                venv_context = venv_builder.ensure_directories(venv_dir)

                local_executor = LocalCommandLineCodeExecutor(work_dir=work_dir, virtual_env_context=venv_context)
                await local_executor.execute_code_blocks(
                    code_blocks=[
                        CodeBlock(language="bash", code="pip install matplotlib"),
                    ],
                    cancellation_token=CancellationToken(),
                )


            asyncio.run(example())

    """
    pass