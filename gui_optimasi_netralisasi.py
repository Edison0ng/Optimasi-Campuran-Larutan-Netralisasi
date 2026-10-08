"""
Optimasi Campuran Larutan Netralisasi (UTS Soal 3)
Program linear minimasi biaya campuran Larutan Basa dan Larutan Garam.

Jalankan:
  - Di Jupyter/Colab  : GUI interaktif muncul
  - Di terminal       : python gui_optimasi_netralisasi.py
                        (perhitungan tetap jalan, GUI dilewati)
"""

from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Definisi model
# ---------------------------------------------------------------------------
CONSTRAINTS = [
    (F(4), F(2), F(24), 'Kebutuhan asam'),
    (F(2), F(4), F(24), 'Kebutuhan logam'),
    (F(1), F(0), F(0),  'x nonnegatif'),
    (F(0), F(1), F(0),  'y nonnegatif'),
]
COST = (F(20000), F(16000))   # biaya per liter: x = Rp20.000, y = Rp16.000


def feasible(x, y):
    """Cek apakah titik (x, y) memenuhi semua kendala."""
    return all(a * x + b * y >= rhs for a, b, rhs, _ in CONSTRAINTS)


def intersect(l1, l2):
    """Titik potong dua garis kendala."""
    a, b, r, _ = l1
    c, d, s, _ = l2
    det = a * d - b * c
    if det == 0:
        return None
    return (r * d - b * s) / det, (a * s - r * c) / det


def solve():
    """Enumerasi titik sudut layak, cari optimum eksak."""
    candidates = sorted({
        pt for pair in combinations(CONSTRAINTS, 2)
        if (pt := intersect(*pair)) is not None
    })
    vertices = [pt for pt in candidates if feasible(*pt)]
    if not vertices:
        raise ValueError('Tidak ditemukan titik sudut layak')
    optimum = min(vertices, key=lambda pt: COST[0] * pt[0] + COST[1] * pt[1])
    return candidates, vertices, optimum


def cost(x, y):
    return COST[0] * x + COST[1] * y


def rupiah(value):
    return f'Rp{int(value):,}'.replace(',', '.')


