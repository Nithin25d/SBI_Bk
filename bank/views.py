from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customer, Account, Transaction, Card, Loan, BillPayment
from .forms import LoginForm, TransactionForm, RegistrationForm
from decimal import Decimal


def home(request):
    return render(request, "home.html")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            account_number = form.cleaned_data['account_number']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            email = form.cleaned_data.get('email', 'user@sbi.com')
            phone = form.cleaned_data.get('phone', '0000000000')

            if password != confirm_password:
                return render(request, "register.html", {
                    'form': form,
                    'error': 'Passwords do not match'
                })

            if Customer.objects.filter(account_number=account_number).exists():
                return render(request, "register.html", {
                    'form': form,
                    'error': 'Account number already exists'
                })

            customer = Customer.objects.create(
                name=name,
                account_number=account_number,
                password=password,
                email=email,
                phone=phone
            )

            request.session['customer_id'] = customer.id
            return redirect('select_account_type')
    else:
        form = RegistrationForm()

    return render(request, "register.html", {'form': form})


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            account = form.cleaned_data['account_number']
            password = form.cleaned_data['password']

            try:
                customer = Customer.objects.get(
                    account_number=account,
                    password=password
                )

                request.session['customer_id'] = customer.id
                
                # Check if customer has accounts
                if customer.accounts.exists():
                    return redirect('select_account')
                else:
                    return redirect('select_account_type')

            except Customer.DoesNotExist:
                return render(request, "login.html", {
                    'form': form,
                    'error': 'Invalid Account Number or Password'
                })

    else:
        form = LoginForm()

    return render(request, "login.html", {'form': form})


def select_account_type(request):
    customer_id = request.session.get('customer_id')
    
    if not customer_id:
        return redirect('login')
    
    customer = Customer.objects.get(id=customer_id)

    if request.method == "POST":
        account_type = request.POST.get('account_type')
        
        if account_type in ['savings', 'current', 'personal']:
            account = Account.objects.create(
                customer=customer,
                account_type=account_type,
                account_number=f"{customer.id}{len(customer.accounts.all())+1}",
                balance=Decimal('0.00')
            )
            return redirect('select_account')
    
    return render(request, "select_account_type.html", {'customer': customer})


def select_account(request):
    customer_id = request.session.get('customer_id')
    
    if not customer_id:
        return redirect('login')
    
    customer = Customer.objects.get(id=customer_id)
    accounts = customer.accounts.filter(is_active=True)

    if request.method == "POST":
        account_id = request.POST.get('account_id')
        try:
            account = Account.objects.get(id=account_id, customer=customer)
            request.session['account_id'] = account.id
            return redirect('dashboard')
        except Account.DoesNotExist:
            pass

    return render(request, "select_account.html", {
        'customer': customer,
        'accounts': accounts
    })


def dashboard(request):
    customer_id = request.session.get('customer_id')
    account_id = request.session.get('account_id')

    if not customer_id or not account_id:
        return redirect('login')

    customer = Customer.objects.get(id=customer_id)
    account = Account.objects.get(id=account_id, customer=customer)
    transactions = account.transactions.all().order_by('-date')[:10]
    cards = account.cards.all()
    loans = customer.loans.all()
    bills = account.bills.all()

    return render(request, "dashboard.html", {
        'customer': customer,
        'account': account,
        'transactions': transactions,
        'cards': cards,
        'loans': loans,
        'bills': bills
    })


def transaction_history(request):
    customer_id = request.session.get('customer_id')
    account_id = request.session.get('account_id')

    if not customer_id or not account_id:
        return redirect('login')

    customer = Customer.objects.get(id=customer_id)
    account = Account.objects.get(id=account_id, customer=customer)
    transactions = account.transactions.all().order_by('-date')

    return render(request, "transaction_history.html", {
        'customer': customer,
        'account': account,
        'transactions': transactions
    })


def transaction(request):
    customer_id = request.session.get('customer_id')
    account_id = request.session.get('account_id')

    if not customer_id or not account_id:
        return redirect('login')

    customer = Customer.objects.get(id=customer_id)
    account = Account.objects.get(id=account_id, customer=customer)

    if request.method == "POST":
        form = TransactionForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']
            action = request.POST.get('action')

            if action == "deposit":
                account.balance += amount
                Transaction.objects.create(
                    account=account,
                    transaction_type="deposit",
                    amount=amount,
                    description="Received"
                )

            elif action == "withdraw":
                if account.balance >= amount:
                    account.balance -= amount
                    Transaction.objects.create(
                        account=account,
                        transaction_type="withdraw",
                        amount=amount,
                        description="Withdrawal"
                    )
                else:
                    return render(request, "transaction.html", {
                        'form': form,
                        'customer': customer,
                        'account': account,
                        'error': 'Insufficient balance'
                    })

            account.save()
            return redirect('dashboard')

    else:
        form = TransactionForm()

    return render(request, "transaction.html", {
        'form': form,
        'customer': customer,
        'account': account
    })


def cards(request):
    customer_id = request.session.get('customer_id')
    account_id = request.session.get('account_id')

    if not customer_id or not account_id:
        return redirect('login')

    customer = Customer.objects.get(id=customer_id)
    account = Account.objects.get(id=account_id, customer=customer)
    cards_list = account.cards.all()

    return render(request, "cards.html", {
        'customer': customer,
        'account': account,
        'cards_list': cards_list
    })


def block_card(request, card_id):
    customer_id = request.session.get('customer_id')
    account_id = request.session.get('account_id')

    if not customer_id or not account_id:
        return redirect('login')

    try:
        card = Card.objects.get(id=card_id, account__id=account_id)
        card.is_blocked = not card.is_blocked
        card.save()
        messages.success(request, 'Card status updated')
    except Card.DoesNotExist:
        messages.error(request, 'Card not found')

    return redirect('cards')


def loans(request):
    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('login')

    customer = Customer.objects.get(id=customer_id)
    loans_list = customer.loans.all()

    return render(request, "loans.html", {
        'customer': customer,
        'loans_list': loans_list
    })


def bills(request):
    customer_id = request.session.get('customer_id')
    account_id = request.session.get('account_id')

    if not customer_id or not account_id:
        return redirect('login')

    customer = Customer.objects.get(id=customer_id)
    account = Account.objects.get(id=account_id, customer=customer)
    bills_list = account.bills.all()

    return render(request, "bills.html", {
        'customer': customer,
        'account': account,
        'bills_list': bills_list
    })


def pay_bill(request, bill_id):
    customer_id = request.session.get('customer_id')
    account_id = request.session.get('account_id')

    if not customer_id or not account_id:
        return redirect('login')

    try:
        account = Account.objects.get(id=account_id)
        bill = BillPayment.objects.get(id=bill_id, account=account)
        
        if account.balance >= bill.amount:
            account.balance -= bill.amount
            account.save()
            bill.status = "paid"
            bill.save()
            messages.success(request, 'Bill paid successfully')
        else:
            messages.error(request, 'Insufficient balance')
    except (Account.DoesNotExist, BillPayment.DoesNotExist):
        messages.error(request, 'Bill not found')

    return redirect('bills')


def support(request):
    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('login')

    customer = Customer.objects.get(id=customer_id)

    return render(request, "support.html", {'customer': customer})


def logout(request):
    request.session.flush()
    return redirect('home')