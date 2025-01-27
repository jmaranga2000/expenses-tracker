from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required 
#from .models import  Expense
from .models import Category, Expense
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
#from userpreferences.models import UserPreferences
import datetime
import csv
import xlwt






#Create your views here.
'''@login_required(login_url='login')
def dashboard(request):
    user = request.user

    # Calculate total income and total expenses for the user
   
    total_expenses = Expense.objects.filter(user=user).aggregate(total=models.Sum('amount'))['total'] or 0

    # Calculate net balance
    net_balance = total_income - total_expenses

    # Retrieve income and expense categories for the user
    
    expense_categories = Expense.objects.filter(user=user).values('category').distinct()

    context = {
        
        'total_expenses': total_expenses,
        'net_balance': net_balance,
       
        'expense_categories': expense_categories,
    }

    return render(request, 'expenses/dashboard.html', context)'''
def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')

        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def index(request):
     # Fetch categories from DB
    categories = Category.objects.all()
    # Fetch expenses of the logged-in user from DB
    expenses = Expense.objects.filter(owner=request.user)
    # Paginate expenses for better user experience
    paginator = Paginator(expenses, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    #currency = UserPreferences.objects.get(user=request.user).currency
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        #'currency' : currency,
    }
    # Render the 'exp/index.html' template with the context
    return render(request, 'exp/index.html', context)


@login_required(login_url='/authentication/login')
def add_exp(request):
    categories = Category.objects.all()
    
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        
    
        return render(request, 'exp/add_exp.html',context)
    

    if request.method == 'POST':
        amount = request.POST.get('amount')

        if not amount:
            messages.warning(request, 'Amount is required')
            return render(request, 'exp/add_exp.html', context)

    
        description = request.POST.get('description')
        date = request.POST.get('expense_date')
        category = request.POST.get('category')

        if not description:
            messages.warning(request, 'Description is required')
            return render(request, 'exp/add_exp.html', context)

        Expense.objects.create(owner=request.user, amount=amount, date=date, category=category, description=description)

        messages.success(request, 'Expense saved successfully')

        return redirect('exp')


@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        
        return render(request, 'exp/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.warning(request, 'Amount is required')
            return render(request, 'exp/edit-expense.html', context)

        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.warning(request, 'Description is required')
            return render(request, 'exp/edit-expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description

        expense.save()

        messages.success(request, 'Expense Updated successfully')

        return redirect('exp')



def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)

    expense.delete()
     # Show success message
    messages.success(request, 'Expense Deleted successfully')
     # Redirect to expenses page
    return redirect('exp')


def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats_view(request):
    return render(request, 'exp/stats.html')


def export_csv(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.datetime.now())+'.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])

    expenses = Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])

    return response


def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.datetime.now())+'.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expense')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font_bold = True

    columns = ['Amount', 'Description', 'Category', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list('amount', 'description', 'category', 'date')

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num,col_num,str(row[col_num]), font_style)
    wb.save(response) 
    return response       



          


