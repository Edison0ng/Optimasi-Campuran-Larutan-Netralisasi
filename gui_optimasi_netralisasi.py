"""
GUI Desktop (Tkinter) untuk Optimasi Campuran Larutan Netralisasi.
Jalankan di terminal: python gui_tkinter.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from fractions import Fraction as F

# ---------------------------------------------------------------------------
# Model (sama seperti versi utama)
# ---------------------------------------------------------------------------
CONSTRAINTS = [
    (F(4), F(2), F(24), 'Kebutuhan asam'),
    (F(2), F(4), F(24), 'Kebutuhan logam'),
    (F(1), F(0), F(0),  'x nonnegatif'),
    (F(0), F(1), F(0),  'y nonnegatif'),
]
COST = (F(20000), F(16000))
X_OPT, Y_OPT = F(4), F(4)   # solusi optimum yang sudah dihitung


def feasible(x, y):
    return all(a * x + b * y >= rhs for a, b, rhs, _ in CONSTRAINTS)


def cost(x, y):
    return COST[0] * x + COST[1] * y


def rupiah(value):
    return f'Rp{int(value):,}'.replace(',', '.')


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------
class NetralisasiGUI:
    def __init__(self, root):
        self.root = root
        root.title('Optimasi Campuran Larutan Netralisasi')
        root.geometry('520x480')
        root.configure(bg='#f5f7fa')

        # Judul
        title = tk.Label(root, text='Optimasi Campuran Larutan Netralisasi',
                         font=('Segoe UI', 14, 'bold'),
                         bg='#f5f7fa', fg='#1f3a5f')
        title.pack(pady=(15, 5))

        subtitle = tk.Label(root,
                            text='UTS Soal 3 — Minimasi biaya campuran',
                            font=('Segoe UI', 9, 'italic'),
                            bg='#f5f7fa', fg='#555')
        subtitle.pack(pady=(0, 15))

        # Frame input
        frame = tk.Frame(root, bg='#f5f7fa')
        frame.pack(pady=5)

        tk.Label(frame, text='Larutan Basa (L):', font=('Segoe UI', 10),
                 bg='#f5f7fa').grid(row=0, column=0, sticky='w', padx=5, pady=8)
        self.basa_var = tk.DoubleVar(value=4.0)
        self.basa_scale = ttk.Scale(frame, from_=0, to=15, orient='horizontal',
                                    variable=self.basa_var, length=280,
                                    command=self.update_basa_label)
        self.basa_scale.grid(row=0, column=1, padx=5)
        self.basa_label = tk.Label(frame, text='4.0', width=6,
                                   font=('Consolas', 10, 'bold'),
                                   bg='#f5f7fa', fg='#277da1')
        self.basa_label.grid(row=0, column=2)

        tk.Label(frame, text='Larutan Garam (L):', font=('Segoe UI', 10),
                 bg='#f5f7fa').grid(row=1, column=0, sticky='w', padx=5, pady=8)
        self.garam_var = tk.DoubleVar(value=4.0)
        self.garam_scale = ttk.Scale(frame, from_=0, to=15, orient='horizontal',
                                     variable=self.garam_var, length=280,
                                     command=self.update_garam_label)
        self.garam_scale.grid(row=1, column=1, padx=5)
        self.garam_label = tk.Label(frame, text='4.0', width=6,
                                    font=('Consolas', 10, 'bold'),
                                    bg='#f5f7fa', fg='#f9844a')
        self.garam_label.grid(row=1, column=2)

        # Tombol aksi
        btn_frame = tk.Frame(root, bg='#f5f7fa')
        btn_frame.pack(pady=15)

        check_btn = tk.Button(btn_frame, text='  Periksa Campuran  ',
                              font=('Segoe UI', 10, 'bold'),
                              bg='#277da1', fg='white',
                              activebackground='#1e5f7a',
                              relief='flat', cursor='hand2',
                              command=self.check_mix)
        check_btn.pack(side='left', padx=5, ipady=6)

        reset_btn = tk.Button(btn_frame, text='  Reset  ',
                              font=('Segoe UI', 10),
                              bg='#e0e0e0', fg='#333',
                              relief='flat', cursor='hand2',
                              command=self.reset)
        reset_btn.pack(side='left', padx=5, ipady=6)

        # Hasil
        self.result_frame = tk.LabelFrame(root, text='Hasil Pemeriksaan',
                                          font=('Segoe UI', 10, 'bold'),
                                          bg='#ffffff', fg='#1f3a5f',
                                          padx=15, pady=15)
        self.result_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        self.status_label = tk.Label(self.result_frame, text='—',
                                     font=('Segoe UI', 11, 'bold'),
                                     bg='#ffffff', fg='#555')
        self.status_label.pack(anchor='w', pady=(0, 10))

        self.detail_labels = {}
        for key in ['Agen pengikat asam', 'Agen pengikat logam',
                    'Biaya campuran', 'Optimum model',
                    'Selisih dari biaya optimum']:
            row = tk.Frame(self.result_frame, bg='#ffffff')
            row.pack(fill='x', pady=2)
            tk.Label(row, text=f'{key}:', font=('Segoe UI', 9),
                     bg='#ffffff', fg='#555', width=22, anchor='w').pack(side='left')
            val = tk.Label(row, text='—', font=('Consolas', 10, 'bold'),
                           bg='#ffffff', fg='#222', anchor='w')
            val.pack(side='left')
            self.detail_labels[key] = val

        # Otomatis periksa saat pertama dibuka
        self.check_mix()

    def update_basa_label(self, _=None):
        self.basa_label.config(text=f'{self.basa_var.get():.1f}')

    def update_garam_label(self, _=None):
        self.garam_label.config(text=f'{self.garam_var.get():.1f}')

    def reset(self):
        self.basa_var.set(4.0)
        self.garam_var.set(4.0)
        self.update_basa_label()
        self.update_garam_label()
        self.check_mix()

    def check_mix(self):
        # Bulatkan ke 0.5 supaya konsisten dengan slider
        x_val = round(self.basa_var.get() * 2) / 2
        y_val = round(self.garam_var.get() * 2) / 2
        x = F(str(x_val))
        y = F(str(y_val))

        acid = 4 * x + 2 * y
        metal = 2 * x + 4 * y
        z = cost(x, y)
        diff = z - cost(X_OPT, Y_OPT)

        # Status
        if feasible(x, y):
            self.status_label.config(
                text='✅ Memenuhi kedua kebutuhan', fg='#2a9d8f')
        else:
            self.status_label.config(
                text='❌ Belum memenuhi semua kebutuhan', fg='#e63946')

        # Detail
        self.detail_labels['Agen pengikat asam'].config(
            text=f'{acid} unit (minimal 24)',
            fg='#2a9d8f' if acid >= 24 else '#e63946')
        self.detail_labels['Agen pengikat logam'].config(
            text=f'{metal} unit (minimal 24)',
            fg='#2a9d8f' if metal >= 24 else '#e63946')
        self.detail_labels['Biaya campuran'].config(text=rupiah(z))
        self.detail_labels['Optimum model'].config(
            text='4 L Basa + 4 L Garam = Rp144.000')
        self.detail_labels['Selisih dari biaya optimum'].config(
            text=rupiah(diff),
            fg='#2a9d8f' if diff == 0 else '#e63946')


if __name__ == '__main__':
    root = tk.Tk()
    app = NetralisasiGUI(root)
    root.mainloop()