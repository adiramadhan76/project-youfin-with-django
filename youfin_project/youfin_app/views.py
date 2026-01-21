from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user
from .models import Profile, Category, Budget, Transaction
from django.contrib.auth import update_session_auth_hash
from django.db.models import Sum
from django.utils import timezone
from calendar import month_name
from itertools import groupby
from datetime import datetime, timedelta
from django.utils.timezone import now
from datetime import date

# Create your views here.
# views front-end

# landing page
@unauthenticated_user
def index(request):
    return render(request, 'index.html')

# halaman login
@unauthenticated_user
def login_user(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        # Inisialisasi context untuk mengembalikan data form
        context = {
            'form_data': {
                'username': username_or_email,
            }
        }

        # Cari user berdasarkan username atau email
        user = User.objects.filter(email=username_or_email).first() or User.objects.filter(username=username_or_email).first()

        if user:
            # Cek apakah pengguna adalah superuser
            if user.is_superuser:
                messages.error(request, "Akses ditolak! Superuser (Admin) tidak dapat login ke website aplikasi.")
                return render(request, 'login/index.html')

            # Autentikasi pengguna
            user = authenticate(username=user.username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if user.last_name == "-":
                        messages.success(request, f"Login berhasil! Selamat datang, {user.first_name}, di YouFin.")
                    else:
                        messages.success(request, f"Login berhasil! Selamat datang, {user.first_name} {user.last_name}, di YouFin.")
                    return redirect('youfin_app:dashboard')
                else:
                    messages.error(request, "Akun Anda tidak aktif.")
            else:
                messages.error(request, "Password salah!")
        else:
            messages.error(request, "Username atau email tidak ditemukan!")

        return render(request, 'login/index.html', context)

    return render(request, 'login/index.html', {'form_data': {}})

# user logout
@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "Anda telah berhasil logout.")
    return HttpResponseRedirect(reverse('login'))

# halaman registrasi
@unauthenticated_user
def registration_user(request):
    if request.method == "POST":
        firstname = request.POST.get('firstname')  
        lastname = request.POST.get('lastname') 
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('konfirmasiPassword')

        # Menyusun context untuk mengirimkan data ke template jika terjadi kesalahan
        context = {
            'form_data': {
                'firstname': firstname,
                'lastname': lastname,
                'username': username,
                'email': email,
            }
        }

        # Validasi jika ada field yang kosong
        if not firstname:
            messages.error(request, "Nama depan tidak boleh kosong!")
        if not lastname:
            messages.error(request, "Nama belakang tidak boleh kosong!")
        if not username:
            messages.error(request, "Username tidak boleh kosong!")
        if not email:
            messages.error(request, "Email tidak boleh kosong!")
        if not password:
            messages.error(request, "Password tidak boleh kosong!")
        if not confirm_password:
            messages.error(request, "Konfirmasi password tidak boleh kosong!")

        # Validasi jika nama depan tidak diawali dengan huruf besar pada setiap kata
        if firstname and not all(word.istitle() for word in firstname.split()):
            messages.error(request, "Nama depan harus diawali dengan huruf besar pada setiap kata!")

        # Validasi nama belakang jika tidak berisi simbol "-" dan tidak diawali huruf besar
        if lastname != "-" and lastname and not all(word.istitle() for word in lastname.split()):
            messages.error(request, "Nama belakang harus diawali dengan huruf besar pada setiap kata!")

        # Jika ada error, kembalikan ke halaman registrasi dengan pesan error
        if not username or not email or not password or not confirm_password or not firstname or not lastname:
            return render(request, 'sign_up/index.html', context)

        # Validasi password dan konfirmasi password tidak cocok
        if password != confirm_password:
            messages.error(request, "Password dan konfirmasi password tidak cocok!")
            return render(request, 'sign_up/index.html', context)

        # Validasi username sudah terdaftar
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah digunakan!")
            return render(request, 'sign_up/index.html', context)

        # Validasi email sudah terdaftar
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email sudah terdaftar!")
            return render(request, 'sign_up/index.html', context)

        # Validasi password sesuai dengan aturan di AUTH_PASSWORD_VALIDATORS
        try:
            validate_password(password)  # Validasi dengan aturan Django
        except ValidationError as e:
            for error in e.messages:
                # Menambahkan pesan error kustom untuk password
                if "This password is too short" in error:
                    messages.error(request, "Password harus terdiri dari minimal 8 karakter!")
                elif "This password is too common" in error:
                    messages.error(request, "Password terlalu umum, coba gunakan kombinasi yang lebih kuat!")
                elif "This password is entirely numeric" in error:
                    messages.error(request, "Password tidak boleh hanya terdiri dari angka!")
                else:
                    messages.error(request, error)  # Pesan lainnya dari validasi default
            return render(request, 'sign_up/index.html', context)

        # Menangani nama belakang hanya tanda "-", itu berarti user hanya memiliki 1 kata didalam namanya
        if lastname == "-":
            lastname = "-"  

        # Membuat user baru dan mengenkripsi password
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = firstname  # Menyimpan nama depan
        user.last_name = lastname    # Menyimpan nama belakang
        user.save()

        messages.success(request, "Registrasi berhasil! Silakan login.")
        return redirect('login')

    # Menampilkan halaman registrasi awal dengan context kosong
    return render(request, 'sign_up/index.html', {'form_data': {}})


# views back-end

@login_required
def dashboard(request):
    # Ambil data transaksi pengguna
    transactions = Transaction.objects.filter(user=request.user)

    # Hitung total pemasukan, pengeluaran, dan saldo bersih
    total_pemasukan = transactions.filter(transaction_type='Pemasukan').aggregate(total=Sum('amount'))['total'] or 0
    total_pengeluaran = transactions.filter(transaction_type='Pengeluaran').aggregate(total=Sum('amount'))['total'] or 0
    saldo_bersih = total_pemasukan - total_pengeluaran

    # Data transaksi terbaru (5 transaksi terakhir)
    transaksi_terbaru = transactions.order_by('-date')[:5]

    # Data anggaran
    budgets = Budget.objects.filter(user=request.user).order_by('-id')

    # Ambil data pemasukan dan pengeluaran per bulan
    monthly_income = (
        transactions
        .filter(transaction_type='Pemasukan')
        .values('date__year', 'date__month')
        .annotate(total=Sum('amount'))
        .order_by('date__year', 'date__month')
    )

    monthly_expense = (
        transactions
        .filter(transaction_type='Pengeluaran')
        .values('date__year', 'date__month')
        .annotate(total=Sum('amount'))
        .order_by('date__year', 'date__month')
    )

    # Format data untuk Chart.js
    labels = [month_name[i] for i in range(1, 13)]  # Label bulan Januari-Desember
    income_data = [0] * 12
    expense_data = [0] * 12

    # Mengisi data pemasukan dan pengeluaran sesuai bulan
    for item in monthly_income:
        income_data[item['date__month'] - 1] = item['total']
    for item in monthly_expense:
        expense_data[item['date__month'] - 1] = item['total']

    # Context untuk template
    context = {
        'total_pemasukan': total_pemasukan,
        'total_pengeluaran': total_pengeluaran,
        'saldo_bersih': saldo_bersih,
        'transaksi_terbaru': transaksi_terbaru,
        'budgets': budgets,
        'labels': labels,
        'income_data': income_data,
        'expense_data': expense_data,
    }
    return render(request, 'page/dashboard/index.html', context)

# halaman anggaran
@login_required
def anggaran(request):
    # Ambil bulan dan tahun dari query parameter
    bulan = request.GET.get('bulan')
    tahun = request.GET.get('tahun')

    # Tambahkan beberapa tahun ke depan dan ke belakang
    current_year = timezone.now().year
    unique_years = list(range(current_year - 0, current_year + 2))  # Contoh: 2 tahun ke depan

    # Hitung total pemasukan pengguna berdasarkan bulan dan tahun
    if bulan and tahun:
        total_income = Transaction.objects.filter(
            user=request.user,
            transaction_type='Pemasukan',
            date__month=bulan,
            date__year=tahun
        ).aggregate(Sum('amount'))['amount__sum'] or 0
    else:
        total_income = 0

    # Hitung saldo bersih dari transaksi pengguna
    transactions = Transaction.objects.filter(user=request.user)
    total_pemasukan = transactions.filter(transaction_type='Pemasukan').aggregate(total=Sum('amount'))['total'] or 0
    total_pengeluaran = transactions.filter(transaction_type='Pengeluaran').aggregate(total=Sum('amount'))['total'] or 0
    saldo_bersih = total_pemasukan - total_pengeluaran

    # Ambil semua anggaran milik pengguna yang login
    all_budgets = Budget.objects.filter(user=request.user)

    # Filter anggaran berdasarkan bulan dan tahun jika parameter diterima
    if bulan:
        all_budgets = all_budgets.filter(bulan=bulan)
    if tahun:
        all_budgets = all_budgets.filter(tahun=tahun)

    # Urutkan data anggaran berdasarkan ID
    budgets = all_budgets.all()

    # for budget in budgets:
    #     # Pastikan perhitungan persentase dan sisa anggaran 
    #     if budget.initial_budget > 0:
    #         budget.spent_percentage = min((budget.total_expenses / budget.initial_budget) * 100, 100)
    #         budget.remaining_balance = max(budget.initial_budget - budget.total_expenses, 0)
    #     else:
    #         budget.spent_percentage = 0
    #         budget.remaining_balance = 0

    for budget in budgets:
        # budget.spent_percentage = budget.spent_percentage
        budget.remaining_balance = max(budget.initial_budget - budget.total_expenses, 0)

    # Perbarui data setiap anggaran saat halaman dimuat
    for budget in budgets:
        budget.update_budget()

    # Ambil semua kombinasi bulan dan tahun dari anggaran
    bulan_tahun_choices = Budget.objects.filter(user=request.user).values('bulan', 'tahun').distinct().order_by('bulan')

    # Gabungkan tahun-tahun untuk bulan yang sama
    bulan_tahun_map = {}
    for choice in bulan_tahun_choices:
        bulan = choice['bulan']
        tahun = choice['tahun']
        if bulan not in bulan_tahun_map:
            bulan_tahun_map[bulan] = []
        if tahun not in bulan_tahun_map[bulan]:
            bulan_tahun_map[bulan].append(tahun)

    # Ubah format bulan_tahun_choices untuk ditampilkan dengan beberapa tahun
    bulan_tahun_choices = [
        {
            'bulan': bulan,
            'nama_bulan': month_name[bulan],
            'tahun_list': bulan_tahun_map[bulan],
        }
        for bulan in sorted(bulan_tahun_map.keys())
    ]

    # Ambil tahun-tahun unik untuk dropdown tahun
    unique_years = sorted(set(year for choice in bulan_tahun_choices for year in choice['tahun_list']))

    # Tambahkan tahun baru jika belum ada
    if current_year not in unique_years:
        unique_years.append(current_year)

    # Kirimkan data ke template
    context = {
        'budgets': budgets,
        'total_income': total_income,
        'saldo_bersih': saldo_bersih,  # Tambahkan saldo bersih ke dalam context
        'bulan': bulan,
        'tahun': tahun,
        'bulan_tahun_choices': bulan_tahun_choices,
        'unique_years': unique_years,
        'current_year': current_year,
    }

    return render(request, 'page/anggaran/index.html', context)


# tambah anggaran
@login_required
def tambah_anggaran(request):
    # Ambil total pemasukan pengguna (hapus validasi jika pemasukan = 0)
    total_income = Transaction.objects.filter(
        user=request.user, transaction_type='Pemasukan'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # Ambil bulan dan tahun dari query parameter atau gunakan default bulan & tahun saat ini
    bulan = int(request.GET.get('bulan', now().month))
    tahun = int(request.GET.get('tahun', now().year))

    # Siapkan pilihan bulan (dalam bahasa Indonesia)
    bulan_choices = [(i, month_name[i]) for i in range(1, 13)]

    # Siapkan daftar tahun dari 2024 hingga 2 tahun ke depan
    current_year = datetime.now().year
    years = range(2024, current_year + 2)

    # Ambil kategori pengeluaran yang belum memiliki anggaran pada bulan dan tahun tertentu
    categories_with_budget = Budget.objects.filter(
        user=request.user, bulan=bulan, tahun=tahun
    ).values_list('category_id', flat=True)

    available_categories = Category.objects.filter(
        user=request.user,
        category_type='Pengeluaran'
    ).exclude(id__in=categories_with_budget)

    if request.method == 'POST':
        # Ambil input dari pengguna
        category_id = request.POST.get('category')
        initial_budget = request.POST.get('initial_budget')
        bulan = int(request.POST.get('bulan', bulan))  # Gunakan input bulan jika ada
        tahun = int(request.POST.get('tahun', tahun))  # Gunakan input tahun jika ada

        # Validasi: Cek apakah kategori valid
        if not category_id or not Category.objects.filter(id=category_id, user=request.user).exists():
            messages.error(request, 'Kategori tidak valid.')
            return redirect('youfin_app:tambah_anggaran')

        # Validasi: Pastikan anggaran untuk kategori, bulan, dan tahun tertentu belum ada
        if Budget.objects.filter(user=request.user, category_id=category_id, bulan=bulan, tahun=tahun).exists():
            messages.error(request, 'Anggaran untuk kategori ini sudah ada untuk bulan dan tahun ini.')
            return redirect('youfin_app:tambah_anggaran')

        # Simpan anggaran baru
        try:
            category = Category.objects.get(id=category_id)
            Budget.objects.create(
                user=request.user,
                category=category,
                initial_budget=initial_budget,
                bulan=bulan,
                tahun=tahun
            )
            messages.success(request, 'Anggaran berhasil ditambahkan!')
            return redirect('youfin_app:anggaran')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {e}')

    return render(request, 'page/anggaran/tambah.html', {
        'categories': available_categories,
        'bulan': bulan,
        'tahun': tahun,
        'bulan_choices': bulan_choices,
        'total_income': total_income,
        'years': years,
    })


# edit anggaran
@login_required
def edit_anggaran(request, budget_id):
    # Ambil anggaran yang ingin diubah
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)

    # Hitung saldo bersih pengguna
    transactions = Transaction.objects.filter(user=request.user)
    total_pemasukan = transactions.filter(transaction_type='Pemasukan').aggregate(total=Sum('amount'))['total'] or 0
    total_pengeluaran = transactions.filter(transaction_type='Pengeluaran').aggregate(total=Sum('amount'))['total'] or 0
    saldo_bersih = total_pemasukan - total_pengeluaran

    # Default initial_budget dari objek yang sudah ada
    initial_budget = budget.initial_budget  
    bulan = budget.bulan  # Ambil bulan dari objek jika sudah ada
    tahun = budget.tahun

    # Menyiapkan pilihan bulan dalam bahasa Indonesia
    bulan_choices = [(i, month_name[i]) for i in range(1, 13)]

    if request.method == 'POST':
        try:
            initial_budget = float(request.POST.get('initial_budget'))
            bulan = request.POST.get('bulan')
            tahun = request.POST.get('tahun')
        except ValueError:
            messages.error(request, 'Jumlah anggaran tidak valid.')
            return redirect('youfin_app:edit_anggaran', budget_id=budget.id)

        # Validasi input
        if initial_budget <= 0:
            messages.error(request, 'Jumlah anggaran harus lebih dari 0.')
            return redirect('youfin_app:edit_anggaran', budget_id=budget.id)

        # Validasi saldo bersih sebelum update
        if initial_budget > saldo_bersih:
            messages.error(request, 'Saldo tidak mencukupi untuk memperbarui anggaran.')
            return redirect('youfin_app:edit_anggaran', budget_id=budget.id)

        # Update anggaran
        budget.initial_budget = initial_budget
        budget.bulan = bulan
        budget.tahun = tahun
        budget.save()

        messages.success(request, 'Anggaran berhasil diperbarui!')
        return redirect('youfin_app:anggaran')

    return render(request, 'page/anggaran/edit.html', {
        'budget': budget,
        'bulan_choices': bulan_choices,
        # 'saldo_bersih': saldo_bersih,  # Kirim saldo bersih untuk validasi di template jika diperlukan
        'initial_budget': initial_budget,
        'bulan': bulan,
        'tahun': tahun,
    })


# Fungsi untuk menghapus anggaran
@login_required
def hapus_anggaran(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)

    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Anggaran berhasil dihapus.')
        return redirect('youfin_app:anggaran')

    return redirect('youfin_app:anggaran')


# halaman transaksi
@login_required
def transaksi(request):
    # Data bulan (1-12)
    bulan_list = range(1, 13)

    # Ambil parameter bulan dari query string
    bulan = request.GET.get('bulan')
    tahun = request.GET.get('tahun')

    # Ambil tahun unik dari transaksi
    years = Transaction.objects.values_list('date__year', flat=True).distinct()

    # Filter transaksi (bisa disesuaikan dengan logika lain)
    transactions = Transaction.objects.all()

    # Ambil waktu saat ini
    current_time = timezone.now()

    # Modifikasi query untuk transaksi terbaru
    transaksi_terbaru = Transaction.objects.filter(user=request.user).order_by('-date')[:5]

    # Ambil transaksi dan kategori yang terkait dengan user
    transactions = Transaction.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)

    # Filter berdasarkan bulan dan tahun (jika ada)
    if bulan and tahun:
        transactions = transactions.filter(date__month=bulan, date__year=tahun)

    # Hitung total pemasukan dan pengeluaran
    total_pemasukan = transactions.filter(transaction_type='Pemasukan').aggregate(total=Sum('amount'))['total'] or 0
    total_pengeluaran = transactions.filter(transaction_type='Pengeluaran').aggregate(total=Sum('amount'))['total'] or 0

    # Hitung saldo bersih
    saldo_bersih = total_pemasukan - total_pengeluaran

    # Kirim data ke template
    return render(request, 'page/transaksi/index.html', {
        'transactions': transactions,
        'transaksi_terbaru': transaksi_terbaru,
        'current_time': current_time,
        'categories': categories,
        'total_pemasukan': total_pemasukan,
        'total_pengeluaran': total_pengeluaran,
        'saldo_bersih': saldo_bersih,
        'bulan_list': bulan_list,
        'years' : years,
        'bulan': bulan,
        'tahun': tahun,
    })

