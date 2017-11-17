import curses
import logging

import threading

try:
    unicode
    _unicode = True
except NameError:
    _unicode = False

from jwoanda.baseinterface import BaseInterface
            
class CursesHandler(logging.Handler):
    def __init__(self, screen):
        logging.Handler.__init__(self)
        self.screen = screen

    def emit(self, record):
        try:
            msg = self.format(record)
            screen = self.screen
            fs = "\n%s"
            if not _unicode: #if no unicode support...
                screen.addstr(fs % msg)
                screen.refresh()
            else:
                try:
                    if (isinstance(msg, unicode) ):
                        ufs = u'\n%s'
                        try:
                            screen.addstr(ufs % msg)
                            screen.refresh()
                        except UnicodeEncodeError:
                            screen.addstr((ufs % msg).encode(code))
                            screen.refresh()
                    else:
                        screen.addstr(fs % msg)
                        screen.refresh()
                except UnicodeError:
                    screen.addstr(fs % msg.encode("UTF-8"))
                    screen.refresh()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


# class CursesHandler(logging.Handler):
#     def __init__(self, screen):
#         logging.Handler.__init__(self)
#         self.screen = screen

#         curses.start_color()
#         curses.use_default_colors()
#         for i in range(0, curses.COLORS):
#             curses.init_pair(i + 1, i, -1)

#     def emit(self, record):
#         msg = self.format(record)
#         screen = self.screen
#         ufs = u'\n%s'
#         screen.addstr(ufs % msg, 83)
#         screen.refresh()


class CursesInterface(threading.Thread, BaseInterface):

    def __init__(self, instruments):
        super(CursesInterface, self).__init__()
        self.instruments = instruments

        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()

        self.stdscr.keypad(1)

    def run(self):
        maxy, maxx = stdscr.getmaxyx()
    
        height = maxy//2
        width = 30
        
        # height, width, begin_y, begin_x
        self.instrwindow = curses.newwin(height, width, 0, 0)
        self.instrwindow.border()

        logwindow = curses.newwin(height, maxx - width - 1, 0, width+1)
        logwindow.border()

        self.ipythonwindow = curses.newwin(height, maxx, height, 0)
        self.ipythonwindow.border()

        self.instrwindow.addstr(0, 0, 'instrwindow')
    
        self.instruments = instruments
        for instrument in self.instruments:
            self.setbidask(instrument, 0., 0.)

    
        self.instrwindow.refresh()
    
        logwindow.addstr(0, 0, 'logwindow')
        logwindow.refresh()
        
        logwindow.refresh()
        logwindow.scrollok(True)
        logwindow.idlok(True)
        
        self.ipythonwindow.addstr(0, 0, 'ipythonwindow')
        self.ipythonwindow.refresh()
        
        #    curses.setsyx(-1, -1)
        
        #    stdscr.addstr(0,0,'dafdsafdafas')
        #    stdscr.refresh()
        #panel.refresh()
        #stdscr.refresh()
        #window.scrollok(True)
        #window.idlok(True)
        #window.leaveok(True)
        
        terminal_handler = CursesHandler(logwindow)
        logging.getLogger().addHandler(terminal_handler)

        self.kill = False
        while not self.kill:
            c = self.ipythonwindow.getch()
            if c == ord('p'):
                pass #PrintDocument()
            elif c == ord('q'):
                break  # Exit the while loop
            elif c == curses.KEY_HOME:
                x = y = 0

    def setbidask(self, instrument, bid, ask):
        try:
            idx = self.instruments.index(instrument)
            self.instrwindow.addstr(idx+1, 1, "%s %3.5f %3.5f" % (instrument, bid, ask))
        except:
            pass
            
    def disconnect(self):
        self.kill = True
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(0)
        curses.endwin()
        

# def main(stdscr):
#     # Clear stdscr
#     #    stdscr.clear()

#     ci = CursesInterface(stdscr)

#     ci.start()
    
#     for i in range(0, 100):
#         logging.error("fuck you")
#         logging.warning("go to hell")
        
#     ci.join()
    

# curses.wrapper(main)
