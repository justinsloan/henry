import tkinter as tk
import ttkbootstrap as ttk

# Usage inside the editor class
# self.notification_manager = NotificationManager(self.text_area)
# self.notification_manager.show("File saved successfully")
# self.notification_manager.show("File saved successfully", 3000) #show notification for 3 seconds
# self.notification_manager.show("File saved successfully", -1) #show notification indefinitely until manually closed


class NotificationManager:
    """Show transient messages in the bottom‑right corner of the specified widget."""

    def __init__(self, entry_widget):
        self.entry_widget = entry_widget
        self.notifications = []  # list of active frames

    def show(self, message, duration="6000"):
        """Create a notification that auto‑closes after duration ms."""
        # Create container
        frame = ttk.Frame(self.entry_widget, style="Notif.TFrame")
        frame.configure(style="Notif.TFrame")
        # Label
        lbl = ttk.Label(frame, text=message)
        lbl.pack(side=tk.LEFT, padx=5, pady=2)
        # Close button
        btn = ttk.Button(frame, text="✕", width=2,
                         command=lambda: self._dismiss(frame))
        btn.pack(side=tk.RIGHT, padx=2)

        # Position: bottom‑right of the text widget
        self.entry_widget.update_idletasks()
        x = self.entry_widget.winfo_width() - frame.winfo_reqwidth() - 30
        y = self.entry_widget.winfo_height() - frame.winfo_reqheight() - 15
        # Stack above previous notifications
        for n in self.notifications:
            y -= n.winfo_reqheight() + 5
        frame.place(in_=self.entry_widget, x=x, y=y)

        self.notifications.append(frame) # show the notification

        # Auto‑close if duration not null
        if int(duration) > 0:
            frame.after(duration, lambda: self._dismiss(frame))

    def _dismiss(self, frame):
        if frame in self.notifications:
            frame.destroy()
            self.notifications.remove(frame)
            # Re‑stack remaining notifications
            self._reposition()

    def _reposition(self):
        y = self.entry_widget.winfo_height() - 10
        for n in reversed(self.notifications):
            y -= n.winfo_reqheight() + 5
            n.place_configure(y=y)