# Fungsi untuk menambahkan transaksi
@login_required
def tambah_transaksi(request):
    # Ambil semua kategori milik user
    categories = Category.objects.filter(user=request.user)

    # Cek apakah pengguna memiliki kategori yang dapat digunakan untuk transaksi
    if not categories.exists():
        messages.error(request, 'Anda harus menambahkan kategori terlebih dahulu sebelum bisa menambah transaksi.')
        return redirect('youfin_app:transaksi')  # Arahkan pengguna ke halaman kategori

    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        date = request.POST.get('date')

        # Pastikan kategori ada dan milik user saat ini
        category = get_object_or_404(Category, id=category_id, user=request.user)

        # Jenis transaksi otomatis ditentukan berdasarkan kategori
        transaction_type = category.category_type  # Menggunakan field category_type

        # Menambahkan transaksi baru
        transaction = Transaction.objects.create(
            user=request.user,
            name=name,
            category=category,
            transaction_type=transaction_type,
            amount=amount,
            date=date
        )

        # Update total transaksi kategori (fungsi di model Category)
        category.update_total_transactions()

        messages.success(request, 'Transaksi berhasil ditambahkan.')
        return redirect('youfin_app:transaksi')

    return render(request, 'page/transaksi/tambah.html', {'categories': categories})

