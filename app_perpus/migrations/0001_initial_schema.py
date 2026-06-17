from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS siswa (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT NOT NULL,
                    kelas TEXT NOT NULL,
                    nis TEXT NOT NULL UNIQUE,
                    is_active INTEGER NOT NULL DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS buku (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    judul TEXT NOT NULL,
                    pengarang TEXT NOT NULL,
                    kategori TEXT NOT NULL,
                    penerbit TEXT NOT NULL,
                    tahun_terbit INTEGER NOT NULL,
                    stok INTEGER NOT NULL DEFAULT 0,
                    isbn TEXT NOT NULL,
                    rak TEXT NOT NULL,
                    deskripsi TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS peminjaman (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    siswa_id INTEGER NOT NULL,
                    buku_id INTEGER NOT NULL,
                    tanggal_pinjam DATE NOT NULL,
                    jatuh_tempo DATE NOT NULL,
                    keperluan TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Dipinjam',
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (siswa_id) REFERENCES siswa (id),
                    FOREIGN KEY (buku_id) REFERENCES buku (id)
                );

                CREATE INDEX IF NOT EXISTS idx_peminjaman_siswa_id ON peminjaman (siswa_id);
                CREATE INDEX IF NOT EXISTS idx_peminjaman_buku_id ON peminjaman (buku_id);
                CREATE INDEX IF NOT EXISTS idx_peminjaman_status ON peminjaman (status);
            """,
            reverse_sql="""
                DROP TABLE IF EXISTS peminjaman;
                DROP TABLE IF EXISTS buku;
                DROP TABLE IF EXISTS siswa;
            """,
        ),
    ]
