import os
import yaml
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, simpledialog, Text, Scrollbar, Label, Frame
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.constants import *
from datetime import datetime
from pathlib import Path
import threading

from editor_functions import *
from class_NotificationManager import *


class HenryTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Henry")

        # Initialize variables/flags
        self.config = []             # dict for _config.yml
        self.config_path = ""        # location of _config.yml
        self.project_path = ""       # dir for project
        self.current_file_path = ""  # path to currently open file
        self.current_spin = ""       # var for progress meter

        self.modified = False        # is the text area modified?
        self.is_project_open = False # is a project open?
        self.verbose = True          # set verbose mode for troubleshooting
        self._show_statusline_spinner = False

        # Get Bootstrap Themes
        style = ttk.Style()
        self.available_themes = style.theme_names()

        # Application icons
        ICONS = Path(__file__).parent / 'icons'
        self.icons = {
            "menu": ttk.PhotoImage(file=ICONS / 'menu_icon_16.png'),
            "plus": ttk.PhotoImage(file=ICONS / 'plus_icon_16.png')
        }

        # Define the editor font
        self.editor_font = tkfont.Font(family="Courier", size=14)

        # Key Bindings
        self.root.bind_all('<Control-a>',       self._select_all)
        self.root.bind_all('<Control-Shift-n>', self._new_file)
        self.root.bind_all('<Control-Shift-o>', self._open_file)
        self.root.bind_all('<Control-o>',       self._select_project)
        self.root.bind_all('<Control-n>',       self._new_project)
        self.root.bind_all('<Control-s>',       self._save_file)
        self.root.bind_all('<Control-Shift-s>', self._save_file_as)
        #self.root.bind_all('<Control-w>',       self._close_current_file)
        self.root.bind_all('<Control-q>',       self._on_close)
        self.root.bind_all('<Control-z>',       self._undo_action)
        self.root.bind_all('<Control-Shift-z>', self._redo_action)
        self.root.bind_all('<Control-x>',       self._cut_text)
        self.root.bind_all('<Control-c>',       self._copy_text)
        self.root.bind_all('<Control-v>',       self._paste_text)
        # self.root.bind("<Escape>", lambda event: root.attributes("-zoomed", False))
        self.root.bind_all('<Control-plus>',    self._increase_font_size)
        self.root.bind_all('<Control-minus>',   self._decrease_font_size)

        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set the window size to 40% of the screen dimensions
        #window_width = int(screen_width * 0.35)
        window_height = int(screen_height * 0.65)
        window_width = window_height

        # Set the window geometry
        self.root.geometry(f"{window_width}x{window_height}")

        # Create a Button Bar
        self.button_bar = ttk.Frame(self.root)
        self.button_bar.pack(side=tk.TOP, fill=tk.X)

        # --------------- Open Menu ---------------
        self.project_menubutton = ttk.Menubutton(self.button_bar, text="🗃️ Project")#, bootstyle="light-outline")
        self.project_menubutton.pack(side=tk.LEFT)

        self.project_menu = ttk.Menu(self.project_menubutton, tearoff=0)
        self.project_menubutton.config(menu=self.project_menu)

        self.project_menu.add_command(label="📂 Open Project...", command=self._select_project)
        self.project_menu.add_command(label="🗂️ New Project...", command=self._new_project)
        self.project_menu.add_separator()
        self.project_menu.add_command(label="Recent Projects", state=tk.DISABLED)
        self.project_menu.add_separator()
        self.project_menu.add_command(label="📡 Publish...", command=self._publish_project, state="disabled")
        # --------------- Open Menu ---------------

        # --------------- New Post Button ---------------
        self.new_post_button = ttk.Button(self.button_bar, text="➕", image=self.icons['plus'], command=self._new_file, bootstyle="link")
        self.new_post_button.pack(side=tk.LEFT)
        # --------------- New Post Button ---------------

        # --------------- Main Menu ---------------
        self.main_menubutton = ttk.Menubutton(self.button_bar, text="Menu", bootstyle=(SECONDARY))
        self.main_menubutton.pack(side=tk.RIGHT)

        self.main_menu = ttk.Menu(self.main_menubutton, tearoff=0)
        self.main_menubutton.config(menu=self.main_menu)

        ## File Submenu
        self.file_submenu = ttk.Menu(self.main_menu, tearoff=0)
        self.main_menu.add_cascade(label="File", menu=self.file_submenu)
        self.file_submenu.add_command(label="➕ New Post", command=self._new_file, accelerator="Ctrl+n")
        self.file_submenu.add_command(label="📄 Open...", command=self._open_file, accelerator="Ctrl+o")
        self.file_submenu.add_command(label="💾 Save", command=self._save_file, accelerator="Ctrl+s")
        self.file_submenu.add_command(label="Save as...", command=self._save_file_as, accelerator="Ctrl+Shift+s")

        ## Edit Submenu
        self.edit_submenu = ttk.Menu(self.main_menu, tearoff=0)
        self.main_menu.add_cascade(label="Edit", menu=self.edit_submenu)
        self.edit_submenu.add_command(label="Undo", command=self._undo_action)
        self.edit_submenu.add_command(label="Redo", command=self._redo_action)
        self.edit_submenu.add_separator()
        self.edit_submenu.add_command(label="✂️ Cut", command=self._cut_text, accelerator="Ctrl+x")
        self.edit_submenu.add_command(label="📋 Copy", command=self._copy_text, accelerator="Ctrl+c")
        self.edit_submenu.add_command(label="Paste", command=self._paste_text, accelerator="Ctrl+v")
        self.edit_submenu.add_separator()
        self.edit_submenu.add_command(label="Select All", command=self._select_all, accelerator="Ctrl+a")

        ## Insert Submenu
        self.insert_submenu = ttk.Menu(self.main_menu, tearoff=0)
        self.main_menu.add_cascade(label="Insert", menu=self.insert_submenu)
        self.insert_submenu.add_command(label="Date/Time", command=self._insert_datetime, accelerator="Ctrl+Shift+O")
        self.insert_submenu.add_command(label="Image...", command=self._new_file, state="disabled")
        self.insert_submenu.add_command(label="Table...", command=self._new_file, state="disabled")
        self.insert_submenu.add_command(label="Link", command=self._insert_link, accelerator="Ctrl+Shift+l")

        ## Help Submenu
        self.help_submenu = ttk.Menu(self.main_menu, tearoff=0)
        self.main_menu.add_cascade(label="Help", menu=self.help_submenu)
        self.help_submenu.add_command(label="Getting Started", command=self._show_about_dialog, state="disabled", accelerator="F1")
        self.help_submenu.add_separator()
        self.help_submenu.add_command(label="Submit a Bug report...", command=self._show_about_dialog, state="disabled")
        self.help_submenu.add_command(label="Submit Feedback...", command=self._show_about_dialog, state="disabled")
        self.help_submenu.add_command(label="🛟 Contact Support", command=self._show_about_dialog, state="disabled")
        self.help_submenu.add_separator()
        self.help_submenu.add_command(label="About...", command=self._show_about_dialog)

        ## Settings
        self.main_menu.add_separator()
        self.theme_submenu = ttk.Menu(self.main_menu, tearoff=0)
        self.main_menu.add_cascade(label="Theme", menu=self.theme_submenu)
        for theme in self.available_themes:
            title = theme.title()
            self.theme_submenu.add_command(label=title, command=lambda t=title.lower(): self._set_theme(t))

        self.main_menu.add_separator()
        self.main_menu.add_command(label="⚙️ Settings...", command=self._show_about_dialog, state="disabled", accelerator="Ctrl+Alt+s")
        self.main_menu.add_command(label="🪪 Project Properties", command=self._show_info_pane, accelerator="Ctrl+Alt+p")
        self.main_menu.add_separator()
        self.main_menu.add_command(label="Exit", command=self._on_close, accelerator="Ctrl+q")
        # --------------- Main Menu ---------------

        # --------------- Project Info Button ---------------
        self.info_button = ttk.Button(self.button_bar, text="🪪", command=self._show_info_pane, bootstyle="link")
        self.info_button.pack(side=tk.RIGHT)
        # --------------- Project Info Button ---------------
        #######################################################################################

        # Create a Text widget for the main editing area
        self.text_area = ttk.Text(self.root, font=self.editor_font, wrap='word', undo=True)
        self.text_area.pack(fill=tk.BOTH, expand=1)
        self.text_area.bind("<Button-3>", self._show_edit_context) # bind mouse right-click
        self.root.bind("<Button-1>", self._hide_context) # hide context menu when clicking elsewhere
        self.text_area.bind("<Configure>", lambda e: self.notify.restack())

        # Create a Scrollbar and attach it to the Text widget
        self.scrollbar = ttk.Scrollbar(self.text_area)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_area.yview)

        # Create a Status Bar
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_bar_left = ttk.Label(self.status_bar, text=" No Project Loaded")
        self.status_bar_left.pack(side=tk.LEFT)

        self.status_bar_right = ttk.Label(self.status_bar, text="Words: 0 ")
        self.status_bar_right.pack(side=tk.RIGHT)

        # ---------- Notification frame ----------
        self.notify = NotificationManager(self.text_area)
        # -----------------------------------

        # ---------- Project Info Pane frame ----------
        self.info_pane = ttk.Frame(self.root, style='Overlay.TFrame')
        # Position it on the right side of the window
        self.info_pane.place(relx=.97, rely=0.5, anchor='e')

        widget_specs = [
            {"label": "Title:", "command": self._show_info_pane},
            {"label": "Email:", "command": self._show_info_pane},
            {"label": "Description:", "command": self._show_info_pane},
            {"label": "URL:", "command": self._show_info_pane},
            {"label": "Base URL:", "command": self._show_info_pane},
        ]

        _yaml_config_entry_widgets = []
        for widget in widget_specs:
            row = ttk.Frame(self.info_pane)
            row.pack(side=tk.TOP, anchor='n', padx=5, pady=3, fill=tk.X)

            label = ttk.Label(row, text=widget["label"])
            label.pack(side=tk.LEFT, padx=5, pady=(2, 0))

            entry = ttk.Entry(row, width=30)
            entry.pack(side=tk.RIGHT, padx=5, pady=(0, 5), fill=tk.X)
            _yaml_config_entry_widgets.append(entry)

        self.yaml_config = {widget["label"]: entry
                                       for widget, entry in zip(widget_specs,
                                                               _yaml_config_entry_widgets)}

        # how to access later:
        # self.yaml_config["URL:"].delete(0, tk.END)
        # self.yaml_config["URL:"].insert(0, "http://example.com")

        # create bottom button frame
        row = ttk.Frame(self.info_pane)
        row.pack(side=tk.TOP, padx=5, pady=3, fill=tk.X)
        # _config.yml button
        btn = ttk.Button(row, text="_config.yml",
                         command=lambda p=self.config_path: self._open_file(p), bootstyle="light")
        btn.pack(side=tk.LEFT, pady=(0, 5))

        # Close button
        self.info_pane_close_btn = ttk.Button(row, text="Close", command=self._close_info_pane)
        self.info_pane_close_btn.pack(side=tk.RIGHT, pady=(0, 5))

        self.info_pane.lower()  # hide initially
        # -----------------------------------

        # Bind the Text widget to update the status bar
        self.text_area.bind('<KeyRelease>', self._update_word_count)

        # Track changes to the text area
        self.text_area.bind('<KeyPress>', self._on_text_change)

        # Get system/service paths
        self.system_path, self.ruby_path, self.jekyll_path = get_app_paths()
        self._verbose("System Path: " + self.system_path)
        self._verbose("Ruby Path: " + self.ruby_path)
        self._verbose("Jekyll Path: " + self.jekyll_path)

        # Verify Jekyll install
        if not self.jekyll_path:
            response = Messagebox.yesno("An installation of Jekyll was not found on your system. Would you like to install Jekyll now?", title="Install Jekyll")
            if response == "Yes":
                self._update_statusline("Please install Jekyll...")
            elif response == "No" or None:
                exit()

        code, out, err = get_jekyll_version(self.jekyll_path)
        if code == 0:
            jekyll_version = out.split()[1]
            self._update_statusline(self.jekyll_path + " " + jekyll_version)

        # Verify Ruby install
        if not self.ruby_path:
            # notify user Ruby was not found and Publish... will be disabled
            response = Messagebox.ok("An installation of Ruby was not found on your system. You can edit your sites, but you will not be able to use the built-in 'Publish...' feature.",
                title="Ruby Not Found")

        # Handle closing/exiting
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Set initial focus to the text area
        self.text_area.focus_force()

    def _set_theme(self, theme="darkly"):
        self._verbose("Theme: " + theme)
        self.root.style.theme_use(theme.lower())
        # force a redraw of all widgets
        for w in self.root.winfo_children():
            w.update_idletasks()

    def _verbose(self, message):
        """Show a notification for 60 seconds"""
        if self.verbose:
            time_now = datetime.today().strftime('%H:%M:%S')
            message = "🛎️ " + time_now + " " + message
            self.notify.show(message, 60000)

    def _close_info_pane(self):
        """Save project config and hide the info pane."""
        self.info_pane.lower()  # hide the pane
        self.root.title(f"Henry - {self.config['title']}")

        # process and save changes
        self.config['title'] = self.yaml_config["Title:"].get()
        self.config['email'] = self.yaml_config["Email:"].get()
        self.config['description'] = self.yaml_config["Description:"].get()
        self.config['url'] = self.yaml_config["URL:"].get()
        self.config['baseurl'] = self.yaml_config["Base URL:"].get()

        self._save_project_config()  # write _config.yml

    def _show_edit_context(self, event=None):
        # Post the submenu at the mouse position
        self.edit_submenu.post(event.x_root, event.y_root)

    def _hide_context(self, event=None):
        self.edit_submenu.unpost()
        self.info_pane.lower()

    def _increase_font_size(self, event=None):
        """Increment the editor font size by 1 point."""
        current_size = self.editor_font.cget('size')
        new_size = current_size + 1
        self.editor_font.config(size=new_size)

    def _decrease_font_size(self, event=None):
        """Decrement the editor font size by 1 point."""
        current_size = self.editor_font.cget('size')
        new_size = current_size - 1
        self.editor_font.config(size=new_size)

    def _notify(self, text="Hello World!", delay=6000):
        """Show notification of the provided text for the specified time in ms."""
        self.notify.show(message=text, duration=delay)
        self.text_area.focus_force() # returns focus to the main text area

    def _show_info_pane(self):
        """Display the overlay with the current file name."""
        if not self.is_project_open:
            self._notify("No project is open.")
            return

        # Pre‑populate entry with the window title
        self.yaml_config["Title:"].delete(0, tk.END)
        self.yaml_config["Title:"].insert(0, self.config['title'])
        self.yaml_config["Email:"].delete(0, tk.END)
        self.yaml_config["Email:"].insert(0, self.config['email'])
        self.yaml_config["Description:"].delete(0, tk.END)
        self.yaml_config["Description:"].insert(0, self.config['description'])
        self.yaml_config["URL:"].delete(0, tk.END)
        self.yaml_config["URL:"].insert(0, self.config['url'])
        self.yaml_config["Base URL:"].delete(0, tk.END)
        self.yaml_config["Base URL:"].insert(0, self.config['baseurl'])

        self.info_pane.lift()  # bring to front

    def _new_file(self, event=None):
        """Create a new file."""
        post_date = datetime.today().strftime('%Y-%m-%d %H:%M')
        header = f"""---
layout: post
title:  "My New Post"
date:   {post_date}
categories: blog
---  

"""
        self._check_save_before_close()
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, header)

        self.root.title("Henry - New File")
        self.current_file_path = ""
        self.modified = False

    def _open_file(self, file_path="", **kwargs):
        """Open an existing file."""
        self._check_save_before_close()
        print(f"Open Request for: {file_path}")

        if not file_path: # show the file dialog
            if not self.project_path:
                initial_dir = ""
            else:
                initial_dir = self.project_path

            file_path = filedialog.askopenfilename(defaultextension=".md",
                                                   initialdir=initial_dir,
                                                   filetypes=[("Markdown", "*.md *.markdown"),
                                                              ("Text Files", "*.txt"),
                                                              ("HTML", "*.htm *.html"),
                                                              ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)

            self.root.title(f"Henry - {file_path}")
            self.current_file_path = file_path
            self._update_word_count()
            self.modified = False
            self._notify(f"✅ Opened {os.path.basename(file_path)}")
            self._update_statusline(f"✅ Opened {os.path.basename(file_path)}")

    def _save_file_as(self, event=None):
        """Show the file dialog to allow user to save the file with a different path/name."""
        file_path = filedialog.asksaveasfilename(defaultextension=".md",
                                                 initialdir=self.current_file_path,
                                                 filetypes=[("Markdown", "*.md *.markdown"),
                                                            ("Text Files", "*.txt"),
                                                            ("HTML", "*.htm *.html"),
                                                            ("All Files", "*.*")])
        if not file_path:
            self._notify("🚫 Cancelled save file.")
        else:
            self._save_file(file_path=file_path)

    def _save_file(self, event=None, file_path=""):
        """
        Save the file to the path provided. If no path is provided, see if there
        is a file currently open and save that instead.
        """
        print(f"Save Request for: {file_path}")

        if not file_path:
            if not self.current_file_path:
                self._save_file_as()
                return
            else:
                file_path = self.current_file_path

        if not file_path: # double check we have a file path before we save
            self._notify("🚫 Error saving file.\nNo file path provided.")
            return
        else:
            try:
                with open(file_path, 'w') as file:
                    content = self.text_area.get(1.0, tk.END)
                    file.write(content)

                print(f"Saved file: {file_path}")
                self.root.title(f"Henry - {file_path}")
                self.current_file_path = file_path
                self.modified = False
                self._notify(f"✅ Saved {os.path.basename(file_path)}")
            except Exception as e:
                print(e)
                self._notify("Could not save file.")

    def _on_close(self, event=None):
        """Exit the editor."""
        save = self._check_save_before_close()
        if not save == "Cancel":
            self.root.quit()

    def _save_project_config(self):
        """Save the current project configuration back to _config.yml."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.config, f, sort_keys=False, default_flow_style=False)

    def _new_project(self, event=None):
        """Create a new Jekyll site."""
        # get the site name from the user
        site_name = simpledialog.askstring(
            title="Henry - New Project",
            prompt="Please enter the name for your site.",
            parent=self.root
        )
        if site_name:
            self._update_statusline(f"Creating {site_name}...")
        else:
            self._update_statusline("Canceled create new project.")

        # get the folder location from the user
        folder = filedialog.askdirectory()

        create_directory(folder)

        code, out, err = new_jekyll_site(self.jekyll_path, site_name, folder)

        if code == 0:
            self._notify(f"✅ {site_name} created.")
        else:
            self._notify("ERROR!!! Creating project.")

        self._open_project(f"{folder}/{site_name}")

    def _select_project(self, event=None):
        """Opens a file dialog to allow the user to select the root directory of a project."""
        project_path = filedialog.askdirectory()
        if not project_path:
            return
        self._open_project(f"{project_path}/")

    def _open_project(self, project_path):
        """Open an existing Jekyll site."""
        self.config_path = os.path.join(project_path, "_config.yml")
        if not os.path.isfile(self.config_path):
            self._update_statusline("_config.yml not found in the selected folder.  " + project_path)
            return

        with open(self.config_path, "r", encoding="utf-8") as f:
            try:
                self.config = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                self._update_statusline(f"Error parsing config.yml:\n{exc}")
                return

        self.root.title(f"Henry - {self.config['title']}")

        self._update_statusline(project_path)
        self.project_path = project_path

        if self.ruby_path: # Enable Publish... menu item if Ruby is installed
            self.project_menu.entryconfig('📡 Publish...', state='normal')

        self._populate_project_menu()

        self.is_project_open = True
        self._notify(f"✅ Opened {self.config['title']}")

    def _populate_project_menu(self):
        if not self.project_path:
            return

        recent_posts = get_recent_markdown_files(self.project_path + "_posts")
        recent_pages = get_recent_markdown_files(self.project_path + "_pages")
        index_pages = get_recent_markdown_files(self.project_path, recursive=False)
        recent_pages += index_pages # combine the lists of Pages

        # append Posts to the project menu
        self.project_menu.add_separator()
        for file_path in recent_posts[:3]:
            self.project_menu.add_command(
                label=os.path.basename(file_path),
                command=lambda p=file_path: self._open_file(p)
            )

        # self.project_pages_menu.delete(0, tk.END) # delete 4 to tk.END
        self.project_posts_more_menu = ttk.Menu(self.main_menu, tearoff=0)
        self.project_posts_more_menu.add_command(label="➕ New Post", command=self._new_file)
        self.project_posts_more_menu.add_separator()
        for file_path in recent_posts[3:]:
            self.project_posts_more_menu.add_command(
                label=os.path.basename(file_path),
                command=lambda p=file_path: self._open_file(p)
            )
        self.project_menu.add_cascade(label="More...", menu=self.project_posts_more_menu)

        # append Pages to the project menu
        self.project_menu.add_separator()
        for file_path in recent_pages[:3]:
            self.project_menu.add_command(
                label=os.path.basename(file_path),
                command=lambda p=file_path: self._open_file(p)
            )

        self.project_pages_more_menu = ttk.Menu(self.main_menu, tearoff=0)
        self.project_pages_more_menu.add_command(label="➕ New Page", command=self._new_file)
        self.project_pages_more_menu.add_separator()
        for file_path in recent_pages[3:]:
            self.project_pages_more_menu.add_command(
                label=os.path.basename(file_path),
                command=lambda p=file_path: self._open_file(p)
            )
        self.project_menu.add_cascade(label="More...", menu=self.project_pages_more_menu)

    def _publish_project(self):
        destination = filedialog.askdirectory(title="Select build destination")
        if not destination:
            return

        self._show_statusline_spinner = True
        # Start background thread for the build
        project_build_thread = threading.Thread(
            target=self._run_project_build,
            args=(destination,),
            daemon=True
        )
        project_build_thread.start()
        self._run_statusline_spinner()

    def _run_project_build(self, destination):
        code, out, err = build_jekyll_site(self.jekyll_path, self.project_path, destination)

        # When finished, schedule UI update on the main thread
        self.root.after(0, self._build_finished, code, err)

    def _build_finished(self, code, err):
        if code == 0:
            self._notify("✅ Site build completed successfully.")
        else:
            self._notify("🚫 Build failed.\n{err}")

        self._show_statusline_spinner = False
        self._update_statusline(self.project_path)

    def _run_statusline_spinner(self):
        if getattr(self, "_show_statusline_spinner", None) is False or None:
            self.current_spin = ""
            return  # stop the spinner

        self.current_spin += "."
        self._update_statusline(self.current_spin)
        self.root.after(1000, self._run_statusline_spinner) # schedule next tick

    def _undo_action(self, event=None):
        """Undo the last action."""
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass
        self._update_word_count()
        self._on_text_change()

    def _redo_action(self, event=None):
        """Redo the last undone action."""
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass
        self._update_word_count()
        self._on_text_change()

    def _cut_text(self, event=None):
        """Cut selected text."""
        self.text_area.event_generate('<<Cut>>')
        self._update_word_count()
        self._on_text_change()

    def _copy_text(self, event=None):
        """Copy selected text."""
        self.text_area.event_generate('<<Copy>>')

    def _paste_text(self, event=None):
        """Paste text from clipboard."""
        self.text_area.event_generate('<<Paste>>')
        self._update_word_count()
        self._on_text_change()

    def _select_all(self, event=None):
        self.text_area.tag_add('sel', '1.0', 'end-1c')
        self.text_area.mark_set('insert', '1.0')
        self.text_area.see('insert')
        return 'break'

    def _get_highlighted_text(self, event=None):
        return self.text_area.get("sel.first", "sel.last")

    def _insert_text(self, text):
        # Check if a selection exists
        try:
            # Delete the selected text if present
            print(self._get_highlighted_text())
            self.text_area.delete("sel.first", "sel.last")
        except tk.TclError:
            # No selection – nothing to delete
            pass

        self.text_area.insert('insert', text)

    def _insert_datetime(self):
        time_now = datetime.today().strftime('%Y-%m-%d %H:%M')
        self._insert_text(time_now)

    def _insert_link(self):
        link_text = (self._get_highlighted_text())
        if not link_text:
            self._insert_text("[link](url)")
        else:
            self._insert_text("[" + link_text + "](url)")
            # highlight 'url' after insert

        # 1. Search for the whole link pattern
        link_start = self.text_area.search(r'\[.*?\]\(url\)', '1.0', stopindex=tk.END, regexp=True)
        if not link_start:
            return  # no link found

        # 2. Find the positions of '(' and ')' inside that link
        open_paren = self.text_area.search(r'\(', link_start, stopindex='end', regexp=True)
        close_paren = self.text_area.search(r'\)', open_paren, stopindex='end', regexp=True)
        if not (open_paren and close_paren):
            return

        # 3. Compute the range that contains the URL (between the parentheses)
        url_start = f"{open_paren}+1c"  # one character after '('
        url_end = close_paren  # position of ')'

        # 4. Select the text of the range found
        self.text_area.tag_add("sel", url_start, url_end)
        self.text_area.mark_set('insert', url_start)
        self.text_area.see('insert')

    @staticmethod
    def _show_about_dialog():
        """Show the about dialog."""
        Messagebox.show_info("Henry\n\nA simple editor for Jekyll.", title="About Henry")

    def _update_word_count(self, event=None):
        """Update the status bar with the current word count."""
        content = self.text_area.get(1.0, tk.END)
        word_count = count_words_outside_header(content)
        self.status_bar_right.config(text=f"Words: {word_count} ")

    def _update_statusline(self, text):
        self.status_bar_left.config(text=" " + text)

    def _on_text_change(self, event=None):
        """Track changes to the text area."""
        self.modified = True
        current_title = self.root.title().replace("• ", "")
        self.root.title(f"• {current_title}")

    def _check_save_before_close(self, event=None):
        """Check for unsaved changes."""
        if self.modified:
            response = Messagebox.yesnocancel("Do you want to save your changes?", title="Unsaved Changes")
            if response == "Yes":
                self._save_file()
                return response
            elif response == "No":
                return response
            elif response == "Cancel" or None:
                return "Cancel"
