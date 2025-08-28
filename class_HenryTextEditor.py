import yaml
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, simpledialog, Text, Scrollbar, Label, Frame
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
#from ttkbootstrap.constants import *
#import glob

from editor_functions import *


class HenryTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Henry")

        # Initialize variables/flags
        self.config = []             # dict for _config.yml
        self.config_path = ""        # location of _config.yml
        self.project_path = ""       # dir for project

        self.modified = False        # is the text area modified?
        self.is_project_open = False # is a project open?

        # Define the editor font
        self.editor_font = tkfont.Font(family="Courier", size=12)

        # Key Bindings
        self.root.bind_all('<Control-a>', self._select_all)
        self.root.bind_all('<Control-n>', self._new_file)
        self.root.bind_all('<Control-o>', self._open_file)
        self.root.bind_all('<Control-s>', self._save_file)
        # self.root.bind_all("<Control-Shift-S>", saveas_com)
        # self.root.bind_all('<Control-w>', close_com)
        self.root.bind_all('<Control-q>', self._on_close)
        # self.root.bind_all('<Control-d>', default_view)
        # self.root.bind_all('<F11>', full_screen)
        # self.root.bind("<Escape>", lambda event: root.attributes("-zoomed", False))
        self.root.bind_all('<Control-plus>', self._increase_font_size)
        self.root.bind_all('<Control-minus>', self._decrease_font_size)

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
        self.project_menubutton = ttk.Menubutton(self.button_bar, text="Project", bootstyle="light")
        self.project_menubutton.pack(side=tk.LEFT)

        self.project_menu = ttk.Menu(self.project_menubutton, tearoff=0)
        self.project_menubutton.config(menu=self.project_menu)

        self.project_menu.add_command(label="Open Project...", command=self._select_project)
        self.project_menu.add_command(label="New Project...", command=self._new_project)
        self.project_menu.add_separator()
        self.project_menu.add_command(label="Publish...", command=self._publish_project, state="disabled")
        # --------------- Open Menu ---------------

        # --------------- New Post Button ---------------
        self.new_post_button = ttk.Button(self.button_bar, text="➕", command=self._new_file, bootstyle="link")
        self.new_post_button.pack(side=tk.LEFT)
        # --------------- New Post Button ---------------

        # --------------- Main Menu ---------------
        self.main_menubutton = ttk.Menubutton(self.button_bar, text="===")
        self.main_menubutton.pack(side=tk.RIGHT)

        self.main_menu = ttk.Menu(self.main_menubutton, tearoff=0)
        self.main_menubutton.config(menu=self.main_menu)

        ## File Submenu
        self.file_submenu = ttk.Menu(self.main_menu, tearoff=0)
        self.main_menu.add_cascade(label="File", menu=self.file_submenu)
        self.file_submenu.add_command(label="New Project...", command=self._new_file, state="disabled")
        self.file_submenu.add_command(label="📂 Open Project...", command=self._new_file, state="disabled")
        self.file_submenu.add_separator()
        self.file_submenu.add_command(label="➕ New Post", command=self._new_file)
        self.file_submenu.add_command(label="Open...", command=self._open_file)
        self.file_submenu.add_command(label="💾 Save", command=self._save_file)
        self.file_submenu.add_command(label="Save as...", command=self._save_file, state="disabled")

        ## Edit Submenu
        self.edit_submenu = ttk.Menu(self.main_menu, tearoff=0)
        self.main_menu.add_cascade(label="Edit", menu=self.edit_submenu)
        self.edit_submenu.add_command(label="Undo", command=self._undo_action)
        self.edit_submenu.add_command(label="Redo", command=self._redo_action)
        self.edit_submenu.add_separator()
        self.edit_submenu.add_command(label="✂️ Cut", command=self._cut_text)
        self.edit_submenu.add_command(label="Copy", command=self._copy_text)
        self.edit_submenu.add_command(label="Paste", command=self._paste_text)
        self.edit_submenu.add_separator()
        self.edit_submenu.add_command(label="Select All", command=self._select_all)

        ## Insert Submenu
        self.insert_submenu = ttk.Menu(self.main_menu, tearoff=0)
        self.main_menu.add_cascade(label="Insert", menu=self.insert_submenu)
        self.insert_submenu.add_command(label="Date/Time", command=self._new_file, state="disabled")
        self.insert_submenu.add_command(label="Image...", command=self._new_file, state="disabled")
        self.insert_submenu.add_command(label="Table...", command=self._new_file, state="disabled")
        self.insert_submenu.add_command(label="Link", command=self._new_file, state="disabled")

        ## Help Submenu
        self.help_submenu = ttk.Menu(self.main_menu, tearoff=0)
        self.main_menu.add_cascade(label="Help", menu=self.help_submenu)
        self.help_submenu.add_command(label="Getting Started", command=self._show_about_dialog, state="disabled")
        self.help_submenu.add_separator()
        self.help_submenu.add_command(label="Submit a Bug report...", command=self._show_about_dialog, state="disabled")
        self.help_submenu.add_command(label="Submit Feedback...", command=self._show_about_dialog, state="disabled")
        self.help_submenu.add_command(label="🛟 Contact Support", command=self._show_about_dialog, state="disabled")
        self.help_submenu.add_separator()
        self.help_submenu.add_command(label="About...", command=self._show_about_dialog)

        ## Settings
        self.main_menu.add_separator()
        self.main_menu.add_command(label="⚙️ Settings...", command=self._show_about_dialog, state="disabled")
        self.main_menu.add_command(label="🪪 Project Properties", command=self._show_info_pane)
        self.main_menu.add_separator()
        self.main_menu.add_command(label="Exit", command=self._on_close)
        # --------------- Main Menu ---------------

        # --------------- Project Info Button ---------------
        self.info_button = ttk.Button(self.button_bar, text="🪪", command=self._show_info_pane, bootstyle="link")
        self.info_button.pack(side=tk.RIGHT)
        # --------------- Project Info Button ---------------
        #######################################################################################

        # Create a Text widget for the main editing area
        self.text_area = ttk.Text(self.root, font=self.editor_font, wrap='word', undo=True)
        self.text_area.pack(fill=tk.BOTH, expand=1)

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

        # ---------- Overlay frame ----------
        self.overlay = ttk.Frame(self.root, style='Overlay.TFrame')
        self.overlay.place(relx=0.5, rely=0.5, anchor='center')  # center over text_area
        self.overlay_label = ttk.Label(self.overlay, text="", padding=5)
        self.overlay_label.pack()
        self.overlay.lower()  # hide initially
        # -----------------------------------

        # ---------- Project Info Pane frame ----------
        self.info_pane = ttk.Frame(self.root, style='Overlay.TFrame')
        # Position it on the right side of the window
        self.info_pane.place(relx=.97, rely=0.5, anchor='e')

        # Entry for the title
        lbl = ttk.Label(self.info_pane, text="Title:")
        lbl.pack(anchor='w', padx=5, pady=(2, 0))
        self.info_pane_title = ttk.Entry(self.info_pane, width=30)
        self.info_pane_title.pack(padx=5, pady=(0,5), fill='x')

        # _config.yml button
        btn = ttk.Button(self.info_pane, text="_config.yml", command=self._open_file, bootstyle="light")
        btn.pack(pady=(0, 5))

        # Close button
        self.info_pane_close_btn = ttk.Button(self.info_pane, text="Close", command=self._close_info_pane)
        self.info_pane_close_btn.pack(anchor='w', pady=(0, 5))

        self.info_pane.lower()  # hide initially
        # -----------------------------------

        # Bind the Text widget to update the status bar
        self.text_area.bind('<KeyRelease>', self._update_status_bar)

        # Track changes to the text area
        self.text_area.bind('<KeyPress>', self._on_text_change)

        # Get system/service paths
        self.system_path, self.gem_path, self.jekyll_path = get_app_paths()

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

        # Verify Gem install
        if not self.gem_path:
            response = Messagebox.ok("An installation of Gem was not found on your system. You can edit your sites, but you will not be able to use the built-in Publish feature.",
                title="Gem Not Found")
            # disable Publish... menu item

        # Handle closing/exiting
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _close_info_pane(self):
        """Save project config and hide the info pane."""
        self.info_pane.lower()  # hide the pane

        self.config['title'] = self.info_pane_title.get()
        self.root.title(f"Henry - {self.config['title']}")

        self._save_project_config()  # write _config.yml

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

    def _show_overlay(self, text="Hello World!"):
        """Display the overlay with the provided text."""
        self.overlay_label.config(text=text)
        self.overlay.lift()  # bring to front
        # hide after a short delay (optional)
        self.root.after(6000, self.overlay.lower)

    def _show_info_pane(self):
        """Display the overlay with the current file name."""
        if not self.is_project_open:
            self._show_overlay("No project is open.")
            return

        # Pre‑populate entry with the window title
        self.info_pane_title.delete(0, tk.END)
        self.info_pane_title.insert(0, self.config['title'])
        self.info_pane.lift()  # bring to front

    def _new_file(self):
        """Create a new file."""
        header = """---
layout: post
title:  "My New Post"
date:   2025-08-22 09:41:47 -1000
categories: blog
---  

"""
        self._check_save_before_close()
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, header)

        self.root.title("Henry - New File")
        self.modified = False

    def _open_file(self):
        """Open an existing file."""
        self._check_save_before_close()
        file_path = filedialog.askopenfilename(defaultextension=".md",
                                               filetypes=[("Markdown", "*.md"),
                                                          ("Text Files", "*.txt"),
                                                          ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
                self.root.title(f"Henry - {file_path}")
                self._update_status_bar()
                self.modified = False

    def _save_file(self):
        """Save the current file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".md",
                                                 filetypes=[("Markdown", "*.md"),
                                                            ("Text Files", "*.txt"),
                                                            ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                content = self.text_area.get(1.0, tk.END)
                file.write(content)
                self.root.title(f"Henry - {file_path}")
                self.modified = False

    def _on_close(self):
        """Exit the editor."""
        save = self._check_save_before_close()
        if not save == "Cancel":
            self.root.quit()

    def _save_project_config(self):
        """Save the current project configuration back to _config.yml."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.config, f, sort_keys=False, default_flow_style=False)

    def _new_project(self):
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
            self._show_overlay(f"{site_name} created.")
        else:
            self._show_overlay("ERROR!!! Creating project.")

        self._open_project(f"{folder}/{site_name}")

    def _select_project(self):
        project_path = filedialog.askdirectory()
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
                self._update_statusline(f"Error parsing config.yml: {exc}")
                return

        self.root.title(f"Henry - {self.config['title']}")

        self._update_statusline(project_path)
        self.project_path = project_path

        if self.gem_path(): # Enable Publish... menu item if Gem is installed
            self.project_menu.entryconfig('Publish...', state='normal')

        self.is_project_open = True

    def _publish_project(self):
        destination = filedialog.askdirectory(title="Select build destination")
        code, out, err = build_jekyll_site(self.jekyll_path, self.project_path, destination)

        if code == 0:
            self._show_overlay("✅ Site build completed successfully.")
        else:
            self._show_overlay("ERROR!!! Build failed.")
            print(err)

    def _undo_action(self):
        """Undo the last action."""
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass
        self._update_status_bar()
        self._on_text_change()

    def _redo_action(self):
        """Redo the last undone action."""
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass
        self._update_status_bar()
        self._on_text_change()

    def _cut_text(self):
        """Cut selected text."""
        self.text_area.event_generate('<<Cut>>')
        self._update_status_bar()
        self._on_text_change()

    def _copy_text(self):
        """Copy selected text."""
        self.text_area.event_generate('<<Copy>>')

    def _paste_text(self):
        """Paste text from clipboard."""
        self.text_area.event_generate('<<Paste>>')
        self._update_status_bar()
        self._on_text_change()

    def _select_all(self, event=None):
        self.text_area.tag_add('sel', '1.0', 'end-1c')
        self.text_area.mark_set('insert', '1.0')
        self.text_area.see('insert')
        return 'break'

    @staticmethod
    def _show_about_dialog():
        """Show the about dialog."""
        Messagebox.show_info("Henry\n\nA simple editor for Jekyll.", title="About Henry")

    def _update_status_bar(self, event=None):
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
