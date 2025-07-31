from autogen_core.tools import FunctionTool


class FunctionTool(FunctionTool):
    """
    Create custom tools by wrapping standard Python functions.

    `FunctionTool` offers an interface for executing Python functions either asynchronously or synchronously.
    Each function must include type annotations for all parameters and its return type. These annotations
    enable `FunctionTool` to generate a schema necessary for input validation, serialization, and for informing
    the LLM about expected parameters. When the LLM prepares a function call, it leverages this schema to
    generate arguments that align with the function's specifications.

    .. note::

        It is the user's responsibility to verify that the tool's output type matches the expected type.

    Args:
        func (Callable[..., ReturnT | Awaitable[ReturnT]]): The function to wrap and expose as a tool.
        description (str): A description to inform the model of the function's purpose, specifying what
            it does and the context in which it should be called.
        name (str, optional): An optional custom name for the tool. Defaults to
            the function's original name if not provided.
        strict (bool, optional): If set to True, the tool schema will only contain arguments that are explicitly
            defined in the function signature, and no default values will be allowed. Defaults to False.
            This is required to be set to True when used with models in structured output mode.

    Example:

        .. code-block:: python

            import random
            from autogen_core import CancellationToken
            from autogen_core.tools import FunctionTool
            from typing_extensions import Annotated
            import asyncio


            async def get_stock_price(ticker: str, date: Annotated[str, "Date in YYYY/MM/DD"]) -> float:
                # Simulates a stock price retrieval by returning a random float within a specified range.
                return random.uniform(10, 200)


            async def example():
                # Initialize a FunctionTool instance for retrieving stock prices.
                stock_price_tool = FunctionTool(get_stock_price, description="Fetch the stock price for a given ticker.")

                # Execute the tool with cancellation support.
                cancellation_token = CancellationToken()
                result = await stock_price_tool.run_json({"ticker": "AAPL", "date": "2021/01/01"}, cancellation_token)

                # Output the result as a formatted string.
                print(stock_price_tool.return_value_as_string(result))


            asyncio.run(example())
    """
    pass