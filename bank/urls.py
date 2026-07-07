from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('select-account-type/', views.select_account_type, name='select_account_type'),
    path('select-account/', views.select_account, name='select_account'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('transaction/', views.transaction, name='transaction'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
    path('cards/', views.cards, name='cards'),
    path('block-card/<int:card_id>/', views.block_card, name='block_card'),
    path('loans/', views.loans, name='loans'),
    path('bills/', views.bills, name='bills'),
    path('pay-bill/<int:bill_id>/', views.pay_bill, name='pay_bill'),
    path('support/', views.support, name='support'),
    path('logout/', views.logout, name='logout'),
]