#!/usr/bin/env python3
__version__ = "Dev.1"
__author__ = "Justin Sloan"

from class_HenryTextEditor import *

def main():
    root = ttk.Window(themename="darkly")
    editor = HenryTextEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()