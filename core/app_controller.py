from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from config import settings, theme
from core.navigation import NavButton
from database.db import DatabaseError
from gui.analysis_page import AnalysisPage
from gui.crops_page import CropsPage
from gui.dashboard_page import DashboardPage
from gui.farmer_page import FarmerPage
from gui.history_page import HistoryPage
from gui.login_page import LoginPage


class AppController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(settings.APP_TITLE)
        self.geometry(settings.APP_GEOMETRY)
        self.minsize(*settings.APP_MIN_SIZE)
        self.configure(bg=theme.BG_APP)
        self.current_user = None
        self.status_var = tk.StringVar(value='Ready')
        self.frames = {}
        self.nav_buttons = {}
        self._configure_ttk()
        self.show_login()

    def _configure_ttk(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        style.configure('Treeview', rowheight=28, font=theme.BODY_FONT, fieldbackground='white', background='white')
        style.configure('Treeview.Heading', font=(theme.FONT_FAMILY, 10, 'bold'))
        style.map('Treeview', background=[('selected', '#d8f3dc')], foreground=[('selected', theme.TEXT)])
        style.configure('TCombobox', padding=4)
        style.configure('TProgressbar', thickness=16)

    def show_login(self):
        for child in self.winfo_children():
            child.destroy()
        self.frames.clear()
        LoginPage(self, self).pack(fill='both', expand=True)

    def login_success(self, user_record: dict):
        self.current_user = user_record
        self._build_shell()
        self.show_page('DashboardPage')
        self.set_status(f"Logged in as {user_record.get('full_name') or user_record.get('username')}")

    def _build_shell(self):
        for child in self.winfo_children():
            child.destroy()

        shell = tk.Frame(self, bg=theme.BG_APP)
        shell.pack(fill='both', expand=True)

        sidebar = tk.Frame(shell, bg=theme.SIDEBAR_BG, width=240)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=theme.SIDEBAR_BG)
        brand.pack(fill='x', padx=18, pady=(18, 14))
        tk.Label(brand, text='Crop Health', bg=theme.SIDEBAR_BG, fg='white', font=(theme.FONT_FAMILY, 20, 'bold')).pack(anchor='w')
        tk.Label(brand, text='Industry-ready farming dashboard', bg=theme.SIDEBAR_BG, fg='#cdebd8', font=theme.SMALL_FONT).pack(anchor='w', pady=(2, 0))

        self.nav_buttons = {}
        for label, page_name in settings.SIDEBAR_ITEMS:
            btn = NavButton(sidebar, text=label, command=lambda p=page_name: self.show_page(p))
            btn.pack(fill='x', padx=10, pady=2)
            self.nav_buttons[page_name] = btn

        tk.Frame(sidebar, bg='#3c7a5e', height=1).pack(fill='x', padx=18, pady=14)
        tk.Label(sidebar, text='Innovation Features', bg=theme.SIDEBAR_BG, fg='#cdebd8', font=(theme.FONT_FAMILY, 10, 'bold')).pack(anchor='w', padx=18)
        for line in ['• Health score engine', '• Smart crop advice', '• CSV/PDF export', '• Live dashboard analytics']:
            tk.Label(sidebar, text=line, bg=theme.SIDEBAR_BG, fg='white', font=theme.SMALL_FONT).pack(anchor='w', padx=18, pady=2)

        tk.Button(sidebar, text='Logout', bg=theme.DANGER, fg='white', font=theme.BUTTON_FONT, relief='flat', cursor='hand2', command=self.logout).pack(side='bottom', fill='x', padx=18, pady=18)

        right = tk.Frame(shell, bg=theme.BG_APP)
        right.pack(side='left', fill='both', expand=True)

        header = tk.Frame(right, bg=theme.CARD_BG, highlightbackground=theme.BORDER, highlightthickness=1)
        header.pack(fill='x', padx=16, pady=(16, 10))
        tk.Label(header, text='Crop Health Analyzer – Image-Based Farming Solution', bg=theme.CARD_BG, fg=theme.TEXT, font=(theme.FONT_FAMILY, 17, 'bold')).pack(side='left', padx=16, pady=14)
        tk.Label(header, text='Python • Tkinter • MySQL • OpenCV', bg=theme.CARD_BG, fg=theme.MUTED, font=theme.SMALL_FONT).pack(side='right', padx=16)

        self.page_container = tk.Frame(right, bg=theme.BG_APP)
        self.page_container.pack(fill='both', expand=True, padx=16)
        self.page_container.grid_rowconfigure(0, weight=1)
        self.page_container.grid_columnconfigure(0, weight=1)

        footer = tk.Frame(right, bg=theme.CARD_BG, highlightbackground=theme.BORDER, highlightthickness=1)
        footer.pack(fill='x', padx=16, pady=(10, 16))
        tk.Label(footer, textvariable=self.status_var, bg=theme.CARD_BG, fg=theme.MUTED, font=theme.SMALL_FONT, anchor='w').pack(fill='x', padx=12, pady=8)

        page_classes = [DashboardPage, AnalysisPage, HistoryPage, CropsPage, FarmerPage]
        self.frames = {}
        for cls in page_classes:
            frame = cls(self.page_container, self)
            self.frames[cls.__name__] = frame
            frame.grid(row=0, column=0, sticky='nsew')

    def show_page(self, page_name: str):
        page = self.frames[page_name]
        for name, button in self.nav_buttons.items():
            button.set_active(name == page_name)
        try:
            if hasattr(page, 'on_show'):
                page.on_show()
            page.tkraise()
            self.set_status(f'{page.page_title} loaded successfully.')
        except DatabaseError as exc:
            messagebox.showerror('Database Error', str(exc))
            self.set_status('Database error occurred.')
        except Exception as exc:  # pragma: no cover - UI guard
            messagebox.showerror('Application Error', f'Unexpected error: {exc}')
            self.set_status('Unexpected error occurred.')

    def set_status(self, text: str):
        self.status_var.set(text)

    def logout(self):
        confirm = messagebox.askyesno('Logout', 'Do you want to logout from the application?')
        if confirm:
            self.current_user = None
            self.show_login()
