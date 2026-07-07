from django import forms


class RegistrationForm(forms.Form):
    name = forms.CharField(
        label="Full Name",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )

    account_number = forms.CharField(
        label="Account Number",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )

    email = forms.EmailField(
        label="Email Address",
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )

    phone = forms.CharField(
        label="Phone Number",
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )


class LoginForm(forms.Form):
    account_number = forms.CharField(
        label="Account Number",
        max_length=20
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput()
    )


class TransactionForm(forms.Form):
    amount = forms.DecimalField(
        label="Amount",
        max_digits=10,
        decimal_places=2,
        min_value=1
    )