import datetime
import docker.errors
from fastmcp import FastMCP
import docker
import socket
import json
from pydantic import Field
import os

DOCKER_FILE="""
FROM python:3.11-slim

RUN mkdir /app
WORKDIR /app
COPY . /app

EXPOSE 8888

RUN pip install uv

RUN uv init

;

CMD ["uv", "run", "executer.py"]
"""

def code_security_check(code: str) -> bool:
    #TODO: Improve security checks to prevent dangerous operations
    """
    Perform a basic security check on the code to prevent dangerous operations.
    
    Args:
        code (str): The Python code to check.
    
    Returns:
        bool: True if the code is safe, False if it contains dangerous operations.
    """
    # Check for dangerous keywords
    dangerous_keywords = ["import os", "import sys", "import subprocess", "exec(", "eval(", "import shutil", "import socket", "import threading", "import multiprocessing", "import requests","import base64", "with open("]
    for keyword in dangerous_keywords:
        if keyword in code:
            return False
    return True



class CodeExecuterClient:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self):
        """Connect to the REPL server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            return False
    
    def send_code(self, code):
        """Send Python code to the server and get result"""
        if not self.socket:
            return None
        
        try:
            # Send code
            self.socket.send(code.encode('utf-8'))
            
            # Receive response
            response = self.socket.recv(4096).decode('utf-8')
            result = json.loads(response.strip())
            
            return result
        except Exception as e:
            return None
    
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            self.socket.close()


mcp = FastMCP("Code Execution Service")

@mcp.tool(description="Starts the code execution service.")
def start_code_executer(dependencies:list[str]=Field([],description="The dependencies you need for the future code execution")) -> str:
    """
    Starts an instance of code execution service.
    
    Args:
        dependencies (str): A string representing the dependencies required for the code execution service. Space-separated.
    
    Returns:
        str: A message indicating that the code execution service has started.
    """

    if dependencies:
        _DOCKER_FILE = DOCKER_FILE.replace(";","RUN uv add "+ " ".join(dependencies))
    else:
        _DOCKER_FILE= DOCKER_FILE.replace(";","")

    dockerfile_path = os.path.join(os.path.dirname(__file__), "code_executer", "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write(_DOCKER_FILE)
        
    docker_path = os.path.join(os.path.dirname(__file__), "code_executer")
    tag = f"code_executer-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    client = docker.from_env()
    client.images.build(
        path=docker_path,
        tag=tag,
    )
    container = client.containers.run(
        image=tag,
        detach=True,
        ports={'8888/tcp': 8888},
        name=tag
    )
    client.containers.prune()
    
    # for line in container.logs(stream=True):
    #     print(line.strip().decode('utf-8'))
    return "Code execution service started with the name: " + container.name

@mcp.tool(description="Stops the code execution service.")
def stop_code_executer(name:str=Field(...,description="The name of the code execution service you want to kill"),delete_service:bool=Field(True,description="Whether the container and the image will be deleted. This action is not reversible. If set to False container can be reused.")) -> str:
    """
    Stops the code execution service
    
    Returns:
        str: A message indicating that the code execution service has been stopped.
    """
    client = docker.from_env()
    try:
        container = client.containers.get(name)
        container.stop()
        if delete_service:
            container.remove()
            client.images.remove(container.image.id, force=True)
        return "Code execution service stopped."
    except docker.errors.NotFound:
        return "Code execution service isII  not running."


@mcp.tool(description="Executes Python code and returns the output.")
def execute_code(code: str=Field(...,description="Python code that will be executed")) -> str:
    """
    Executes the provided Python code and returns the output.
    
    Args:
        code (str): The Python code to execute.
    Returns:
        str: The output of the executed code.
    """
    if not code_security_check(code):
        return "Error: The code contains dangerous operations and cannot be executed."
    
    code_executer_client = CodeExecuterClient()
    if not code_executer_client.connect():
        return "Failed to connect to the code execution service."
    result = code_executer_client.send_code(code)
    code_executer_client.disconnect()
    
    if result is None:
        return "Error executing code."
    
    if result.get("type") == "error":
        return f"Error: {result['error']}"
    
    return result.get("output", "No output returned.")

@mcp.tool()
def reuse_code_executer(name:str=Field(...,description="The name of the code execution service you want to restart")) -> str:
    """
    Restarts the code execution service with the given name.
    
    Returns:
        str: A message indicating that the code execution service has been restarted.
    """
    client = docker.from_env()
    try:
        container = client.containers.get(name)
        container.start()
        return "Code execution service restarted."
    except docker.errors.NotFound:
        return "Code execution service is not running."

@mcp.prompt(title="Mathematics Solver")
def math_evaluation(expression:str=Field(...,description="The mathematical expression")):
    return f"Evaluate this mathematical expression using python code execution and SymPy library. Use SymPy for all advanced computations.\nExpression:\n{expression}"
    
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run()