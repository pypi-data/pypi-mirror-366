# log_soso

Some logging enhancements, such as log error with traceback, redirect STDOUT, STDERR to log, and more.

## Functions

### log_error

Log an error with traceback:

### log_stdout

Redirect STDOUT to log

### log_stderr

Redirect STDOUT to log

## Classes

### StreamToLogger

File-like stream object that redirects writes to a logger instance.
Use like:

	with StreamToLogger(logging.getLogger(), logging.DEBUG) as sob:
		pprint(object, stream=sob)

### PrintPassthru

A context manager which temporarily directs loggin output to real stdout.

