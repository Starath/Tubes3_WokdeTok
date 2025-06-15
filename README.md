# Tubes3_WokdeTok
Tugas Besar 3 untuk mata kuliah Strategi Algoritma

</br>

<H2 align="center">Pemanfaatan Pattern Matching untuk Membangun Sistem ATS (Applicant Tracking System) Berbasis CV Digital</p>


##  Authors: Kelompok 03 - WokdeTok

<div align="center">

<table border="1" cellspacing="0" cellpadding="8"> 
  <tr> <th>NIM</th> <th>Nama</th> </tr> 
  <tr> <td>10122057</td> <td>Farrell Jabaar Altafataza</td> </tr> 
  <tr> <td>13523082</td> <td>Aramazaya</td> 
  </tr> <tr> <td>13523106</td> <td>Athian Nugraha Muarajuang</td> </tr> </table>

</div>

## Deskripsi Repository
Mengembangkan sistem ATS yang dapat melakukan pencocokan dan pencarian otomatis terhadap CV pelamar kerja menggunakan algoritma pattern matching. Sistem ini membantu HR atau rekruter untuk menemukan kandidat yang paling sesuai dengan kriteria yang dicari secara efisien dan akurat.

## 💻 Requirements dan Instalasi
### System Requirements
- Python 3.8 atau lebih baru
- MySQL Server 8.0 atau lebih baru

## Cara Menjalankan Program

### 1. Clone Repository
```bash
git clone https://github.com/Starath/Tubes3_WokdeTok.git
cd Tubes3_WokdeTok
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
### 3. Masuk Ke MySQL
#### ubuntu
```bash
sudo mysql -u root -p
```

#### windows
```bash
cd \path\to\your\MySQL\bin
mysql -u root -p
```

### 4. Jalankan Command Berikut
```
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'bitchass';
GRANT ALL PRIVILEGES ON *.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
SELECT user, host FROM mysql.user WHERE user = 'app_user';
EXIT;
```

### Fitur Wajib
- Queries by KMP, BM, Levenshtein
- PDF Extracting
- Regex Feature extraction
- Summary and View CV Applicants
- MySQL Database
- Flet GUI
### Fitur Bonus
- Aho-Chorasick
