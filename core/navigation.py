from __future__ import annotations

import tkinter as tk

from config import theme


class NavButton(tk.Label):
    def __init__(self, parent, text: str, command, *args, **kwargs):
        super().__init__(
            parent,
            text=text,
            bg=theme.SIDEBAR_BG,
            fg='white',
            anchor='w',
            padx=18,
            pady=12,
            font=theme.BODY_FONT,
            cursor='hand2',
            *args,
            **kwargs,
        )
        self.command = command
        self.active = False
        self.bind('<Button-1>', lambda e: self.command())
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _on_enter(self, _event=None):
        if not self.active:
            self.configure(bg=theme.SIDEBAR_HOVER)

    def _on_leave(self, _event=None):
        if not self.active:
            self.configure(bg=theme.SIDEBAR_BG)

    def set_active(self, active: bool):
        self.active = active
        self.configure(bg=theme.SIDEBAR_ACTIVE if active else theme.SIDEBAR_BG)
