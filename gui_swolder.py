import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont

# ------------------------------------------------------------
# Swolder (GUI Tkinter) — dimensioni INDIPENDENTI per ogni groupbox
# + tema "boxed" per Entry/Combobox (bordi completi)
# + PALETTE COLORI stile Windows
# + FONT globale: CONSOLAS
# e adattamento automatico della finestra
# ------------------------------------------------------------

# --- FONT GLOBALE ---
FONT_FAMILY = "Consolas"
FONT_SIZE = 10  # cambia qui per ingrandire/ridurre

# --- DIMENSIONI INDEPENDENTI (px) ---
GBALL_H = 160
GB1_W, GB1_H = 195, GBALL_H   # Livello 1
GB2_W, GB2_H = 195, GBALL_H   # Livello 2
GB3_W, GB3_H = 195, GBALL_H   # Livello 3
GB5_W, GB5_H = 255, GBALL_H   # Livello 5
LIST_W, LIST_H = 350, GBALL_H # Colonna "Commesse esistenti"

# Spaziature/padding
OUTER_PAD = 8             # padding del frame root
COL_GAP = 8               # spazio orizzontale tra colonne
ROW_GAP = 6               # spazio verticale riga superiore vs resto

class SwolderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Swolder 1.4.2")
        self.resizable(False, False)

        # --- FONT: Consolas per tutto (tk + ttk) ---
        self._ui_font = tkfont.Font(family=FONT_FAMILY, size=FONT_SIZE)
        self.option_add("*Font", self._ui_font)

        # stato
        self.cartella_lav = tk.StringVar(value="P:/Lav")
        self.num_commesse = tk.IntVar(value=0)
        self.tipo_pompa_var = tk.StringVar()
        self.nuovo_tipo_pompa_var = tk.StringVar()
        self.modello_pompa_num = tk.StringVar()
        self.modello_pompa_letters = tk.StringVar()
        self.modello_pompa_suffix = tk.StringVar()
        self.modello_esistente_var = tk.StringVar()
        self.idraulica_letters = tk.StringVar()
        self.idraulica_esistente_var = tk.StringVar()
        self.commessa = tk.StringVar()
        self.annomese = tk.StringVar()
        self.sheet_type = tk.StringVar(value="NPS")

        # tema + palette (configura anche font ttk)
        self._apply_theme()

        self._build_ui()
        self._bind_uppercase()

        # adatta la finestra alla dimensione richiesta dai widget
        self.after(0, self._autofit_window)

    # --------------------- THEME / COLORI ---------------------
    def _apply_theme(self):
        # Palette stile Windows (chiara)
        BG       = "#f3f3f3"   # sfondo finestra
        SURFACE  = "#ffffff"   # superfici controlli (entry/combo/listbox)
        FG       = "#1f1f1f"   # testo principale
        SUBTLE   = "#5f6a6a"   # testo secondario (label frame titles)
        ACCENT   = "#0078D4"   # Windows blue (Fluent)
        BORDER   = "#d1d5db"   # bordo controlli

        style = ttk.Style(self)

        # Prova ad usare i temi Windows nativi quando possibile
        # 'vista' è disponibile su Windows moderni; altrimenti fallback a 'clam'
        try:
            if sys.platform.startswith("win") and "vista" in style.theme_names():
                style.theme_use("vista")
            else:
                style.theme_use("clam")
        except Exception:
            style.theme_use("clam")

        # Colora la finestra principale (tk)
        self.configure(bg=BG)

        # Default ttk (applico anche il font globale)
        style.configure(".", background=BG, foreground=FG, font=self._ui_font)

        # Frame e Label
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG, font=self._ui_font)

        # LabelFrame e titolo
        style.configure("TLabelframe", background=BG, bordercolor=BORDER, relief="solid")
        style.configure("TLabelframe.Label", background=BG, foreground=SUBTLE, font=self._ui_font)

        # ENTRY boxed (bordi completi)
        style.configure(
            "Box.TEntry",
            padding=4,
            relief="solid",
            borderwidth=1,
            bordercolor=BORDER,
            fieldbackground=SURFACE,
            foreground=FG,
            insertcolor=FG,
            font=self._ui_font,
        )

        # COMBOBOX boxed
        style.configure(
            "Box.TCombobox",
            padding=4,
            relief="solid",
            borderwidth=1,
            bordercolor=BORDER,
            fieldbackground=SURFACE,
            foreground=FG,
            font=self._ui_font,
        )
        style.map(
            "Box.TCombobox",
            fieldbackground=[("readonly", SURFACE), ("!readonly", SURFACE)],
            foreground=[("readonly", FG)],
            # bordo in focus (piccolo tocco Win): accento sul focus
            bordercolor=[("focus", ACCENT), ("!focus", BORDER)]
        )

        # BUTTON (neutro) + Accent opzionale
        style.configure("TButton", padding=6, background=BG, foreground=FG, bordercolor=BORDER, font=self._ui_font)
        style.map(
            "TButton",
            focuscolor=[("focus", ACCENT)]
        )
        style.configure(
            "Accent.TButton",
            padding=6,
            background=ACCENT,
            foreground="#ffffff",
            borderwidth=1,
            relief="solid",
            bordercolor=ACCENT,
            font=self._ui_font,
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#106EBE")],  # shade del blu Windows
            bordercolor=[("active", "#106EBE")]
        )

        # SCROLLBAR base
        style.configure("Vertical.TScrollbar", background=BG, troughcolor=BG, bordercolor=BG)
        style.configure("Horizontal.TScrollbar", background=BG, troughcolor=BG, bordercolor=BG)

        # Listbox (tk widget) colori coordinati
        self._listbox_colors = dict(
            bg=SURFACE,
            fg=FG,
            selectbackground=ACCENT,
            selectforeground="#ffffff",
            highlightthickness=0,
            relief="flat",
            font=self._ui_font,
        )

    # --------------------- UI ---------------------
    def _build_ui(self):
        root = ttk.Frame(self, padding=OUTER_PAD)
        root.grid(row=0, column=0, sticky="nsew")

        # colonne con minsize INDIVIDUALI
        root.columnconfigure(0, weight=0, minsize=GB1_W)
        root.columnconfigure(1, weight=0, minsize=GB2_W)
        root.columnconfigure(2, weight=0, minsize=GB3_W)
        root.columnconfigure(3, weight=0, minsize=GB5_W)
        root.columnconfigure(4, weight=1, minsize=LIST_W)
        root.rowconfigure(0, weight=0)
        root.rowconfigure(1, weight=0)
        root.rowconfigure(2, weight=0)

        # riga 0: groupbox + lista
        gb1 = ttk.LabelFrame(root, text="LEVEL 1", padding=(10, 6))
        gb1.grid(row=0, column=0, sticky="nsew", padx=(0, COL_GAP), pady=(0, ROW_GAP))
        self._gb1_contents(gb1)

        gb2 = ttk.LabelFrame(root, text="LEVEL 2", padding=(10, 6))
        gb2.grid(row=0, column=1, sticky="nsew", padx=(0, COL_GAP), pady=(0, ROW_GAP))
        self._gb2_contents(gb2)

        gb3 = ttk.LabelFrame(root, text="LEVEL 3", padding=(10, 6))
        gb3.grid(row=0, column=2, sticky="nsew", padx=(0, COL_GAP), pady=(0, ROW_GAP))
        self._gb3_contents(gb3)

        gb5 = ttk.LabelFrame(root, text="LEVEL 4", padding=(10, 6))
        gb5.grid(row=0, column=3, sticky="nsew", padx=(0, COL_GAP), pady=(0, ROW_GAP))
        self._gb5_contents(gb5)

        # dimensioni indipendenti
        for gb, (w, h) in [
            (gb1, (GB1_W, GB1_H)),
            (gb2, (GB2_W, GB2_H)),
            (gb3, (GB3_W, GB3_H)),
            (gb5, (GB5_W, GB5_H)),
        ]:
            gb.grid_propagate(False)
            gb.configure(width=w, height=h)

        # colonna destra
        right = ttk.LabelFrame(root, text="EXISTING JOBS", padding=(6, 6))
        right.grid(row=0, column=4, sticky="nsew", padx=(0, 0), pady=(0, ROW_GAP))
        right.grid_propagate(False)
        right.configure(width=LIST_W, height=max(GB1_H, GB2_H, GB3_H, GB5_H, LIST_H))
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        list_container = ttk.Frame(right)
        list_container.grid(row=0, column=0, sticky="nsew", padx=6, pady=4)
        list_container.rowconfigure(0, weight=1)
        list_container.columnconfigure(0, weight=1)

        self.list_commesse = tk.Listbox(list_container, selectmode=tk.EXTENDED, height=10)
        self.list_commesse.grid(row=0, column=0, sticky="nsew")
        if hasattr(self, "_listbox_colors"):
            self.list_commesse.configure(**self._listbox_colors)

        yscroll = ttk.Scrollbar(list_container, orient="vertical", command=self.list_commesse.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.list_commesse.configure(yscrollcommand=yscroll.set)
        self.list_commesse.bind("<<ListboxSelect>>", self._update_num_commesse)

        bottom_info = ttk.Frame(right)
        bottom_info.grid(row=1, column=0, sticky="we", padx=6, pady=(2,6))
        ttk.Label(bottom_info, text="Jobs find:").pack(side="left")
        ttk.Label(bottom_info, textvariable=self.num_commesse).pack(side="left", padx=(4,0))

        # riga 1: path
        path_row = ttk.Frame(root)
        path_row.grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, ROW_GAP))
        ttk.Label(path_row, text="Actual Path:").pack(side="left")
        ttk.Label(path_row, textvariable=self.cartella_lav).pack(side="left", padx=(4,0))

        # riga 2: pulsanti
        btn_bar = ttk.Frame(root)
        btn_bar.grid(row=2, column=0, columnspan=5, sticky="we")
        btn_bar.columnconfigure(7, weight=1)

        self.btn_set_folder = ttk.Button(btn_bar, text="Set Folder Path", command=self.on_set_folder)
        self.btn_set_folder.grid(row=0, column=0, padx=4)

        self.btn_find_job = ttk.Button(btn_bar, text="Find Job", command=self.on_find_job)
        self.btn_find_job.grid(row=0, column=1, padx=4)

        self.btn_file_manager = ttk.Button(btn_bar, text="File Manager", command=self.on_open_folder)
        self.btn_file_manager.grid(row=0, column=2, padx=4)

        self.btn_reset = ttk.Button(btn_bar, text="Reset", command=self.on_reset)
        self.btn_reset.grid(row=0, column=3, padx=4)

        self.btn_open_folder = ttk.Button(btn_bar, text="Open Folder", command=self.on_open_folder)
        self.btn_open_folder.state(["disabled"])
        self.btn_open_folder.grid(row=0, column=4, padx=4)

        self.btn_crea_tipo = ttk.Button(btn_bar, text="New Pump Type", command=self.on_crea_tipo)
        self.btn_crea_tipo.state(["disabled"])
        self.btn_crea_tipo.grid(row=0, column=5, padx=4)

        ttk.Label(btn_bar, text="").grid(row=0, column=6, padx=4)  # spacer
        self.btn_crea_doctree = ttk.Button(btn_bar, text="Create Doc.Tree", command=self.on_crea_doctree)
        self.btn_crea_doctree.grid(row=0, column=7, padx=4, sticky="e")

    # --- Adatta la finestra alla dimensione richiesta dai widget ---
    def _autofit_window(self):
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        self.geometry(f"{w}x{h}")

    def _gb1_contents(self, parent: ttk.LabelFrame):
        pad = dict(padx=1, pady=2)
        ttk.Label(parent, text="LAV FOLDER").grid(row=0, column=0, sticky="w", **pad)
        cb = ttk.Combobox(
            parent,
            textvariable=self.cartella_lav,
            state="readonly",
            values=[self.cartella_lav.get()],
            style="Box.TCombobox"
        )
        cb.grid(row=1, column=0, sticky="we", **pad)

        ttk.Label(parent, text="PUMP TYPE").grid(row=2, column=0, sticky="w", **pad)
        self.cb_tipo_pompa = ttk.Combobox(
            parent,
            textvariable=self.tipo_pompa_var,
            state="readonly",
            style="Box.TCombobox"
        )
        self.cb_tipo_pompa.grid(row=3, column=0, sticky="we", **pad)

    def _gb2_contents(self, parent: ttk.LabelFrame):
        pad = dict(padx=3, pady=2)
        ttk.Label(parent, text="PUMP MODEL").grid(row=0, column=0, columnspan=3, sticky="w", **pad)

        ttk.Entry(parent, width=4, textvariable=self.modello_pompa_num, style="Box.TEntry").grid(row=1, column=0, **pad)
        ttk.Entry(parent, width=6, textvariable=self.modello_pompa_letters, style="Box.TEntry").grid(row=1, column=1, **pad)
        ttk.Entry(parent, width=4, textvariable=self.modello_pompa_suffix, style="Box.TEntry").grid(row=1, column=2, **pad)

        ttk.Label(parent, text="EXISTING PUMP").grid(row=2, column=0, columnspan=3, sticky="w", **pad)
        self.cb_modello_esistente = ttk.Combobox(
            parent,
            textvariable=self.modello_esistente_var,
            state="readonly",
            style="Box.TCombobox"
        )
        self.cb_modello_esistente.grid(row=3, column=0, columnspan=3, sticky="we", **pad)

    def _gb3_contents(self, parent: ttk.LabelFrame):
        pad = dict(padx=1, pady=2)
        ttk.Label(parent, text="HYDRAULIC").grid(row=0, column=0, columnspan=2, sticky="w", **pad)
        ttk.Label(parent, text="idr").grid(row=1, column=0, sticky="e", **pad)
        ttk.Entry(parent, width=5, textvariable=self.idraulica_letters, style="Box.TEntry").grid(row=1, column=1, sticky="w", **pad)

        ttk.Label(parent, text="EXISTING HYDRAULIC").grid(row=2, column=0, columnspan=2, sticky="w", **pad)
        self.cb_idraulica_esistente = ttk.Combobox(
            parent,
            textvariable=self.idraulica_esistente_var,
            state="readonly",
            style="Box.TCombobox"
        )
        self.cb_idraulica_esistente.grid(row=3, column=0, columnspan=2, sticky="we", **pad)

    def _gb5_contents(self, parent: ttk.LabelFrame):
        pad = dict(padx=5, pady=2)
        ttk.Label(parent, text="JOB").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(parent, textvariable=self.commessa, width=20, style="Box.TEntry").grid(row=1, column=0, sticky="we", **pad)

        ttk.Label(parent, text="YYMM").grid(row=0, column=1, **pad)
        ttk.Entry(
            parent,
            textvariable=self.annomese,
            width=5,
            validate="key",
            validatecommand=(self.register(self._validate_yymm), "%P"),
            style="Box.TEntry"
        ).grid(row=1, column=1, **pad)

        rb_frame = ttk.Frame(parent)
        rb_frame.grid(row=2, column=0, columnspan=2, sticky="w", padx=8, pady=(4,8))
        ttk.Radiobutton(rb_frame, text="NPS - Not Project Sheet", value="NPS", variable=self.sheet_type).pack(anchor="w")
        ttk.Radiobutton(rb_frame, text="DPS - Document Project Sheet", value="DPS", variable=self.sheet_type).pack(anchor="w")

    def _bind_uppercase(self):
        for var in (
            self.modello_pompa_letters,
            self.modello_pompa_suffix,
            self.idraulica_letters,
            self.commessa,
            self.nuovo_tipo_pompa_var,
        ):
            var.trace_add("write", self._to_upper_var(var))

    def _to_upper_var(self, var):
        def _inner(*_):
            val = var.get()
            if val != val.upper():
                var.set(val.upper())
        return _inner

    def _validate_yymm(self, proposed: str) -> bool:
        if len(proposed) > 4:
            return False
        if not proposed:
            return True
        return proposed.isdigit()

    def _update_num_commesse(self, _evt=None):
        self.num_commesse.set(len(self.list_commesse.curselection()))

    # --------------------- Event handlers (PLACEHOLDER) ---------------------
    def on_set_folder(self):
        chosen = filedialog.askdirectory(title="Seleziona Cartella Lavoro")
        if chosen:
            self.cartella_lav.set(chosen)
            try:
                self.btn_open_folder.state(["!disabled"])
            except Exception:
                pass

    def on_open_folder(self):
        import os, subprocess, sys
        path = self.cartella_lav.get()
        if not path:
            messagebox.showwarning("Attenzione", "Nessuna cartella impostata.")
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def on_reset(self):
        self.tipo_pompa_var.set("")
        self.nuovo_tipo_pompa_var.set("")
        self.modello_pompa_num.set("")
        self.modello_pompa_letters.set("")
        self.modello_pompa_suffix.set("")
        self.modello_esistente_var.set("")
        self.idraulica_letters.set("")
        self.idraulica_esistente_var.set("")
        self.commessa.set("")
        self.annomese.set("")
        self.sheet_type.set("NPS")
        self.list_commesse.selection_clear(0, tk.END)
        self.num_commesse.set(0)
        try:
            self.btn_open_folder.state(["disabled"])
        except Exception:
            pass
        self._autofit_window()

    def on_crea_doctree(self):
        messagebox.showinfo("Crea DocTree", "Logica DocTree non ancora implementata.")

    def on_crea_tipo(self):
        messagebox.showinfo("Crea Tipo Pompa", "Funzione non ancora implementata.")

    def on_find_job(self):
        self.list_commesse.delete(0, tk.END)
        sample = ["NPS2501-001", "DPS2412-014", "NPS2410-003", "DPS2307-002"]
        for item in sample:
            self.list_commesse.insert(tk.END, item)
        self.num_commesse.set(0)
        self._autofit_window()

if __name__ == "__main__":
    app = SwolderApp()
    app.mainloop()
