#!/usr/bin/env python3
__version__ = "0"
__author__ = "Justin Sloan"

from class_HenryTextEditor import *

def main():
    root = ttk.Window(themename="sandstone") #pulse #vapor #flatly #darkly #sandstone
    editor = HenryTextEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
