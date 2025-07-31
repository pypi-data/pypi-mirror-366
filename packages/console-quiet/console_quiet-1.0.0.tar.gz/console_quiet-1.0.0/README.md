# console_quiet

Provides a context manager for doing a "deep suppression" of stdout and stderr.

## Usage

Use thusly:

	from console_quiet import ConsoleQuiet
	with ConsoleQuiet():
		... do something noisy ...

That's all folks!
