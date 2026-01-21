from django.db import models 
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from django.utils.timezone import now

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('L', 'Laki-laki'), ('P', 'Perempuan')], blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.user.username

    @property
    def is_complete(self):
        """
        Properti untuk mengecek apakah semua data profil terisi dengan lengkap.
        Memeriksa: nomor telepon, alamat, tanggal lahir, jenis kelamin, dan foto profil.
        """
        return all([
            self.phone_number, 
            self.address, 
            self.birth_date, 
            self.gender, 
            self.profile_picture
        ])

    def delete_profile_picture(self):
        """
        Fungsi untuk menghapus foto profil dari server dan mengatur ulang field profile_picture menjadi None.
        """
        if self.profile_picture:
            self.profile_picture.delete(save=False)  # Menghapus file dari media folder
            self.profile_picture = None  # Set field profile_picture ke None
            self.save()  # Menyimpan perubahan ke database


# kategori, anggaran dan transaksi
# Kategori Pengeluaran atau Pemasukan
class Category(models.Model):
    CATEGORY_CHOICES = [
        ('Pemasukan', 'Pemasukan'),
        ('Pengeluaran', 'Pengeluaran'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # Menambahkan hubungan ke user
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    total_transactions = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Field baru untuk menyimpan total transaksi

    def __str__(self):
        return self.name

    def update_total_transactions(self):
        """
        Menghitung dan memperbarui total transaksi untuk kategori ini.
        """
        self.total_transactions = self.transaction_set.aggregate(total=Sum('amount'))['total'] or 0
        self.save()


# Anggaran per Kategori
class Budget(models.Model):
    MONTH_CHOICES = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
        (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember')
    ]

    YEAR_CHOICES = [(r, str(r)) for r in range(2000, now().year + 2)]  # Menambahkan 2 tahun ke depan

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # Menambahkan hubungan ke user
    category = models.ForeignKey('Category', on_delete=models.CASCADE)  # Relasi dengan model Category
    bulan = models.IntegerField(choices=MONTH_CHOICES)  # Bulan (default dihapus)
    tahun = models.IntegerField(choices=YEAR_CHOICES)  # Tahun (default dihapus)
    initial_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Jumlah anggaran awal
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Total pengeluaran kategori ini
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Sisa saldo anggaran

    def __str__(self):
        return f"Anggaran {self.category.name} - {self.bulan}/{self.tahun}"
    
    @property
    def spent_percentage(self):
        """
        Mengembalikan persentase pengeluaran dari anggaran.
        Jika lebih dari 100%, batas maksimal 100%.
        """
        if self.initial_budget > 0:
            return min((self.total_expenses / self.initial_budget) * 100, 100)
        return 0

    def update_budget(self):
        """
        Menghitung dan memperbarui total pengeluaran dan sisa saldo untuk anggaran ini.
        """
        # Menghitung total pengeluaran berdasarkan kategori dan periode (bulan dan tahun)
        self.total_expenses = self.category.transaction_set.filter(
            transaction_type='Pengeluaran',
            date__month=self.bulan,
            date__year=self.tahun
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Menghitung sisa saldo
        self.remaining_balance = self.initial_budget - self.total_expenses

        # Menyimpan perubahan
        self.save()
    
    


# Transaksi Pengeluaran atau Pemasukan
class Transaction(models.Model):
    TRANSACTION_CHOICES = [
        ('Pemasukan', 'Pemasukan'),
        ('Pengeluaran', 'Pengeluaran'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # Menambahkan hubungan ke user
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f'{self.name} - {self.transaction_type}'
    


