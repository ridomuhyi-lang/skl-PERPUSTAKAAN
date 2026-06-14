from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection

# 1. Fungsi Dashboard Utama (Dinamis)
def dashboard(request):
    with connection.cursor() as cursor:
        # 1. Hitung akumulasi total unit buku (SUM dari kolom stok)
        cursor.execute("SELECT COALESCE(SUM(stok), 0) FROM buku;")
        total_buku = cursor.fetchone()[0]

        # 2. Hitung total judul buku unik
        cursor.execute("SELECT COUNT(*) FROM buku;")
        total_judul = cursor.fetchone()[0]

        # 3. Hitung peminjaman aktif (Sedang Dipinjam)
        cursor.execute("SELECT COUNT(*) FROM peminjaman WHERE status = 'Dipinjam';")
        sedang_dipinjam = cursor.fetchone()[0]

        # 4. Hitung peminjaman yang selesai (Sudah Dikembalikan)
        cursor.execute("SELECT COUNT(*) FROM peminjaman WHERE status = 'Dikembalikan';")
        sudah_dikembalikan = cursor.fetchone()[0]

        # 5. Ambil data judul dan stok untuk progress bar "Distribusi Stok Buku"
        cursor.execute("SELECT judul, stok FROM buku ORDER BY id ASC LIMIT 5;")
        buku_rows = cursor.fetchall()
        distribusi_buku = [{'judul': r[0], 'stok': r[1]} for r in buku_rows]

    context = {
        'total_buku': total_buku,
        'total_judul': total_judul,
        'sedang_dipinjam': sedang_dipinjam,
        'sudah_dikembalikan': sudah_dikembalikan,
        'distribusi_buku': distribusi_buku,
    }
    return render(request, 'app_perpus/index.html', context)
