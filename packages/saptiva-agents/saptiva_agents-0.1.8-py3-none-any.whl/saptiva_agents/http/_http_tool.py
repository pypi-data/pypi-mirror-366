from autogen_ext.tools.http import HttpTool


class HttpTool(HttpTool):
    """A wrapper for using an HTTP server as a tool.

    Args:
        name (str): The name of the tool.
        description (str, optional): A description of the tool.
        scheme (str): The scheme to use for the request. Must be either "http" or "https".
        host (str): The host to send the request to.
        port (int): The port to send the request to.
        path (str, optional): The path to send the request to. Defaults to "/".
            Can include path parameters like "/{param1}/{param2}" which will be templated from input args.
        method (str, optional): The HTTP method to use, will default to POST if not provided.
            Must be one of "GET", "POST", "PUT", "DELETE", "PATCH".
        headers (dict[str, Any], optional): A dictionary of headers to send with the request.
        json_schema (dict[str, Any]): A JSON Schema object defining the expected parameters for the tool.
            Path parameters must also be included in the schema and must be strings.
        return_type (Literal["text", "json"], optional): The type of response to return from the tool.
            Defaults to "text".

    .. note::
        This tool requires the :code:`http-tool` extra for the :code:`autogen-ext` package.
    """
    pass
