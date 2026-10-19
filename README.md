# IF3170_G33_ApaKek

Tugas Besar 1 IF3170 Inteligensi Artifisial 2026/2027.

Program ini mencari susunan paket di dalam peti kemas truk agar total value paket yang diangkut sebesar mungkin. Susunan harus memenuhi beberapa batasan, yaitu paket tidak boleh saling bertabrakan, tidak boleh menembus dinding, tidak boleh melayang, paket fragile tidak boleh menjadi tumpuan, dan total berat tidak boleh melebihi kapasitas truk.

Algoritma yang diimplementasikan:

- Hill-climbing (steepest ascent, sideways move, stochastic, dan random restart)
- Simulated Annealing
- Genetic Algorithm

## Struktur Repository

```
docs/                  laporan
input/                 contoh file input
output/                hasil eksperimen
src/
  core/                model, fungsi objektif, neighbor, baca input
  hillClimbing/        varian hill-climbing
  simulatedAnnealing/  simulated annealing
  geneticAlgorithm/    genetic algorithm
  visualization/       plot dan visualisasi 3D
  tests/               unit test
  run_all.py           menjalankan semua eksperimen
```

## Setup

Program membutuhkan Python 3.10 atau lebih baru. Install library yang dibutuhkan dengan perintah berikut.

```
pip install -r requirements.txt
```

## Cara Menjalankan

Semua perintah dijalankan dari folder `src`.

```
cd src
python run_all.py
```

Secara default program membaca `input/contoh.json` dan menyimpan hasilnya ke folder `output`. File input dan folder output lain bisa diberikan sebagai argumen.

```
python run_all.py ../input/contoh.json ../output
```

Eksperimen yang dijalankan:

- Hill-climbing, setiap varian 3 kali (max sideways 100, stochastic 1000 iterasi, max restart 10)
- Simulated Annealing 3 kali
- Genetic Algorithm 18 kali, yaitu 3 variasi banyak iterasi dengan populasi tetap dan 3 variasi populasi dengan iterasi tetap, masing-masing 3 kali

Untuk setiap run, program menyimpan state awal dan akhir dalam format JSON, visualisasi 3D state awal dan akhir dalam format HTML, serta plot nilai objective function terhadap iterasi. Ringkasan semua run disimpan di `output/summary.csv`. File HTML dibuka dengan browser dan membutuhkan koneksi internet.

Unit test dapat dijalankan dengan perintah berikut.

```
python -m unittest discover -s tests -t .
```

## Format Input

Input berupa file JSON yang berisi data truk dan daftar paket.

```json
{
  "truck": {"w": 6, "l": 8, "h": 4, "max_capacity": 45},
  "packages": [
    {"id": "P01", "w": 2, "l": 3, "h": 1, "value": 40, "weight": 5, "fragile": false, "eta": 3}
  ]
}
```

| Atribut | Keterangan |
|---|---|
| `w`, `l`, `h` | lebar, panjang, dan tinggi, berupa bilangan bulat positif |
| `max_capacity` | kapasitas berat maksimum truk |
| `id` | nama paket, harus unik |
| `value` | nilai paket |
| `weight` | berat paket |
| `fragile` | `true` jika paket pecah belah, boleh tidak diisi (default `false`) |
| `eta` | perkiraan waktu kedatangan dalam hari, boleh tidak diisi (default `0`) |

## Pembagian Tugas

| Nama | NIM | Tugas |
|---|---|---|
| Jonathan Alveraldo Bangun | 13524120 | Simulated Annealing, plot, dan visualisasi 3D |
| Ramadhian Nabil Firdaus Gumay | 13524126 | Fungsi objektif dan constraint, representasi state, neighbor, seluruh varian hill-climbing, integrasi, dan eksperimen |
| Jonathan Harijadi | 13524144 | Genetic Algorithm |
