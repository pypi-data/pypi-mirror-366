import socket
import sys
import io
import traceback
import threading
import json

class PythonREPLServer:
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.globals_dict = {}
        
    def start_server(self):
        """Start the socket server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            print(f"Python REPL Server started on {self.host}:{self.port}")
            print("Waiting for connection...")
            
            while True:
                client_socket, address = self.socket.accept()
                print(f"Connection from {address}")
                
                # Handle each client in a separate thread
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\nShutting down server...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.cleanup()
    
    def handle_client(self, client_socket, address):
        """Handle a client connection"""
        # Each client gets its own globals dictionary to maintain state
        client_globals = {}
        
        try:
            while True:
                # Receive data from client
                data = client_socket.recv(8192).decode('utf-8')
                with open("received_code.txt", "a") as f:
                    f.write(data + "\n")
                if not data:
                    break
                print(f"Received from {address}: {data.strip()}")
                
                # Execute the Python code and get result
                result = self.execute_code(data.strip(), client_globals)
                
                # Send result back to client
                response = json.dumps(result) + '\n'
                client_socket.send(response.encode('utf-8'))
                
        except ConnectionResetError:
            print(f"Client {address} disconnected")
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            print(f"Connection with {address} closed")
    
    def execute_code(self, code, globals_dict):
        """Execute Python code and return the result"""
        if not code.strip():
            return {"type": "empty", "output": ""}
        
        # Special commands
        if code.strip() == "clear":
            globals_dict.clear()
            return {"type": "success", "output": "Globals cleared"}
        
        if code.strip() == "exit":
            return {"type": "exit", "output": "Goodbye!"}

        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        
        try:
            # Redirect stdout and stderr
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            # Try to compile and execute the code
            try:
                # First, try to compile as an expression for immediate evaluation
                compiled = compile(code, '<socket>', 'eval')
                result = eval(compiled, globals_dict)

                # Get any output
                output = stdout_capture.getvalue()
                error_output = stderr_capture.getvalue()
                
                # Format the result - show result for any expression that produces a value
                # Only exclude None results to avoid showing None for statements
                if result is not None:
                    if output:
                        output += str(result)
                    else:
                        output = str(result)
                
                return {
                    "type": "success",
                    "output": output,
                    "error": error_output if error_output else None
                }
                
            except SyntaxError:
                # If it's not an expression, try as a statement
                try:
                    compiled = compile(code, '<socket>', 'exec')
                    exec(compiled, globals_dict)
                    
                    # Get any output
                    output = stdout_capture.getvalue()
                    error_output = stderr_capture.getvalue()
                    return {
                        "type": "success",
                        "output": output,
                        "error": error_output if error_output else None
                    }
                    
                except Exception as e:
                    error_output = stderr_capture.getvalue()
                    traceback_str = traceback.format_exc()
                    print(f"Execution error: {error_output + traceback_str}")
                    return {
                        "type": "error",
                        "output": "",
                        "error": error_output + traceback_str
                    }
            
        except Exception as e:
            error_output = stderr_capture.getvalue()
            traceback_str = traceback.format_exc()
            
            return {
                "type": "error",
                "output": "",
                "error": error_output + traceback_str
            }
            
        finally:
            # Restore stdout and stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def cleanup(self):
        """Clean up resources"""
        if self.socket:
            self.socket.close()

def main():
    server = PythonREPLServer()
    server.start_server()

if __name__ == "__main__":
    main()