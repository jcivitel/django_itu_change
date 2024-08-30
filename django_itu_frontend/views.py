from celery.result import AsyncResult
from django.http import JsonResponse
from django.shortcuts import render

from .models import CountryUpdate
from .tasks import scrape_itu_data


def start_scraping(request):
    filter_date = request.GET.get('filter_date', '2023-01-01')
    print(f"Starting task with filter_date: {filter_date}")
    try:
        task = scrape_itu_data.delay(filter_date)
        print(f"Task started with ID: {task.id}")
        return JsonResponse({"task_id": task.id})
    except Exception as e:
        print(f"Error starting task: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


def get_progress(request):
    task_id = request.GET.get('task_id')
    print(f'Task ID: {task_id}')

    if not task_id:
        return JsonResponse({'error': 'Task ID is required'}, status=400)

    result = AsyncResult(task_id)


    if result.state == 'SUCCESS':
        return JsonResponse({
            'state': result.state,
            'total_updates': result.result,  # Assuming result.result contains the number of updates
            'countries': list(CountryUpdate.objects.values('country', 'update_date', 'link'))
        })
    elif result.state == 'FAILURE':
        # Handle task failure
        return JsonResponse({'state': result.state, 'error': str(result.result)}, status=500)
    elif result.state in ['PENDING', 'STARTED', 'RETRY']:
        # If the task is still running or pending
        return JsonResponse({'state': result.state})

    return JsonResponse({'state': 'PENDING'}, status=200)


def index(request):
    return render(request, 'index.html')
