from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from collections import defaultdict
from .models import LotteryResult, Advertisement
from .forms import LotteryResultForm, AdvertisementForm
import datetime
import csv

def lottery_results(request):
    current_date = datetime.date.today()
    
    # Check if viewing full chart
    view_chart = request.GET.get('view_chart', 'false') == 'true'
    state_filter = request.GET.get('state', '')
    date_filter = request.GET.get('date', '')
    
    # Define the 8 main lottery states with times (sorted by time for display order)
    MAIN_STATES_WITH_TIME = [
        {'name': 'Disawar', 'time': '05:00 AM', 'sort_time': '05:00'},
        {'name': 'Dwarka City', 'time': '10:00 AM', 'sort_time': '10:00'},
        {'name': 'Ujjain King', 'time': '12:00 PM', 'sort_time': '12:00'},
        {'name': 'Delhi Bazar', 'time': '03:00 PM', 'sort_time': '15:00'},
        {'name': 'Shri Ganesh', 'time': '04:00 PM', 'sort_time': '16:00'},
        {'name': 'Faridabad', 'time': '06:15 PM', 'sort_time': '18:15'},
        {'name': 'Ghaziabad', 'time': '08:40 PM', 'sort_time': '20:40'},
        {'name': 'Gali', 'time': '11:30 PM', 'sort_time': '23:30'},
    ]
    
    # List of state names only (for table columns)
    MAIN_STATES = [state['name'] for state in MAIN_STATES_WITH_TIME]
    
    if view_chart:
        # Show full month chart
        month = int(request.GET.get('month', current_date.month))
        year = int(request.GET.get('year', current_date.year))
        
        # If specific date is selected, filter by that date
        if date_filter:
            try:
                filter_date = datetime.datetime.strptime(date_filter, '%Y-%m-%d').date()
                results = LotteryResult.objects.filter(date=filter_date)
            except ValueError:
                results = LotteryResult.objects.filter(date__month=month, date__year=year)
        else:
            results = LotteryResult.objects.filter(date__month=month, date__year=year)
        
        month_name = datetime.date(year, month, 1).strftime('%B')
    else:
        # Show only today's results
        results = LotteryResult.objects.filter(date=current_date)
        month = current_date.month
        year = current_date.year
        month_name = current_date.strftime('%B')
    
    # Apply state filter if provided
    if state_filter:
        results = results.filter(state__icontains=state_filter)
    
    # Create a time sorting map
    time_sort_map = {state['name']: state['sort_time'] for state in MAIN_STATES_WITH_TIME}
    
    # Group results by date and sort by time
    results_by_date = defaultdict(list)
    for result in results:
        results_by_date[result.date].append(result)
    
    # Sort each date's results by time
    for date in results_by_date:
        results_by_date[date].sort(key=lambda x: time_sort_map.get(x.state, '99:99'))
    
    # Sort by date descending
    sorted_results = sorted(results_by_date.items(), reverse=True)
    
    # Get current month's results for the main states table
    current_month = current_date.month
    current_year = current_date.year
    
    # Get all results for current month for the 8 main states
    month_results = LotteryResult.objects.filter(
        date__year=current_year,
        date__month=current_month,
        state__in=MAIN_STATES
    ).order_by('date')
    
    # Get all unique dates in current month that have results
    month_dates = LotteryResult.objects.filter(
        date__year=current_year,
        date__month=current_month,
        state__in=MAIN_STATES
    ).values_list('date', flat=True).distinct().order_by('date')
    
    # Create table rows with date and results for each state
    month_table_rows = []
    for date in month_dates:
        row = {
            'date': date,
            'is_today': date == current_date,
            'results': {}
        }
        
        # Get results for this date
        date_results = month_results.filter(date=date)
        
        # Fill in results for each state
        for state in MAIN_STATES:
            try:
                result = date_results.get(state=state)
                row['results'][state] = result.winning_number or 'WAIT'
            except LotteryResult.DoesNotExist:
                row['results'][state] = 'WAIT'
        
        month_table_rows.append(row)
    
    # Get all unique states for filter
    all_states = LotteryResult.objects.values_list('state', flat=True).distinct().order_by('state')
    
    # Get active advertisements
    advertisements = Advertisement.objects.filter(is_active=True)
    
    context = {
        'results_by_date': sorted_results,
        'month': month,
        'year': year,
        'month_name': month_name,
        'view_chart': view_chart,
        'state_filter': state_filter,
        'date_filter': date_filter,
        'all_states': all_states,
        'current_date': current_date,
        'advertisements': advertisements,
        'main_states': MAIN_STATES,
        'main_states_with_time': MAIN_STATES_WITH_TIME,
        'month_table_rows': month_table_rows,
    }
    return render(request, 'lottery/results.html', context)

