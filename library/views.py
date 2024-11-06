from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, UpdateView
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from authentication.models import UserAccount
from .models import Book, Borrow, Review
from .forms import DepositForm

########## Home Page View ##########
class HomepageView(View):
    def get(self, request):
        context = {'data': Book.objects.all()}
        return render(request, 'library/homepage.html', context)


########## Book Detail View ##########
class BookDetailView(DetailView):
    model = Book
    pk_url_kwarg = 'id'
    template_name = 'library/book_detail.html'


########## User Profile View ##########
class UserProfileView(LoginRequiredMixin, View):
    template_name = 'library/user_profile.html'

    def get(self, request, *args, **kwargs):
        # Get user account details
        user_account = UserAccount.objects.get(user=request.user)

        # Get all borrows for the current user
        user_borrows = Borrow.objects.filter(username=request.user.username)

        # Prepare borrow records with all required information
        borrow_records = []
        for borrow in user_borrows:
            book = Book.objects.get(id=borrow.book_id)
            borrow_records.append({
                'borrow_id': borrow.id,
                'book_title': book.book_title,
                'book_borrowing_price': book.book_borrowing_price,
                'borrowing_on': borrow.borrowing_on
            })

        # Prepare context data
        context = {
            'user': request.user,
            'balance': user_account.balance,
            'borrow_records': borrow_records
        }

        return render(request, self.template_name, context)


########## Money Deposit View ##########
class DepositMoneyView(View):
    model = UserAccount
    form_class = DepositForm
    template_name = 'library/deposit_money.html'
    success_url = '/user_profile/'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['balance']
            user_account = self.model.objects.get(user=request.user)
            user_account.balance += amount
            user_account.save()
            messages.success(request, f'Successfully deposited {amount}')
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})


########## Borrowing Book View ##########
class BorrowingView(View):
    model = Borrow
    success_url = '/user_profile/'

    def get(self, request, *args, **kwargs):
        return redirect('library:homepage')

    def post(self, request, id, *args, **kwargs):
        # book_id = request.POST.get('book_id')
        print(id)
        book_id = id
        if book_id:
            book = Book.objects.get(id=book_id)
            user_account = UserAccount.objects.get(user=request.user)
            if user_account.balance >= book.book_borrowing_price:
                user_account.balance -= book.book_borrowing_price
                user_account.save()
                print('Borrowed')
                Borrow.objects.create(book_id=book.id, username=request.user.username)
                messages.success(request, 'Book borrowed successfully')
                return redirect(self.success_url)
            else:
                messages.warning(request, 'Insufficient balance to borrow this book')
                return redirect('library:book_detail', id=book_id)

        messages.error(request, 'Failed to borrow book')
        return redirect('library:homepage')
    