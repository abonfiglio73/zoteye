import tkinter as tk


class CustomMenuButton(tk.Menubutton):

    opened_menu = None
    opened_instance = None

    def __init__(
        self,
        master,
        text,
        options,
        variable=None,
        bg="#292929",
        fg="#fafafa",
        active_bg="#595959",
        active_fg="#ffffff",
        hover_bg="#57c8ff",
        border_color="#1c1c1c",
        font=None,
        **kwargs,
    ):
        super().__init__(
            master,
            text=text,
            bg=bg,
            fg=fg,
            font=font,
            cursor="hand2",
            activebackground=active_bg,
            activeforeground=active_fg,
            **kwargs,
        )
        self.bg = bg
        self.fg = fg
        self.active_bg = active_bg
        self.active_fg = active_fg
        self.hover_bg = hover_bg
        self.border_color = border_color
        self.variable = variable
        self.options = options
        self.menu = None

        # Toggle the popup menu on left-click
        self.bind("<Button-1>", self.show_menu)

    def show_menu(self, event):
        # Close a different instance's open menu, if any
        if CustomMenuButton.opened_menu and CustomMenuButton.opened_instance != self:
            CustomMenuButton.opened_menu.destroy()
            CustomMenuButton.opened_menu = None
            CustomMenuButton.opened_instance = None

        # If this menu is already open, close it (toggle behavior)
        if self.menu:
            self.menu.destroy()
            self.menu = None
            CustomMenuButton.opened_menu = None
            CustomMenuButton.opened_instance = None
            return

        self.menu = tk.Toplevel(self)
        self.menu.overrideredirect(True)  # Borderless popup
        self.menu.config(bg=self.border_color)

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.menu.geometry(f"+{x}+{y}")

        frame = tk.Frame(self.menu, bg=self.bg)
        frame.pack(padx=1, pady=1, fill="both")

        for label, value, cmd in self.options:
            # Separator row
            if value is None:
                sep = tk.Frame(frame, bg=self.border_color, height=1)
                sep.pack(fill="x", pady=4)
                continue

            # Regular menu item with optional checkmark
            check = "✓ " if (self.variable and self.variable.get() == value) else "   "
            btn = tk.Label(
                frame,
                text=f"{check}{label}",
                bg=self.bg,
                fg=self.fg,
                font=self["font"],
                anchor="w",
                padx=10,
                pady=3,
            )
            btn.pack(fill="x")

            # Hover effects for items
            btn.bind(
                "<Enter>",
                lambda e, b=btn: b.config(bg=self.hover_bg, fg=self.active_fg),
            )
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.bg, fg=self.fg))

            # Select the option and invoke its command
            btn.bind("<Button-1>", lambda e, v=value, c=cmd: self.select_option(v, c))

        CustomMenuButton.opened_menu = self.menu
        CustomMenuButton.opened_instance = self

        self.menu.bind("<FocusOut>", lambda e: self.close_menu())
        self.menu.focus_set()

    def close_menu(self):
        if self.menu:
            self.menu.destroy()
            self.menu = None
            CustomMenuButton.opened_menu = None
            CustomMenuButton.opened_instance = None

    def select_option(self, value, command):
        if self.variable:
            self.variable.set(value)
        if callable(command):
            command()
        self.close_menu()

    def refresh_style(self):
        self.config(
            bg=self.bg,
            fg=self.fg,
            activebackground=self.active_bg,
            activeforeground=self.active_fg,
        )