# 2. Fungsi Inisialisasi Tabel Database (Sudah Dibenerin Bug-nya)
def init_db(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS buku (
                id SERIAL PRIMARY KEY,
                judul VARCHAR(255) NOT NULL,
                pengarang VARCHAR(255) NOT NULL,
                kategori VARCHAR(50) NOT NULL,
                penerbit VARCHAR(255) NOT NULL,
                tahun_terbit INTEGER NOT NULL,
                rak VARCHAR(50) NOT NULL,
                stok INTEGER NOT NULL,
                deskripsi TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS siswa (
                id SERIAL PRIMARY KEY,
                nama VARCHAR(255) NOT NULL,
                kelas VARCHAR(100) NOT NULL,
                nis VARCHAR(50) UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT TRUE
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS peminjaman (
                id SERIAL PRIMARY KEY,
                siswa_id INTEGER REFERENCES siswa(id) ON DELETE CASCADE,
                buku_id INTEGER REFERENCES buku(id) ON DELETE CASCADE,
                tanggal_pinjam DATE NOT NULL,
                jatuh_tempo DATE NOT NULL,
                keperluan TEXT,
                status VARCHAR(50) DEFAULT 'Dipinjam'
            );
        """)
        
    return HttpResponse("Tabel berhasil divalidasi!")


# 3. Fungsi Menampilkan Daftar Siswa (User) dari Database
def list_siswa(request):
    with connection.cursor() as cursor:
        # Ambil semua data siswa terurut berdasarkan ID terkecil
        cursor.execute("SELECT id, nama, kelas, nis, is_active FROM siswa ORDER BY id ASC;")
        rows = cursor.fetchall()
        
        # Susun menjadi list dictionary agar mudah dibaca di template HTML
        daftar_siswa = []
        for row in rows:
            daftar_siswa.append({
                'id': row[0],
                'nama': row[1],
                'kelas': row[2],
                'nis': row[3],
                'is_active': row[4], # Boolean True/False
            })
            
    return render(request, 'app_perpus/users.html', {'daftar_siswa': daftar_siswa})


# 4. Fungsi Tambah Siswa Baru ke Database (Warna Tombol Ikut Berubah Biru)
def add_siswa(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        kelas = request.POST.get('kelas')
        nis = request.POST.get('nis')
        status_input = request.POST.get('status') # 'Aktif' atau 'Nonaktif'
        
        is_active = True if status_input == 'Aktif' else False
        
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO siswa (nama, kelas, nis, is_active) VALUES (%s, %s, %s, %s);",
                    [nama, kelas, nis, is_active]
                )
                return redirect('list_siswa')
            except Exception as e:
                return HttpResponse(f"Gagal menambahkan data. Error: {e}")
                
    return render(request, 'app_perpus/add-user.html')


# 5. LOGIC DETAIL SISWA (Ngerender detail-user.html Baru)
def detail_siswa(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nama, kelas, nis, is_active FROM siswa WHERE id = %s;", [id])
        row = cursor.fetchone()
        
    if not row:
        return HttpResponse("Siswa tidak ditemukan", status=404)
        
    siswa = {'id': row[0], 'nama': row[1], 'kelas': row[2], 'nis': row[3], 'is_active': row[4]}
    return render(request, 'app_perpus/detail-user.html', {'siswa': siswa})


# 6. LOGIC EDIT SISWA (Ngerender edit-user.html Dengan Tombol Perbarui Warna Biru Cerah)
def edit_siswa(request, id):
    with connection.cursor() as cursor:
        # Ambil data real dari PostgreSQL berdasarkan ID
        cursor.execute("SELECT id, nama, kelas, nis, is_active FROM siswa WHERE id = %s;", [id])
        row = cursor.fetchone()
        
    if not row:
        return HttpResponse("Siswa tidak ditemukan", status=404)
        
    # Mapping data agar bisa dibaca di html {{ siswa.nama }}
    siswa = {'id': row[0], 'nama': row[1], 'kelas': row[2], 'nis': row[3], 'is_active': row[4]}
    
    if request.method == 'POST':
        nama = request.POST.get('nama')
        kelas = request.POST.get('kelas')
        nis = request.POST.get('nis')
        status_input = request.POST.get('status')
        
        # Konversi teks "Aktif" menjadi True / False untuk database
        is_active = True if status_input == 'Aktif' else False
        
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE siswa SET nama=%s, kelas=%s, nis=%s, is_active=%s WHERE id=%s;",
                [nama, kelas, nis, is_active, id]
            )
        return redirect('list_siswa')
        
    return render(request, 'app_perpus/edit-user.html', {'siswa': siswa})


# 7. LOGIC HAPUS SISWA (Ngerender hapus-user.html Sesuai Foto Box & Tombol Merah Solid)
def delete_siswa(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nama FROM siswa WHERE id = %s;", [id])
        row = cursor.fetchone()
        
    if not row:
        return HttpResponse("Siswa tidak ditemukan", status=404)
        
    siswa = {'id': row[0], 'nama': row[1]}
    
    # Jika admin menekan tombol merah (Request POST) baru kita delete beneran
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM siswa WHERE id = %s;", [id])
        return redirect('list_siswa')
        
    # Jika cuma klik link, tampilin halaman konfirmasi 'hapus-user.html'
    return render(request, 'app_perpus/hapus-user.html', {'siswa': siswa})

# ==========================================
#              MODUL KELOLA BUKU
# ==========================================

# 1. Menampilkan Daftar Buku
def list_buku(request):
    with connection.cursor() as cursor:
        # Ambil semua data buku terurut berdasarkan ID terkecil
        cursor.execute("SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok FROM buku ORDER BY id ASC;")
        rows = cursor.fetchall()
        
        daftar_buku = []
        for row in rows:
            daftar_buku.append({
                'id': row[0],
                'judul': row[1],
                'pengarang': row[2],
                'kategori': row[3],
                'penerbit': row[4],
                'tahun_terbit': row[5],
                'rak': row[6],
                'stok': row[7],
            })
            
    return render(request, 'app_perpus/books.html', {'data_buku': daftar_buku})


# 2. Tambah Buku Baru
def add_buku(request):
    if request.method == 'POST':
        judul = request.POST.get('judul')
        pengarang = request.POST.get('pengarang')
        kategori = request.POST.get('kategori')
        penerbit = request.POST.get('penerbit')
        tahun_terbit = request.POST.get('tahun_terbit')
        rak = request.POST.get('rak')
        stok = request.POST.get('stok')
        isbn = request.POST.get('isbn', '') # Menangkap input ISBN
        deskripsi = request.POST.get('deskripsi', '')
        
        with connection.cursor() as cursor:
            try:
                # Pastikan kolom tabel buku lu sudah mendukung atau sesuaikan query-nya
                cursor.execute(
                    """INSERT INTO buku (judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                    [judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi]
                )
                return redirect('list_buku')
            except Exception as e:
                # Jika kolom 'isbn' belum ada di database lama lu, jalankan query ALTER TABLE otomatis di bawah:
                try:
                    cursor.execute("ALTER TABLE buku ADD COLUMN IF NOT EXISTS isbn VARCHAR(50);")
                    cursor.execute(
                        """INSERT INTO buku (judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                        [judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi]
                    )
                    return redirect('list_buku')
                except Exception as ex:
                    return HttpResponse(f"Gagal menambahkan data buku. Error: {ex}")
                
    return render(request, 'app_perpus/add-book.html')


# 3. Detail Buku
def detail_buku(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi FROM buku WHERE id = %s;", [id])
        row = cursor.fetchone()
        
    if not row:
        return HttpResponse("Buku tidak ditemukan", status=404)
        
    buku = {
        'id': row[0], 'judul': row[1], 'pengarang': row[2], 'kategori': row[3], 
        'penerbit': row[4], 'tahun_terbit': row[5], 'rak': row[6], 'stok': row[7],
        'isbn': row[8] if row[8] else '-', 'deskripsi': row[9]
    }
    return render(request, 'app_perpus/detail-book.html', {'buku': buku})


# 4. Edit Buku
def edit_buku(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi FROM buku WHERE id = %s;", [id])
        row = cursor.fetchone()
        
    if not row:
        return HttpResponse("Buku tidak ditemukan", status=404)
        
    buku = {
        'id': row[0], 'judul': row[1], 'pengarang': row[2], 'kategori': row[3], 
        'penerbit': row[4], 'tahun_terbit': row[5], 'rak': row[6], 'stok': row[7],
        'isbn': row[8] if row[8] else '', 'deskripsi': row[9]
    }
    
    if request.method == 'POST':
        judul = request.POST.get('judul')
        pengarang = request.POST.get('pengarang')
        kategori = request.POST.get('kategori')
        penerbit = request.POST.get('penerbit')
        tahun_terbit = request.POST.get('tahun_terbit')
        rak = request.POST.get('rak')
        stok = request.POST.get('stok')
        isbn = request.POST.get('isbn', '')
        deskripsi = request.POST.get('deskripsi', '')
        
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE buku SET judul=%s, pengarang=%s, kategori=%s, penerbit=%s, 
                   tahun_terbit=%s, rak=%s, stok=%s, isbn=%s, deskripsi=%s WHERE id=%s;""",
                [judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi, id]
            )
        return redirect('list_buku')
        
    return render(request, 'app_perpus/edit-book.html', {'buku': buku})


# 5. Hapus Buku
def delete_buku(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, judul FROM buku WHERE id = %s;", [id])
        row = cursor.fetchone()
        
    if not row:
        return HttpResponse("Buku tidak ditemukan", status=404)
        
    buku = {'id': row[0], 'judul': row[1]}
    
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM buku WHERE id = %s;", [id])
        return redirect('list_buku')
        
    return render(request, 'app_perpus/hapus-book.html', {'buku': buku})


# ==========================================
#              MODUL PEMINJAMAN
# ==========================================

# 1. Menampilkan Daftar Peminjaman
def list_peminjaman(request):
    with connection.cursor() as cursor:
        # Kita gunakan INNER JOIN karena tabel peminjaman hanya menyimpan siswa_id dan buku_id
        query = """
            SELECT p.id, s.nama, s.kelas, s.nis, b.judul, p.tanggal_pinjam, p.jatuh_tempo, p.keperluan, p.status
            FROM peminjaman p
            INNER JOIN siswa s ON p.siswa_id = s.id
            INNER JOIN buku b ON p.buku_id = b.id
            ORDER BY p.id ASC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        daftar_pinjam = []
        for row in rows:
            daftar_pinjam.append({
                'id': row[0],
                'nama_peminjam': row[1],
                'kelas': row[2],
                'nis': row[3],
                'judul_buku': row[4],
                'tanggal_pinjam': row[5],
                'jatuh_tempo': row[6],
                'keperluan': row[7],
                'status': row[8],
                'petugas': 'Budi Siregar' # Statis sesuai nama admin aktif di sidebar lu
            })

    return render(request, 'app_perpus/peminjaman.html', {'daftar_pinjam': daftar_pinjam})


# 2. Form Tambah Peminjaman Baru (Dropdown Dinamis dari DB)
def add_peminjaman(request):
    with connection.cursor() as cursor:
        # Ambil data siswa untuk pilihan dropdown Nama Peminjam
        cursor.execute("SELECT id, nama, kelas, nis FROM siswa WHERE is_active = TRUE ORDER BY nama ASC;")
        siswa_rows = cursor.fetchall()
        list_siswa_dropdown = [{'id': r[0], 'nama': r[1], 'kelas': r[2], 'nis': r[3]} for r in siswa_rows]

        # Ambil data buku untuk pilihan dropdown Pilih Buku (hanya yang stoknya > 0)
        cursor.execute("SELECT id, judul, stok FROM buku WHERE stok > 0 ORDER BY judul ASC;")
        buku_rows = cursor.fetchall()
        list_buku_dropdown = [{'id': r[0], 'judul': r[1], 'stok': r[2]} for r in buku_rows]

    if request.method == 'POST':
        siswa_id = request.POST.get('siswa_id')
        buku_id = request.POST.get('buku_id')
        tanggal_pinjam = request.POST.get('tanggal_pinjam')
        jatuh_tempo = request.POST.get('jatuh_tempo')
        keperluan = request.POST.get('keperluan')

        with connection.cursor() as cursor:
            try:
                # 1. Insert data peminjaman baru
                cursor.execute(
                    """INSERT INTO peminjaman (siswa_id, buku_id, tanggal_pinjam, jatuh_tempo, keperluan, status) 
                       VALUES (%s, %s, %s, %s, %s, 'Dipinjam');""",
                    [siswa_id, buku_id, tanggal_pinjam, jatuh_tempo, keperluan]
                )
                
                # 2. Potong stok buku otomatis di PostgreSQL sebanyak 1
                cursor.execute("UPDATE buku SET stok = stok - 1 WHERE id = %s;", [buku_id])
                
                return redirect('list_peminjaman')
            except Exception as e:
                return HttpResponse(f"Gagal memproses peminjaman. Error: {e}")

    context = {
        'list_siswa': list_siswa_dropdown,
        'list_buku': list_buku_dropdown
    }
    return render(request, 'app_perpus/pinjam-buku.html', context)


# 3. Fungsi Kembalikan Buku (Mengubah status & mengembalikan stok)
def kembalikan_buku(request, id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            # Ambil dulu buku_id terkait transaksi ini sebelum diupdate
            cursor.execute("SELECT buku_id FROM peminjaman WHERE id = %s;", [id])
            buku_id = cursor.fetchone()[0]

            # Update status peminjaman menjadi 'Dikembalikan'
            cursor.execute("UPDATE peminjaman SET status = 'Dikembalikan' WHERE id = %s;", [id])

            # Kembalikan stok buku ke database (+1)
            cursor.execute("UPDATE buku SET stok = stok + 1 WHERE id = %s;", [buku_id])
            
        return redirect('list_peminjaman')
    return HttpResponse("Metode tidak diizinkan", status=405)