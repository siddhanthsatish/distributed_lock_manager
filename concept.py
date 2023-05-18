import multiprocessing
import socket
import threading
import time


class LockManager:
    def __init__(self, host, port):
        """
        Initializes the LockManager object.

        Args:
            host (str): The host name or IP address.
            port (int): The port number.
        """
        self.host = host
        self.port = port
        self.locks = {}  # Lock metadata and state
        self.lock_timers = {}
        self.server_thread = None
        self.lock_timeout = 10  # Lock timeout in seconds

    def start(self):
        """
        Starts the lock manager server in a separate thread.
        """
        self.server_thread = threading.Thread(target=self._start_server)
        self.server_thread.start()

    def stop(self):
        """
        Stops the lock manager server and waits for the thread to join.
        """
        if self.server_thread:
            self.server_thread.join()

    def _start_server(self):
        """
        Starts the lock manager server to listen for client connections.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)

        print(f"Lock manager listening on {self.host}:{self.port}")

        while True:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(target=self._handle_client, args=(client_socket,))
            client_thread.start()

    def _handle_client(self, client_socket):
        """
        Handles client connections and processes client requests.

        Args:
            client_socket (socket): The client socket object.
        """
        while True:
            request = client_socket.recv(1024).decode()
            if not request:
                break

            response = self._process_request(request)
            client_socket.sendall(response.encode())

        client_socket.close()

    def _process_request(self, request):
        """
        Processes client requests and performs lock operations.

        Args:
            request (str): The client request.

        Returns:
            str: The response to send back to the client.
        """
        parts = request.split()
        command = parts[0]

        if command == "LOCK":
            lock_name = parts[1]
            client_id = parts[2]
            lock_type = parts[3]

            if lock_name not in self.locks:
                self.locks[lock_name] = {"owners": [], "type": None}

            lock = self.locks[lock_name]

            if lock_type == "READ":
                if lock["type"] == "WRITE":
                    response = "FAILURE"
                else:
                    lock["owners"].append(client_id)
                    lock["type"] = "READ"
                    response = "SUCCESS"
            elif lock_type == "WRITE":
                if lock["type"] or lock["owners"]:
                    response = "FAILURE"
                else:
                    lock["owners"].append(client_id)
                    lock["type"] = "WRITE"
                    response = "SUCCESS"

        elif command == "UNLOCK":
            lock_name = parts[1]
            client_id = parts[2]

            if lock_name in self.locks:
                lock = self.locks[lock_name]
                if client_id in lock["owners"]:
                    lock["owners"].remove(client_id)
                    if len(lock["owners"]) == 0:
                        lock["type"] = None
                    response = "SUCCESS"
                else:
                    response = "FAILURE"
            else:
                response = "FAILURE"

        self._reset_lock_timeout(lock_name)  # Reset lock timeout for the lock

        return response

    def _reset_lock_timeout(self, lock_name):
        """
        Resets the lock timeout for a given lock.

        Args:
            lock_name (str): The name of the lock.
        """
        if lock_name in self.lock_timers:
            self.lock_timers[lock_name].cancel()

        timer = threading.Timer(self.lock_timeout, self._lock_timeout_handler, args=(lock_name,))
        self.lock_timers[lock_name] = timer
        timer.start()

    def _lock_timeout_handler(self, lock_name):
        """
        Handles the lock timeout by releasing the lock.

        Args:
            lock_name (str): The name of the lock.
        """
        if lock_name in self.locks:
            lock = self.locks[lock_name]
            lock["owners"] = []
            lock["type"] = None
            print(f"Lock timeout for {lock_name}. Lock released.")

    def request_lock(self, lock_name, client_id, lock_type):
        """
        Requests a lock from the lock manager.

        Args:
            lock_name (str): The name of the lock.
            client_id (str): The ID of the client requesting the lock.
            lock_type (str): The type of lock requested (READ or WRITE).

        Returns:
            str: The response indicating the success or failure of the lock request.
        """
        request = f"LOCK {lock_name} {client_id} {lock_type}"
        response = self._send_request(request)
        return response

    def release_lock(self, lock_name, client_id):
        """
        Releases a lock from the lock manager.

        Args:
            lock_name (str): The name of the lock.
            client_id (str): The ID of the client releasing the lock.

        Returns:
            str: The response indicating the success or failure of the lock release.
        """
        request = f"UNLOCK {lock_name} {client_id}"
        response = self._send_request(request)
        return response

    def _send_request(self, request):
        """
        Sends a request to the lock manager server.

        Args:
            request (str): The request to send.

        Returns:
            str: The response received from the server.
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))
        client_socket.sendall(request.encode())
        response = client_socket.recv(1024).decode()
        client_socket.close()
        return response


# Testing and Evaluation
def test_lock_manager():
    lock_manager = LockManager("localhost", 8888)
    lock_manager_process = multiprocessing.Process(target=lock_manager.start)
    lock_manager_process.start()

    # Pause for a moment to allow the server to start
    time.sleep(1)

    # Test case 1: Single process requesting a lock
    response1 = lock_manager.request_lock("resource1", "client1", "WRITE")
    print(f"Test case 1 response: {response1}")
    assert response1 == "SUCCESS"

    # Test case 2: Multiple processes requesting conflicting locks
    response2 = lock_manager.request_lock("resource1", "client2", "WRITE")
    response3 = lock_manager.request_lock("resource1", "client3", "READ")
    print(f"Test case 2 response 1: {response2}")
    print(f"Test case 2 response 2: {response3}")
    assert response2 == "FAILURE"
    assert response3 == "FAILURE"

    # Test case 3: Releasing locks
    release_response1 = lock_manager.release_lock("resource1", "client1")
    print(f"Test case 3 release response: {release_response1}")
    assert release_response1 == "SUCCESS"

    # Test case 4: Multiple processes requesting non-conflicting locks
    response4 = lock_manager.request_lock("resource1", "client2", "WRITE")
    response5 = lock_manager.request_lock("resource2", "client3", "READ")
    print(f"Test case 4 response 1: {response4}")
    print(f"Test case 4 response 2: {response5}")
    assert response4 == "SUCCESS"
    assert response5 == "SUCCESS"

    lock_manager_process.terminate()
    lock_manager_process.join()
    print("All test cases passed successfully.")

# Usage example
if __name__ == "__main__":
    print("Running Tests on the system")
    test_lock_manager()