'''from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Income, Expense
# Create your views here.
# tracker/views.py



@login_required(login_url='login')
def dashboard(request):
    user = request.user

    # Calculate total income and total expenses for the user
    total_income = Income.objects.filter(user=user).aggregate(total=models.Sum('amount'))['total'] or 0
    total_expenses = Expense.objects.filter(user=user).aggregate(total=models.Sum('amount'))['total'] or 0

    # Calculate net balance
    net_balance = total_income - total_expenses

    # Retrieve income and expense categories for the user
    income_categories = Income.objects.filter(user=user).values('category').distinct()
    expense_categories = Expense.objects.filter(user=user).values('category').distinct()

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': net_balance,
        'income_categories': income_categories,
        'expense_categories': expense_categories,
    }

    return render(request, 'tracker/dashboard.html', context)'''
'''# tracker/views.py
@login_required(login_url='login')
def dashboard(request):
    user = request.user

    # Calculate total income and total expenses for the user
    total_income = Income.objects.filter(user=user).aggregate(total=models.Sum('amount'))['total'] or 0
    total_expenses = Expense.objects.filter(user=user).aggregate(total=models.Sum('amount'))['total'] or 0

    # Calculate net balance
    net_balance = total_income - total_expenses

    # Retrieve income and expense categories for the user
    income_categories = Income.objects.filter(user=user).values('category').distinct()
    expense_categories = Expense.objects.filter(user=user).values('category').distinct()

    # Retrieve recent transactions for the user
    recent_transactions = Expense.objects.filter(user=user).order_by('-date')[:5]

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': net_balance,
        'income_categories': income_categories,
        'expense_categories': expense_categories,
        'transactions': recent_transactions,
    }

    return render(request, 'tracker/dashboard.html', context)
'''