# Fungsi untuk mengedit transaksi
@login_required
def edit_transaksi(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)

    if request.method == 'POST':
        transaction.name = request.POST.get('name')
        transaction.category = get_object_or_404(Category, id=request.POST.get('category'), user=request.user)
        transaction.transaction_type = transaction.category.category_type  # Menggunakan category_type dari kategori yang dipilih
        transaction.amount = request.POST.get('amount')
        transaction.date = request.POST.get('date')

        transaction.save()
        transaction.category.update_total_transactions()  # Update total transaksi kategori

        messages.success(request, 'Transaksi berhasil diperbarui.')
        return redirect('youfin_app:transaksi')

    categories = Category.objects.filter(user=request.user)
    return render(request, 'page/transaksi/edit.html', {'transaction': transaction, 'categories': categories})

# Fungsi untuk menghapus transaksi
@login_required
def delete_transaksi(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)

    if request.method == 'POST':
        category = transaction.category
        transaction.delete()
        category.update_total_transactions()  # Update total transaksi kategori
        messages.success(request, 'Transaksi berhasil dihapus.')
        return redirect('youfin_app:transaksi')

    return redirect('youfin_app:transaksi')


# Halaman kategori
@login_required
def kategori(request):
    categories = Category.objects.filter(user=request.user)  # Ambil kategori milik user yang login
    
    # Memperbarui total transaksi untuk setiap kategori
    for category in categories:
        category.update_total_transactions()  # Memperbarui total transaksi kategori
    
    return render(request, 'page/kategori/index.html', {'categories': categories})

