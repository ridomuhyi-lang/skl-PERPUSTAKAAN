from django.db import models

class Buku(models.Model):
    judul = models.CharField(max_length=255)
    pengarang = models.CharField(max_length=255)
    kategori = models.CharField(max_length=100)
    penerbit = models.CharField(max_length=255)
    tahun_terbit = models.IntegerField()
    rak = models.CharField(max_length=100)
    stok = models.IntegerField()
    deskripsi = models.TextField(blank=True, null=True)
    isbn = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'buku' 
         # <--- INI WAJIB! Supaya Django dipaksa membaca tabel 'buku' di Postgres lu!