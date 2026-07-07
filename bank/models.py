from django.db import models
from django.utils import timezone


class Customer(models.Model):
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(default="user@sbi.com")
    phone = models.CharField(max_length=10, default="0000000000")
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Account(models.Model):
    ACCOUNT_TYPES = [
        ('savings', 'Savings Account'),
        ('current', 'Current Account'),
        ('personal', 'Personal Account'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='accounts')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=3.5)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.customer.name} - {self.account_type}"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('payment', 'Payment'),
    ]
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=200, default="Transaction")
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="completed")

    def __str__(self):
        return f"{self.account.customer.name} - {self.transaction_type}"


class Card(models.Model):
    CARD_TYPES = [
        ('debit', 'Debit Card'),
        ('credit', 'Credit Card'),
    ]
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='cards')
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=3)
    expiry_date = models.CharField(max_length=5)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card_type} - {self.card_number[-4:]}"


class Loan(models.Model):
    LOAN_TYPES = [
        ('personal', 'Personal Loan'),
        ('home', 'Home Loan'),
        ('auto', 'Auto Loan'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_emi = models.DecimalField(max_digits=10, decimal_places=2)
    tenure_months = models.IntegerField()
    status = models.CharField(max_length=20, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.loan_type}"


class BillPayment(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='bills')
    biller_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    paid_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.biller_name} - {self.account.customer.name}"