from datetime import timedelta
import curses, time
from multiprocessing.connection import Connection

import communication as coms

def runDisplay(stdscr, cmdPipe:Connection):
  # Setup curses
  curses.cbreak()  # Disable line buffering
  stdscr.keypad(True)  # Enable special key handling
  stdscr.timeout(-1)  # Set a timeout for `getch` to avoid blocking
  starttime = time.process_time()

  while True:
    # Check if key is pressed
    key = stdscr.getch()
    if key == 27:  # Escape key (ASCII 27) to quit
      cmdPipe.send(coms.CommandSignal.EXIT)
      break
    # Update timer on display
    stdscr.addstr(
      1, 0,
      f"Time elapsed: {str(timedelta(seconds=time.process_time()-starttime))}"
    )
    stdscr.refresh()

  cmdPipe.close()

def displayProcess(cmdPipe:Connection):
  curses.wrapper(runDisplay, cmdPipe)