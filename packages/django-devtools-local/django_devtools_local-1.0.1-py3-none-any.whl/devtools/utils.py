import ast
import inspect
import traceback
from django.apps import apps
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import connection
from django.http import Http404


def is_debug_mode():
    """Check if application is in DEBUG mode"""
    return getattr(settings, 'DEBUG', False)


def is_authorized_ip(request):
    """Check if IP is authorized (localhost by default)"""
    allowed_ips = getattr(settings, 'DEVTOOLS_ALLOWED_IPS', ['127.0.0.1', '::1'])
    
    # Get client IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip in allowed_ips


def check_devtools_access(request):
    """Check access to devtools"""
    if not is_debug_mode():
        raise Http404("DevTools not available in production")
    
    if not request.user.is_authenticated or not request.user.is_superuser:
        raise Http404("Access denied")
    
    if not is_authorized_ip(request):
        raise Http404("IP not authorized")
    
    return True


def get_all_models():
    """Get all registered Django models"""
    models_data = []
    
    for app_config in apps.get_app_configs():
        app_models = []
        for model in app_config.get_models():
            model_info = {
                'name': model.__name__,
                'app_label': model._meta.app_label,
                'verbose_name': model._meta.verbose_name,
                'table_name': model._meta.db_table,
                'fields': [],
                'count': 0
            }
            
            # Get model fields
            for field in model._meta.get_fields():
                if hasattr(field, 'column'):
                    field_info = {
                        'name': field.name,
                        'type': field.__class__.__name__,
                        'null': getattr(field, 'null', False),
                        'blank': getattr(field, 'blank', False),
                        'verbose_name': getattr(field, 'verbose_name', field.name),
                    }
                    model_info['fields'].append(field_info)
            
            # Record count
            try:
                model_info['count'] = model.objects.count()
            except Exception:
                model_info['count'] = 'Error'
            
            app_models.append(model_info)
        
        if app_models:
            models_data.append({
                'app_name': app_config.name,
                'app_verbose_name': getattr(app_config, 'verbose_name', app_config.name),
                'models': app_models
            })
    
    return models_data


def get_model_data(app_label, model_name, limit=100, offset=0):
    """Get data from a specific model"""
    try:
        model = apps.get_model(app_label, model_name)
        
        # Get data with pagination
        queryset = model.objects.all()[offset:offset + limit]
        
        # Field information
        fields = []
        for field in model._meta.get_fields():
            if hasattr(field, 'column'):
                fields.append({
                    'name': field.name,
                    'verbose_name': getattr(field, 'verbose_name', field.name),
                    'type': field.__class__.__name__
                })
        
        # Convert data to dictionary
        data = []
        for obj in queryset:
            row = {}
            for field in fields:
                try:
                    value = getattr(obj, field['name'])
                    # Convert values for display
                    if value is None:
                        row[field['name']] = 'NULL'
                    elif hasattr(value, '__str__'):
                        row[field['name']] = str(value)
                    else:
                        row[field['name']] = repr(value)
                except Exception as e:
                    row[field['name']] = f'Error: {str(e)}'
            data.append(row)
        
        return {
            'model': model,
            'fields': fields,
            'data': data,
            'total_count': model.objects.count(),
            'current_offset': offset,
            'limit': limit
        }
    
    except Exception as e:
        return {
            'error': f'Error retrieving data: {str(e)}',
            'model': None,
            'fields': [],
            'data': [],
            'total_count': 0
        }


def execute_code(code, safe_globals=None):
    """Execute Python code safely"""
    if safe_globals is None:
        safe_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'dict': dict,
                'list': list,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'sorted': sorted,
                'reversed': reversed,
                'sum': sum,
                'max': max,
                'min': min,
                'abs': abs,
                'round': round,
            },
            'apps': apps,
            'connection': connection,
            'settings': settings,
        }
    
    # Import Django models
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            safe_globals[model.__name__] = model
    
    result = {
        'success': False,
        'output': '',
        'error': ''
    }
    
    try:
        # Syntax verification
        ast.parse(code)
        
        # Code execution
        import io
        import sys
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        
        try:
            exec(code, safe_globals)
            result['output'] = mystdout.getvalue()
            result['success'] = True
        finally:
            sys.stdout = old_stdout
            
    except SyntaxError as e:
        result['error'] = f'Syntax error: {str(e)}'
    except Exception as e:
        result['error'] = f'Execution error: {str(e)}\n{traceback.format_exc()}'
    
    return result


def execute_sql_query(query):
    """Execute raw SQL query"""
    result = {
        'success': False,
        'data': [],
        'columns': [],
        'error': '',
        'row_count': 0
    }
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            
            if cursor.description:
                # SELECT query
                result['columns'] = [col[0] for col in cursor.description]
                result['data'] = cursor.fetchall()
                result['row_count'] = len(result['data'])
            else:
                # INSERT/UPDATE/DELETE query
                result['row_count'] = cursor.rowcount
                result['data'] = []
                result['columns'] = []
            
            result['success'] = True
            
    except Exception as e:
        result['error'] = f'SQL error: {str(e)}'
    
    return result


def get_app_functions(app_name):
    """Get available functions in an app"""
    try:
        app_config = apps.get_app_config(app_name)
        module = __import__(f'{app_name}.utils', fromlist=[''])
        
        functions = []
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith('_'):
                sig = inspect.signature(obj)
                functions.append({
                    'name': name,
                    'signature': str(sig),
                    'doc': obj.__doc__ or 'No documentation'
                })
        
        return functions
    except ImportError:
        return []
    except Exception:
        return [] 