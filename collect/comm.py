import curses

EXIT = 0

def curses_up():
  sc = curses.initscr()
  curses.noecho()
  curses.cbreak()
  sc.keypad(1)
  sc.timeout(-1)
  return sc

def curses_down(sc):
  curses.nocbreak()
  sc.keypad(0)
  curses.echo()
  curses.endwin()
