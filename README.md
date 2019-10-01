This is a procedural cave generator.  It turned out to work suprisingly well given its very simple implementation.
To run just type in `python cave_maker.py CAVE_HEIGHT CAVE_LENGTH MIN_CAVE_GAP`. e.g. `python cave_maker.py 50 230 10`

If you get an error try changing your input arguments so that the output can fit into your terminal window.

hit CTRL+c to stop at any time

note, this depends on curses (python wrapper for ncurses) and has limited support for Microsoft Windows.