# ---------------------------------------------------------------------------
# 2. Perhitungan inti
# ---------------------------------------------------------------------------
def main():
    candidates, vertices, (x_opt, y_opt) = solve()

    # Verifikasi optimum & sertifikat batas bawah
    u, v = F(4000), F(2000)
    assert (x_opt, y_opt) == (F(4), F(4)), "Optimum tidak sesuai ekspektasi"
    assert 4 * u + 2 * v == COST[0] and 2 * u + 4 * v == COST[1]
    assert 24 * u + 24 * v == cost(x_opt, y_opt) == F(144000)
    assert 4 * x_opt + 2 * y_opt == 24 and 2 * x_opt + 4 * y_opt == 24

    print('=' * 60)
    print('Penyelesaian Aljabar')
    print('=' * 60)
    print('Garis batas: 2x + y = 12  dan  x + 2y = 12')
    print('Dari eliminasi: 3x = 12 -> x = 4, y = 4')
    print()
    print(f'Optimum: x = {x_opt} L Basa, y = {y_opt} L Garam')
    print(f'Agen asam : {4 * x_opt + 2 * y_opt} unit (minimal 24)')
    print(f'Agen logam: {2 * x_opt + 4 * y_opt} unit (minimal 24)')
    print(f'Biaya minimum: {rupiah(cost(x_opt, y_opt))}')
    print()
    print('Bukti batas bawah:')
    print('  20.000x + 16.000y >= 4.000(24) + 2.000(24) = Rp144.000')
    print('  Solusi (4,4) mencapai batas bawah -> optimum global.')
    print()

    # Tabel titik sudut
    print('=' * 60)
    print('Tabel Titik Sudut')
    print('=' * 60)
    rows = []
    for px, py in candidates:
        rows.append({
            'x Basa (L)': str(px),
            'y Garam (L)': str(py),
            'Agen asam': str(4 * px + 2 * py),
            'Agen logam': str(2 * px + 4 * py),
            'Biaya': rupiah(cost(px, py)),
            'Status': 'Layak' if feasible(px, py) else 'Tidak layak',
        })
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    print()

    # -----------------------------------------------------------------------
    # 3. Visualisasi
    # -----------------------------------------------------------------------
    xx = np.linspace(0, 14, 500)
    yy = np.linspace(0, 14, 500)
    X, Y = np.meshgrid(xx, yy)
    feas = (4 * X + 2 * Y >= 24) & (2 * X + 4 * Y >= 24)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.contourf(X, Y, feas.astype(int), levels=[.5, 1.5], colors=['#d9eaf5'], alpha=.9)
    ax.plot(xx, 12 - 2 * xx, label='Asam: 4x + 2y = 24', color='#277da1')
    ax.plot(xx, 6 - .5 * xx, label='Logam: 2x + 4y = 24', color='#f9844a')
    ax.plot(xx, 9 - 1.25 * xx, '--', color='#333', label='Biaya Rp144.000')
    for px, py in vertices:
        ax.scatter(float(px), float(py), color='#222', zorder=4)
        label = f'({px},{py})' + (' optimum' if (px, py) == (x_opt, y_opt) else '')
        ax.annotate(label, (float(px), float(py)),
                    xytext=(7, 8), textcoords='offset points')
    ax.set(xlim=(0, 14), ylim=(0, 14),
           xlabel='Larutan Basa x (liter)',
           ylabel='Larutan Garam y (liter)',
           title='Daerah layak dan solusi biaya minimum')
    ax.grid(alpha=.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig('daerah_layak.png', dpi=180)
    print("Grafik disimpan: daerah_layak.png")

    # -----------------------------------------------------------------------
    # 4. Ekspor CSV
    # -----------------------------------------------------------------------
    out_df = pd.DataFrame([
        {'Basa (L)': str(a), 'Garam (L)': str(b), 'Biaya (Rp)': int(cost(a, b))}
        for a, b in vertices
    ])
    out_df.to_csv('titik_sudut.csv', index=False)
    print("Tabel titik sudut disimpan: titik_sudut.csv")

    # Tampilkan plot kalau di Jupyter/Colab
    try:
        get_ipython  # noqa: F821
        plt.show()
    except NameError:
        # Di terminal: simpan saja, tidak perlu show
        plt.close(fig)

    return candidates, vertices, (x_opt, y_opt)


# ---------------------------------------------------------------------------
# 5. GUI interaktif (hanya jalan di Jupyter/Colab)
# ---------------------------------------------------------------------------
def run_gui(x_opt, y_opt):
    """GUI slider; otomatis dilewati jika bukan di Jupyter/Colab."""
    try:
        import ipywidgets as widgets
        from IPython.display import display, clear_output, Markdown
    except ImportError:
        print("\n[INFO] ipywidgets tidak tersedia. GUI dilewati.")
        print("       Jalankan di Jupyter/Colab untuk memakai GUI interaktif.")
        return

    try:
        from google.colab import output as colab_output
        colab_output.enable_custom_widget_manager()
    except Exception:
        pass

    basa = widgets.FloatSlider(value=4, min=0, max=15, step=.5,
                               description='Basa (L):', readout_format='.1f')
    garam = widgets.FloatSlider(value=4, min=0, max=15, step=.5,
                                description='Garam (L):', readout_format='.1f')
    button = widgets.Button(description='Periksa campuran',
                            button_style='primary', icon='check')
    out = widgets.Output()

    def check_mix(_):
        x = F(str(basa.value))
        y = F(str(garam.value))
        acid = 4 * x + 2 * y
        metal = 2 * x + 4 * y
        z = cost(x, y)
        with out:
            clear_output(wait=True)
            status = ('✅ Memenuhi kedua kebutuhan' if feasible(x, y)
                      else '❌ Belum memenuhi semua kebutuhan')
            display(Markdown(
                f"### {status}\n\n"
                f"- Agen pengikat asam: **{acid} unit** (minimal 24)\n"
                f"- Agen pengikat logam: **{metal} unit** (minimal 24)\n"
                f"- Biaya campuran: **{rupiah(z)}**\n"
                f"- Optimum model: **4 L Basa + 4 L Garam = Rp144.000**\n"
                f"- Selisih dari biaya optimum: "
                f"**{rupiah(z - cost(x_opt, y_opt))}**"
            ))

    button.on_click(check_mix)
    display(widgets.VBox([basa, garam, button, out]))
    button.click()


if __name__ == '__main__':
    _, _, (x_opt, y_opt) = main()
    run_gui(x_opt, y_opt)