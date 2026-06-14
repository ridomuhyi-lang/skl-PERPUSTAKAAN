
from django.urls import path
from . import views

urlpatterns = [
    # JALUR UTAMA & USER
    path('', views.dashboard, name='dashboard'),
    path('init/', views.init_db, name='init_db'),
    path('users/', views.list_siswa, name='list_siswa'),
    path('users/add/', views.add_siswa, name='add_siswa'),
    path('users/detail/<int:id>/', views.detail_siswa, name='detail_siswa'),
    path('users/edit/<int:id>/', views.edit_siswa, name='edit_siswa'),
    path('users/delete/<int:id>/', views.delete_siswa, name='delete_siswa'),
    
    # JALUR BARU: MODUL KELOLA BUKU
    path('books/', views.list_buku, name='list_buku'),
    path('books/add/', views.add_buku, name='add_buku'),
    path('books/detail/<int:id>/', views.detail_buku, name='detail_buku'),
    path('books/edit/<int:id>/', views.edit_buku, name='edit_buku'),
    path('books/delete/<int:id>/', views.delete_buku, name='delete_buku'),

    #peminjaman
   path('peminjaman/', views.list_peminjaman, name='list_peminjaman'),
   path('peminjaman/tambah/', views.add_peminjaman, name='add_peminjaman'),
   path('peminjaman/kembali/<int:id>/', views.kembalikan_buku, name='kembalikan_buku'),
]