# Lock Manager

## Description

The `LockManager` is a Python class that provides a simple mechanism for managing locks over a network. This lock manager is useful in distributed systems where multiple processes may need to coordinate access to shared resources.

The `LockManager` allows clients to request locks of two types: `READ` and `WRITE`. These locks are granted based on the following rules:

- Any number of `READ` locks can be granted simultaneously.
- `WRITE` lock is exclusive; no other `READ` or `WRITE` lock can be active at the same time.
- If a lock cannot be granted immediately due to conflicts with existing locks, the request will fail.

Locks have a built-in timeout and will automatically be released after a specified period of time.

## Features

- Two types of locks: **READ** and **WRITE**.
- Management of concurrent requests.
- Timeout functionality for locks to prevent indefinite lock holding.

## Dependencies

This script relies on the following built-in Python libraries:

1. `socket`
2. `threading`
3. `time`
4. `multiprocessing`

It has been developed and tested with Python 3.x. Please make sure you have a compatible Python version before running this script. 

## Usage

Here is a simple way to run the script:

1. Save the script to a file, for example, `lock_manager.py`.
2. Run the script from your terminal or command line:

```bash
python lock_manager.py
This will automatically start the Lock Manager and execute the test cases defined in the test_lock_manager() function.
```
To use the Lock Manager

## How to Use

To use the `LockManager`, you need to start a LockManager server and then use client requests to acquire and release locks.

Here is an example of how to use the `LockManager`:

```python
lock_manager = LockManager("localhost", 8888)
lock_manager.start()
```

# Request a WRITE lock
response = lock_manager.request_lock("resource1", "client1", "WRITE")
print(f"Lock request response: {response}")

# Release the lock
response = lock_manager.release_lock("resource1", "client1")
print(f"Lock release response: {response}")

lock_manager.terminate()

## Testing

The script includes a testing function, `test_lock_manager()`, that you can use to verify the functionality of the `LockManager`. It executes several test scenarios and asserts the expected outcomes. Here is an example of how to run this function:

```python
if __name__ == "__main__":
    test_lock_manager()
```
