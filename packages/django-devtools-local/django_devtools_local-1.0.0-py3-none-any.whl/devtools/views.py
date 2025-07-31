from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json

from .utils import (
    check_devtools_access, 
    get_all_models, 
    get_model_data, 
    execute_code, 
    execute_sql_query,
    get_app_functions
)


class DevToolsBaseMixin:
    """Base mixin to check DevTools access"""
    
    def dispatch(self, request, *args, **kwargs):
        try:
            check_devtools_access(request)
        except Http404 as e:
            raise e
        return super().dispatch(request, *args, **kwargs)


class IndexView(DevToolsBaseMixin, View):
    """DevTools home page"""
    
    def get(self, request):
        models_data = get_all_models()
        context = {
            'models_data': models_data,
            'total_apps': len(models_data),
            'total_models': sum(len(app['models']) for app in models_data)
        }
        return render(request, 'devtools/index.html', context)


class TablesView(DevToolsBaseMixin, View):
    """View to display table data"""
    
    def get(self, request):
        app_label = request.GET.get('app')
        model_name = request.GET.get('model')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 50))
        
        if not app_label or not model_name:
            return render(request, 'devtools/tables.html', {
                'error': 'App and model parameters required'
            })
        
        offset = (page - 1) * limit
        result = get_model_data(app_label, model_name, limit, offset)
        
        if 'error' in result:
            context = {'error': result['error']}
        else:
            # Pagination
            total_pages = (result['total_count'] + limit - 1) // limit
            
            context = {
                'app_label': app_label,
                'model_name': model_name,
                'model': result['model'],
                'fields': result['fields'],
                'data': result['data'],
                'current_page': page,
                'total_pages': total_pages,
                'total_count': result['total_count'],
                'limit': limit,
                'has_previous': page > 1,
                'has_next': page < total_pages,
                'previous_page': page - 1 if page > 1 else None,
                'next_page': page + 1 if page < total_pages else None,
            }
        
        return render(request, 'devtools/tables.html', context)


class QueryView(DevToolsBaseMixin, View):
    """View to execute queries and code"""
    
    def get(self, request):
        return render(request, 'devtools/query.html')
    
    @csrf_exempt
    def post(self, request):
        try:
            data = json.loads(request.body)
            query_type = data.get('type')
            code = data.get('code', '').strip()
            
            if not code:
                return JsonResponse({
                    'success': False,
                    'error': 'Empty code'
                })
            
            if query_type == 'python':
                result = execute_code(code)
            elif query_type == 'sql':
                result = execute_sql_query(code)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Unsupported query type'
                })
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error: {str(e)}'
            })


class ModelsAPIView(DevToolsBaseMixin, View):
    """API to get models list"""
    
    def get(self, request):
        models_data = get_all_models()
        return JsonResponse({
            'success': True,
            'data': models_data
        })


class ModelDataAPIView(DevToolsBaseMixin, View):
    """API to get model data"""
    
    def get(self, request, app_label, model_name):
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        
        result = get_model_data(app_label, model_name, limit, offset)
        
        if 'error' in result:
            return JsonResponse({
                'success': False,
                'error': result['error']
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'fields': result['fields'],
                'rows': result['data'],
                'total_count': result['total_count'],
                'limit': limit,
                'offset': offset
            }
        })


class FunctionsView(DevToolsBaseMixin, View):
    """View to test app functions"""
    
    def get(self, request):
        app_name = request.GET.get('app')
        context = {'app_name': app_name}
        
        if app_name:
            functions = get_app_functions(app_name)
            context['functions'] = functions
        
        return render(request, 'devtools/functions.html', context)


# Decorators for function-based views
def devtools_required(view_func):
    """Decorator to check devtools access"""
    def wrapper(request, *args, **kwargs):
        check_devtools_access(request)
        return view_func(request, *args, **kwargs)
    return wrapper


@devtools_required
def database_schema_view(request):
    """View to display database schema"""
    from django.db import connection
    
    tables_info = []
    
    with connection.cursor() as cursor:
        # Get tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            # Get columns for each table
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default, extra
                FROM information_schema.columns 
                WHERE table_name = %s AND table_schema = DATABASE()
                ORDER BY ordinal_position
            """, [table])
            
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'nullable': row[2] == 'YES',
                    'default': row[3],
                    'extra': row[4]
                })
            
            tables_info.append({
                'name': table,
                'columns': columns
            })
    
    return render(request, 'devtools/schema.html', {
        'tables': tables_info
    }) 