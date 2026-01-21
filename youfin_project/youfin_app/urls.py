from django.urls import path
from . import views

app_name = "youfin_app"

urlpatterns = [
    # urls & views bag.back-end
    path('dashboard/', views.dashboard, name='dashboard'),
    # anggaran
    path('anggaran/', views.anggaran, name='anggaran'),
    path('anggaran/tambah/', views.tambah_anggaran, name='tambah_anggaran'),
    path('anggaran/edit/<int:budget_id>/', views.edit_anggaran, name='edit_anggaran'),
    path('anggaran/hapus/<int:budget_id>/', views.hapus_anggaran, name='hapus_anggaran'),
    # transaksi
    path('transaksi/', views.transaksi, name='transaksi'),
    path('transaksi/tambah/', views.tambah_transaksi, name='tambah_transaksi'),
    path('transaksi/edit/<int:transaction_id>/', views.edit_transaksi, name='edit_transaksi'),
    path('transaksi/hapus/<int:transaction_id>/', views.delete_transaksi, name='delete_transaksi'),
    # kategori
    path('kategori/', views.kategori, name='kategori'),
    path('kategori/tambah/', views.tambah_kategori, name='tambah_kategori'),
    path('kategori/edit/<int:category_id>/', views.edit_kategori, name='edit_kategori'),
    path('kategori/hapus/<int:category_id>/', views.hapus_kategori, name='hapus_kategori'),
    # path('notifikasi/', views.notifikasi, name='notifikasi'),
    # path('premium/', views.premium, name='premium'),
    # path('konsultasi/', views.konsultasi, name='konsultasi'),
    path('tips/', views.tips, name='tips'),
    path('pengaturan/', views.pengaturan, name='pengaturan'),
    path('pengaturan/edit/', views.edit_pengaturan, name='edit_pengaturan'),
    path('pengaturan/edit/password', views.ubah_password, name='ubah_password'),
]