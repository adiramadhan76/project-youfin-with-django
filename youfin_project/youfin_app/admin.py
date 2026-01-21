from django.contrib import admin
from .models import Profile, Category, Budget, Transaction

# Register your models here.
# Register Profile model
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address', 'birth_date', 'gender', 'is_complete')
    search_fields = ('user__username', 'user__email')


# kategori, anggaran dan transaksi
# Register Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'total_transactions', 'user')
    search_fields = ('name', 'category_type', 'user__username')
    list_filter = ('category_type', 'user')  # Menambahkan filter berdasarkan user dan jenis kategori


# Register Budget model
@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('category', 'bulan', 'tahun', 'initial_budget', 'total_expenses', 'remaining_balance', 'user')
    search_fields = ('category__name', 'user__username')
    list_filter = ('user', 'category__category_type', 'bulan', 'tahun')  # Menambahkan filter bulan dan tahun


# Register Transaction model
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'transaction_type', 'amount', 'date', 'user')
    search_fields = ('name', 'category__name', 'transaction_type', 'user__username')
    list_filter = ('transaction_type', 'user', 'category__category_type')  # Menambahkan filter berdasarkan user dan jenis transaksi