# Fungsi untuk menambah kategori
@login_required
def tambah_kategori(request):
    if request.method == 'POST':
        name = request.POST['name']
        category_type = request.POST['category_type']
        user = request.user
        
        # Validasi apakah kategori dengan nama yang sama sudah ada
        if Category.objects.filter(user=user, name=name).exists():
            messages.error(request, 'Kategori dengan nama tersebut sudah ada.')
            return render(request, 'page/kategori/tambah.html')  # Tampilkan form lagi jika ada duplikat
        
        # Membuat kategori baru jika tidak ada duplikat
        category = Category.objects.create(
            user=user,
            name=name,
            category_type=category_type
        )
        messages.success(request, 'Kategori berhasil ditambahkan!')
        return redirect('youfin_app:kategori')  # Redirect kembali ke halaman kategori
    
    return render(request, 'page/kategori/tambah.html')

# Fungsi untuk mengedit kategori
@login_required
def edit_kategori(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    
    if request.method == 'POST':
        name = request.POST['name']
        category_type = request.POST['category_type']
        
        # Validasi apakah kategori dengan nama yang sama sudah ada (kecuali kategori yang sedang diedit)
        if Category.objects.filter(user=request.user, name=name).exclude(id=category.id).exists():
            messages.error(request, 'Kategori dengan nama tersebut sudah ada.')
            return render(request, 'page/kategori/edit.html', {'category': category})  # Tampilkan form lagi jika ada duplikat
        
        # Update kategori jika tidak ada duplikat
        category.name = name
        category.category_type = category_type
        category.save()
        messages.success(request, 'Kategori berhasil diperbarui!')
        return redirect('youfin_app:kategori')  # Redirect kembali ke halaman kategori

    return render(request, 'page/kategori/edit.html', {'category': category})

# Fungsi untuk menghapus kategori
@login_required
def hapus_kategori(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    
    if request.method == 'POST':
        # Menghapus kategori
        category.delete()
        messages.success(request, 'Kategori berhasil dihapus!')
        return redirect('youfin_app:kategori')  # Redirect kembali ke halaman kategori
    
    # Jika bukan POST, maka tampilkan halaman konfirmasi
    return HttpResponseForbidden("Hanya dapat menghapus melalui metode POST.")


# @login_required
# def notifikasi(request):
#     return render(request, 'page/notifikasi/index.html')

# @login_required
# def premium(request):
#     return render(request, 'page/premium/index.html')

# @login_required
# def konsultasi(request):
#     return render(request, 'page/konsultasi/index.html')


# halaman tips
@login_required
def tips(request):
    return render(request, 'page/tips/index.html')


# halaman pengaturan profil
# pengaturan profile pengguna
@login_required
def pengaturan(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'page/pengaturan/index.html', {'profile': profile, 'user_status': 'premium' if request.user.groups.filter(name='Premium').exists() else 'standar'})

# Tambahkan fungsi validasi untuk memeriksa ekstensi gambar
def is_valid_image(file):
    # Daftar ekstensi gambar yang diperbolehkan
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    # Periksa apakah file memiliki ekstensi yang valid
    if any(file.name.endswith(ext) for ext in allowed_extensions):
        return True
    return False

# halaman edit pengaturan profil
@login_required
def edit_pengaturan(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Ambil data dari form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        profile_picture = request.FILES.get('profile_picture')

        # Validasi jika ada field yang kosong
        if not first_name:
            messages.error(request, "Nama depan tidak boleh kosong!")
        if not last_name:
            messages.error(request, "Nama belakang tidak boleh kosong!")
        if not username:
            messages.error(request, "Username tidak boleh kosong!")
        if not email:
            messages.error(request, "Email tidak boleh kosong!")
        if not phone_number:
            messages.error(request, "Nomor telepon tidak boleh kosong!")
        if not address:
            messages.error(request, "Alamat tidak boleh kosong!")
        if not birth_date:
            messages.error(request, "Tanggal lahir tidak boleh kosong!")
        if not gender:
            messages.error(request, "Jenis kelamin tidak boleh kosong!")
        # Validasi gender
        elif gender not in ['L', 'P']:
            messages.error(request, "Jenis kelamin tidak valid!")

        # Validasi jika nama depan tidak diawali dengan huruf besar pada setiap kata
        if first_name and not all(word.istitle() for word in first_name.split()):
            messages.error(request, "Nama depan harus diawali dengan huruf besar pada setiap kata!")

        # Validasi nama belakang jika tidak berisi simbol "-" dan tidak diawali huruf besar
        if last_name != "-" and last_name and not all(word.istitle() for word in last_name.split()):
            messages.error(request, "Nama belakang harus diawali dengan huruf besar pada setiap kata!")

        # Validasi username sudah terdaftar oleh user lain
        if User.objects.filter(username=username).exclude(pk=request.user.pk).exists():
            messages.error(request, "Username sudah digunakan oleh pengguna lain!")

        # Validasi email sudah terdaftar oleh user lain
        if User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
            messages.error(request, "Email sudah digunakan oleh pengguna lain!")

        # Validasi format nomor telepon (opsional, contoh validasi panjang minimal)
        if phone_number and not phone_number.isdigit():
            messages.error(request, "Nomor telepon harus berupa angka!")
        elif phone_number and len(phone_number) < 10:
            messages.error(request, "Nomor telepon harus terdiri dari minimal 10 digit!")

        # Validasi dan set tanggal lahir
        if birth_date:
            try:
                profile.birth_date = birth_date
            except ValueError:
                messages.error(request, "Tanggal lahir tidak valid.")

        # Validasi format gambar jika ada yang diunggah
        if profile_picture and not is_valid_image(profile_picture):
            messages.error(request, "Format gambar tidak valid. Harap unggah gambar dengan ekstensi .jpg, .jpeg, atau .png!")

        # Jika ada error, kembali ke halaman edit pengaturan
        if messages.get_messages(request):
            return render(request, 'page/pengaturan/edit.html', {'profile': profile})

        # Update User fields
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.username = username
        request.user.email = email
        request.user.save()

        # Update Profile fields
        profile.phone_number = phone_number
        profile.address = address
        profile.gender = gender

        # Hapus foto profil jika checkbox 'clear_picture' dicentang
        if 'clear_picture' in request.POST:
            profile.delete_profile_picture()

        # Ganti foto profil jika user mengunggah yang baru
        elif profile_picture:
            # Hapus foto profil lama dari path dan database
            if profile.profile_picture:
                profile.profile_picture.delete(save=False)
            profile.profile_picture = profile_picture

        # Simpan perubahan pada profil
        profile.save()
        messages.success(request, "Data profil berhasil diperbarui!")
        return redirect('youfin_app:pengaturan')

    return render(request, 'page/pengaturan/edit.html', {'profile': profile})

# modal untuk ubah password pada halaman edit pengaturan profil
@login_required
def ubah_password(request):
    if request.method == 'POST':
        # Ambil input dari form
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validasi inputan kosong
        if not current_password:
            messages.error(request, "Password lama tidak boleh kosong!")
        if not new_password:
            messages.error(request, "Password baru tidak boleh kosong!")
        if not confirm_password:
            messages.error(request, "Konfirmasi password baru tidak boleh kosong!")

        # Periksa apakah password baru sama dengan konfirmasinya
        if new_password and confirm_password and new_password != confirm_password:
            messages.error(request, "Password baru dan konfirmasi tidak cocok!")

        # Periksa validitas password lama
        if current_password and not request.user.check_password(current_password):
            messages.error(request, "Password lama yang dimasukkan salah!")

        # Validasi password baru sesuai dengan aturan di AUTH_PASSWORD_VALIDATORS
        try:
            if new_password:
                validate_password(new_password)  # Validasi password dengan aturan Django
        except ValidationError as e:
            for error in e.messages:
                if "This password is too short" in error:
                    messages.error(request, "Password harus terdiri dari minimal 8 karakter!")
                elif "This password is too common" in error:
                    messages.error(request, "Password terlalu umum, coba gunakan kombinasi yang lebih kuat!")
                elif "This password is entirely numeric" in error:
                    messages.error(request, "Password tidak boleh hanya terdiri dari angka!")
                else:
                    messages.error(request, error)  # Pesan lainnya dari validasi default

        # Jika ada error, tampilkan halaman kembali tanpa mengubah password
        if messages.get_messages(request):
            return redirect('youfin_app:edit_pengaturan')

        # Jika semua validasi lulus, lanjutkan untuk ubah password
        try:
            request.user.set_password(new_password)
            request.user.save()

            # Memastikan sesi tetap aktif setelah mengubah password
            update_session_auth_hash(request, request.user)

            messages.success(request, "Password berhasil diperbarui! Silahkan logout dan login kembali menggunakan password baru Anda.")
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan saat mengubah password: {str(e)}")

        return redirect('youfin_app:edit_pengaturan')

    # Jika bukan POST, langsung kembali ke halaman edit_pengaturan
    return redirect('youfin_app:edit_pengaturan')