@login_required
def admin_dashboard(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    state_filter = request.GET.get('state', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    page_number = request.GET.get('page', 1)
    
    # Base queryset
    results = LotteryResult.objects.all().order_by('-date', '-created_at')
    
    # Apply filters
    if search_query:
        results = results.filter(
            Q(state__icontains=search_query) | 
            Q(winning_number__icontains=search_query)
        )
    
    if state_filter:
        results = results.filter(state__iexact=state_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            results = results.filter(date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            results = results.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(results, 20)
    page_obj = paginator.get_page(page_number)
    
    # Get statistics
    total_results = LotteryResult.objects.count()
    total_states = LotteryResult.objects.values('state').distinct().count()
    latest_result = LotteryResult.objects.order_by('-date', '-created_at').first()
    today_results = LotteryResult.objects.filter(date=datetime.date.today()).count()
    
    # Get all unique states for filter dropdown
    all_states = LotteryResult.objects.values_list('state', flat=True).distinct().order_by('state')
    
    # Advertisements
    advertisements = Advertisement.objects.all().order_by('-created_at')[:10]
    
    context = {
        'page_obj': page_obj,
        'advertisements': advertisements,
        'total_results': total_results,
        'total_states': total_states,
        'latest_result': latest_result,
        'today_results': today_results,
        'all_states': all_states,
        'search_query': search_query,
        'state_filter': state_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'lottery/admin_dashboard.html', context)

@login_required
def add_result(request):
    if request.method == 'POST':
        form = LotteryResultForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lottery result added successfully!')
            return redirect('lottery:admin_dashboard')
    else:
        form = LotteryResultForm()
    return render(request, 'lottery/add_result.html', {'form': form})

@login_required
def edit_result(request, pk):
    result = get_object_or_404(LotteryResult, pk=pk)
    if request.method == 'POST':
        form = LotteryResultForm(request.POST, instance=result)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lottery result updated successfully!')
            return redirect('lottery:admin_dashboard')
    else:
        form = LotteryResultForm(instance=result)
    return render(request, 'lottery/edit_result.html', {'form': form, 'result': result})

@login_required
def delete_result(request, pk):
    result = get_object_or_404(LotteryResult, pk=pk)
    if request.method == 'POST':
        result.delete()
        messages.success(request, 'Lottery result deleted successfully!')
        return redirect('lottery:admin_dashboard')
    return render(request, 'lottery/delete_result.html', {'result': result})

@login_required
def add_advertisement(request):
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Advertisement added successfully!')
            return redirect('lottery:admin_dashboard')
    else:
        form = AdvertisementForm()
    return render(request, 'lottery/add_advertisement.html', {'form': form})

@login_required
def edit_advertisement(request, pk):
    ad = get_object_or_404(Advertisement, pk=pk)
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Advertisement updated successfully!')
            return redirect('lottery:admin_dashboard')
    else:
        form = AdvertisementForm(instance=ad)
    return render(request, 'lottery/edit_advertisement.html', {'form': form, 'ad': ad})

@login_required
def delete_advertisement(request, pk):
    ad = get_object_or_404(Advertisement, pk=pk)
    if request.method == 'POST':
        ad.delete()
        messages.success(request, 'Advertisement deleted successfully!')
        return redirect('lottery:admin_dashboard')
    return render(request, 'lottery/delete_advertisement.html', {'ad': ad})

@login_required
def bulk_delete_results(request):
    if request.method == 'POST':
        result_ids = request.POST.getlist('result_ids[]')
        if result_ids:
            deleted_count = LotteryResult.objects.filter(id__in=result_ids).delete()[0]
            messages.success(request, f'Successfully deleted {deleted_count} results!')
        else:
            messages.warning(request, 'No results selected for deletion.')
        return redirect('lottery:admin_dashboard')
    return redirect('lottery:admin_dashboard')

@login_required
def fetch_results(request):
    """Fetch today's results from satta-resultss.in (Delhi Bazar, Shri Ganesh, etc.)"""
    import requests
    from bs4 import BeautifulSoup
    import re
    
    url = "https://www.satta-resultss.in/index.php"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    today = datetime.date.today()
    
    state_mapping = {
        'DELHI BAZAR': 'Delhi Bazar',
        'SHRI GANESH': 'Shri Ganesh',
        'DISAWER': 'Disawar',
        'FARIDABAD': 'Faridabad',
        'GHAZIABAD': 'Ghaziabad',
        'GAZIYABAD': 'Ghaziabad',
        'GALI': 'Gali'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        added_count = 0
        updated_count = 0
        found_states = set()
        
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                
                for cell in cells:
                    text = cell.get_text(strip=True).upper()
                    
                    for key, state_name in state_mapping.items():
                        if key in text:
                            found_states.add(state_name)
                            
                            match = re.search(r'\{(\d+)\s*\}', text)
                            if match:
                                winning_number = match.group(1)
                            elif 'WAIT' in text:
                                winning_number = ''
                            else:
                                continue
                            
                            result, created = LotteryResult.objects.update_or_create(
                                date=today,
                                state=state_name,
                                defaults={'winning_number': winning_number}
                            )
                            
                            if created:
                                added_count += 1
                            else:
                                updated_count += 1
        
        # Add manual states with WAITING status (Dwarka City, Ujjain King)
        manual_states = ['Dwarka City', 'Ujjain King']
        for state_name in manual_states:
            result, created = LotteryResult.objects.update_or_create(
                date=today,
                state=state_name,
                defaults={'winning_number': ''}
            )
            if created:
                added_count += 1
            else:
                updated_count += 1
        
        if added_count > 0 or updated_count > 0:
            messages.success(request, f'Results fetched! Added: {added_count}, Updated: {updated_count}')
        else:
            messages.warning(request, 'No results found on satta-resultss.in')
            
    except requests.exceptions.Timeout:
        messages.error(request, 'Request timed out. Please try again.')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('lottery:admin_dashboard')

@login_required
def export_results_csv(request):
    # Get filter parameters
    state_filter = request.GET.get('state', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    results = LotteryResult.objects.all().order_by('-date')
    
    # Apply filters
    if state_filter:
        results = results.filter(state__iexact=state_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            results = results.filter(date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            results = results.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="lottery_results_{datetime.date.today()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Date', 'State', 'Winning Number', 'Created At', 'Updated At'])
    
    for result in results:
        writer.writerow([
            result.id,
            result.date.strftime('%Y-%m-%d'),
            result.state,
            result.winning_number,
            result.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            result.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    
    return response

def monthly_table(request):
    """Display current month's data in table format - only fetch_results.py states"""
    current_date = datetime.date.today()
    current_month = current_date.month
    current_year = current_date.year
    
    # Only show states from fetch_results.py configuration
    FETCH_STATES = [
        'Disawar',
        'Delhi Bazar', 
        'Shri Ganesh',
        'Faridabad',
        'Ghaziabad',
        'Gali',
        'Dwarka City',
        'Ujjain King'
    ]
    
    # Get results for current month - only for configured states
    results = LotteryResult.objects.filter(
        date__year=current_year,
        date__month=current_month,
        state__in=FETCH_STATES
    ).order_by('date', 'state')
    
    # Get all unique dates in current month
    dates = LotteryResult.objects.filter(
        date__year=current_year,
        date__month=current_month,
        state__in=FETCH_STATES
    ).values_list('date', flat=True).distinct().order_by('date')
    
    # Create table rows with date and results for each state
    table_rows = []
    for date in dates:
        row = {'date': date, 'is_today': date == current_date, 'results': {}}
        
        # Get results for this date
        date_results = results.filter(date=date)
        
        # Fill in results for each state
        for state in FETCH_STATES:
            try:
                result = date_results.get(state=state)
                row['results'][state] = result.winning_number or 'WAIT'
            except LotteryResult.DoesNotExist:
                row['results'][state] = 'WAIT'
        
        table_rows.append(row)
    
    month_name = current_date.strftime('%B')
    
    context = {
        'current_date': current_date,
        'month_name': month_name,
        'year': current_year,
        'states': FETCH_STATES,
        'table_rows': table_rows,
        'total_days': len(dates),
        'total_states': len(FETCH_STATES),
    }
    
    return render(request, 'lottery/monthly_table.html', context)
