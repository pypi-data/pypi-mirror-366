# Pocketwatch

Pocketwatch provides a simple stopwatch for timing any block of Python code. It
can display desktop notifications, play a chime after long runs, and optionally
collect profiling statistics.

## Installation

```bash
pip install pocketwatch
```

## Basic Usage

```python
from pocketwatch import Pocketwatch

with Pocketwatch("load data"):
    load_data()
```

The context manager prints the elapsed time when the block finishes. Pass a
`logging.Logger` if you also want the output sent to a log. Notifications and
sound are disabled unless explicitly requested.

```python
with Pocketwatch(
    "big task",
    notify=True,          # show a pop-up
    notify_after=5.0,     # minimum duration before popup
    sound=True,           # play ding.wav
    sound_after=60.0,     # minimum duration for sound
):
    run_big_task()
```

You can capture intermediate checkpoints using `mark()` (or its alias
`log()`):

```python
with Pocketwatch("steps") as pw:
    load()
    pw.mark("loaded data")
    transform()
    pw.log("transformed")
```

To enable cProfile integration, pass `profile=True`.  By default the raw stats
are written to `profile_output.prof`; set `profile_output_path=None` to skip
writing the file.  Call `end(return_stats=True)` to retrieve a
`pstats.Stats` instance.

```python
with Pocketwatch(profile=True) as pw:
    crunch_numbers()
stats = pw.end(return_stats=True)
```

## Decorator Shortcut

A lightweight decorator mirrors the context manager. It uses the function name
as the message label and prints the elapsed time. Provide a logger argument to
forward output to your own logging setup.

```python
from pocketwatch.decorators import stopwatch

@stopwatch
def do_work():
    ...
```

Custom options may be supplied when decorating:

```python
@stopwatch(sound=True, notify=False)
def background_job():
    ...
```

## Features

- Drop-in context manager for timing code blocks
- Desktop notifications via [notifypy](https://pypi.org/project/notifypy/)
- Optional sound playback with bundled audio files
- Incremental mode to suppress output for short runs
- Optional logging to a custom logger
- Checkpointing with `mark()` or `log()`
- cProfile support with stats returned on request
- Works with Python 3.9+
- Licensed under the MIT license

