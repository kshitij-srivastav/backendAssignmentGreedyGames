# README

This Flask application provides a key-value store with support for operations such as setting values, getting values, pushing and popping values from a queue.

## Endpoints

### GET /qpop

This endpoint pops a value from the queue at the given key.

#### Parameters

key (required): The key of the queue to pop a value from.
Returns

result: The value that was popped from the queue.
error: An error message if the operation was unsuccessful.

### GET /bqpop

This endpoint blocks until a value is available to pop from the queue at the given key, or until the specified timeout has elapsed.

#### Parameters

key (required): The key of the queue to pop a value from.
timeout (optional): The maximum amount of time to block, in seconds. Defaults to 0 (no timeout).
Returns
result: The value that was popped from the queue.
error: An error message if the operation was unsuccessful.

### POST /set

This endpoint sets a value for the given key.

#### Parameters

key (required): The key to set the value for.
value (required): The value to set.
expiry (optional): The expiration time for the key-value pair, in seconds.  
condition (optional): The condition for the set operation. Possible values are "NX" (set the value only if the key does not already exist) and "XX" (set the value only if the key already exists).
Returns
success: Whether the operation was successful.
message: A message indicating the result of the operation.

### GET /get

This endpoint retrieves the value for the given key.

#### Parameters

key (required): The key to retrieve the value for.
Returns
result: The value for the given key.
error: An error message if the operation was unsuccessful.

### POST /qpush

This endpoint pushes one or more values to the queue at the given key.

#### Parameters

key (required): The key of the queue to push values to.
values (required): A list of values to push to the queue.
Returns
result: The new length of the queue.
error: An error message if the operation was unsuccessful.
Functions
key_valid
Checks whether the given key exists in the store and is not expired.

### set_value

Sets the given value for the given key in the store, optionally with an expiration time and a condition for the operation.

### get_value

Retrieves the value for the given key from the store.

### push_value

Pushes one or more values to the queue at the given key in the store.

### pop_value

Pops a value from the queue at the given key in the store.

### blocking_pop_value

Blocks until a value is available to pop from the queue at the given key in the store, or until the specified timeout has elapsed.
