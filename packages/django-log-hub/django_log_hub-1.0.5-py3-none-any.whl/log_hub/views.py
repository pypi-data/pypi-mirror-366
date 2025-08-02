from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseNotFound, HttpResponseBadRequest, FileResponse, Http404, JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils.translation import gettext as _, activate
from django.utils import translation
from datetime import datetime
import os
import json
import logging

# Constants
DEFAULT_LOG_LIMIT = 50
MAX_LOG_LIMIT = 1000
SUPPORTED_LOG_LEVELS = ['INFO', 'WARNING', 'ERROR', 'DEBUG', 'CRITICAL']

logger = logging.getLogger(__name__)


def change_language(request):
    """
    Dil değiştirme view'ı
    """
    lang = request.GET.get('lang', 'en')
    if lang in ['tr', 'en']:
        # Django versiyonuna göre session key'i ayarla
        if hasattr(translation, 'LANGUAGE_SESSION_KEY'):
            request.session[translation.LANGUAGE_SESSION_KEY] = lang
        else:
            # Eski Django versiyonları için
            request.session['django_language'] = lang
        # Dil değişikliğini aktifleştir
        translation.activate(lang)
    return redirect('log_hub:log_view')


def parse_log_line(line):
    """
    Log satırını JSON formatından parse eder
    """
    try:
        log_data = json.loads(line)
        level = log_data.get("levelname", "UNKNOWN")
        exc_info = log_data.get("exc_info", "")
        info = exc_info.split("\n") if exc_info else []

        # Tarihi milisaniyeye kadar dönüştürür
        asctime_str = log_data.get("asctime", "")
        asctime = datetime.strptime(asctime_str, "%Y-%m-%d %H:%M:%S,%f")

        return {
            "level": level,
            "name": log_data.get("name", ""),
            "asctime": asctime,
            "timestamp": asctime_str,
            "message": log_data.get("message", ""),
            "status_code": log_data.get("status_code", ""),
            "task_name": log_data.get("taskName", ""),
            "request": log_data.get("request", ""),
            "info": info,
            "raw": line,
        }
    except json.JSONDecodeError as e:
        return {
            "level": "ERROR",
            "timestamp": "",
            "message": "Invalid JSON format",
            "status_code": "",
            "task_name": "",
            "request": "",
            "raw": line,
        }


@login_required
@user_passes_test(lambda u: u.is_staff)
def log_view(request):
    """
    Log dosyalarını görüntülemek için view
    """
    try:
        # Log dizinini al (settings'den veya varsayılan)
        log_dir = getattr(settings, 'LOG_HUB_LOG_DIR', os.path.join(settings.BASE_DIR, 'logs'))
        
        # Log dizini kontrolü
        if not os.path.exists(log_dir):
            template_name = getattr(settings, 'LOG_HUB_TEMPLATE', 'log_hub/logging.html')
            return render(request, template_name, {
                "hata": _("Log directory not found: %(dir)s") % {"dir": log_dir},
                'log_count': 0,
                'logs': [],
                'log_files': [],
                'selected_log_type': None,
                'search_query': '',
                'log_level': '',
                'start_date': '',
                'end_date': '',
                'limit': DEFAULT_LOG_LIMIT,
                'status_code': '',
                'exclude': '',
                'LANGUAGE_CODE': translation.get_language(),
            })
        
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]  # .log dosyalarını bul
        
        # Log dosyası yoksa
        if not log_files:
            template_name = getattr(settings, 'LOG_HUB_TEMPLATE', 'log_hub/logging.html')
            return render(request, template_name, {
                "hata": _("No .log files found in directory: %(dir)s") % {"dir": log_dir},
                'log_count': 0,
                'logs': [],
                'log_files': [],
                'selected_log_type': None,
                'search_query': '',
                'log_level': '',
                'start_date': '',
                'end_date': '',
                'limit': DEFAULT_LOG_LIMIT,
                'status_code': '',
                'exclude': '',
                'LANGUAGE_CODE': translation.get_language(),
            })
        
        log_type = request.GET.get('log_type', log_files[0] if log_files else None)  # Seçilen log dosyası
        search_query = request.GET.get('q', '')  # Arama kelimesi
        log_level = request.GET.get('level', '')  # Log seviyesi (INFO, ERROR, WARNING)
        limit = int(request.GET.get('limit', DEFAULT_LOG_LIMIT))  # Gösterilecek log sayısı
        limit = min(limit, MAX_LOG_LIMIT)  # Maksimum limit kontrolü
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        status_code = request.GET.get('status_code', '') # status koduna göre listele
        exclude = request.GET.get('exclude', '') # Listelerken hariç tutulacak log satırları(anahtar kelimeler)

        if log_type and log_type in log_files:
            log_file_path = os.path.join(log_dir, log_type)
        else:
            template_name = getattr(settings, 'LOG_HUB_TEMPLATE', 'log_hub/logging.html')
            return render(request, template_name, {
                "hata": _("Selected log file not found: %(file)s") % {"file": log_type},
                'log_count': 0,
                'logs': [],
                'log_files': log_files,
                'selected_log_type': log_files[0] if log_files else None,
                'search_query': search_query,
                'log_level': log_level,
                'start_date': start_date,
                'end_date': end_date,
                'limit': limit,
                'status_code': status_code,
                'exclude': exclude,
                'LANGUAGE_CODE': translation.get_language(),
            })
        
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%dT%H:%M") if start_date else None
            end_datetime = datetime.strptime(end_date, "%Y-%m-%dT%H:%M") if end_date else None
        except ValueError:
            template_name = getattr(settings, 'LOG_HUB_TEMPLATE', 'log_hub/logging.html')
            return render(request, template_name, {
                "hata": _("Invalid date format. Please use 'YYYY-MM-DDTHH:MM' format."),
                'log_count': 0,
                'logs': [],
                'log_files': log_files,
                'selected_log_type': log_type,
                'search_query': search_query,
                'log_level': log_level,
                'start_date': start_date,
                'end_date': end_date,
                'limit': limit,
                'status_code': status_code,
                'exclude': exclude,
                'LANGUAGE_CODE': translation.get_language(),
            })

        logs = []
        hata = None
        try:
            with open(log_file_path, 'r', encoding='utf-8') as file:
                exclude_keywords = [kelime.strip().lower() for kelime in exclude.split(",") if kelime.strip()]
                s = 0
                
                # Dosyayı sondan başlayarak oku (son logları göster)
                lines = file.readlines()
                for line in reversed(lines):  # Sondan başla
                    log_data = parse_log_line(line)
                    
                    # Filtreleme
                    if exclude and any(kelime in line.lower() for kelime in exclude_keywords):
                        continue
                    if status_code and str(status_code) != str(log_data["status_code"]):
                        continue
                    if log_level and log_level != log_data["level"]:
                        continue
                    if search_query and search_query.lower() not in log_data["raw"].lower():
                        continue
                    if start_datetime and log_data["asctime"] and log_data["asctime"] < start_datetime:
                        continue
                    if end_datetime and log_data["asctime"] and log_data["asctime"] > end_datetime:
                        continue
                    
                    logs.append(log_data)
                    s += 1
                    if s >= int(limit):
                        break
        except UnicodeDecodeError as e:
            hata = _("Log file encoding error: %(error)s. File must be in UTF-8 format.") % {"error": str(e)}
        except PermissionError as e:
            hata = _("No permission to access log file: %(error)s") % {"error": str(e)}
        except Exception as e:
            hata = _("Error reading log file: %(error)s") % {"error": str(e)}

        # Template path'ini settings'den al veya varsayılan kullan
        template_name = getattr(settings, 'LOG_HUB_TEMPLATE', 'log_hub/logging.html')

        return render(request, template_name, {
            "hata": hata,
            'log_count': len(logs),
            'logs': logs,
            'log_files': log_files,
            'selected_log_type': log_type,
            'search_query': search_query,
            'log_level': log_level,
            'start_date': start_date,
            'end_date': end_date,
            'limit': limit,
            'status_code': status_code,
            'exclude': exclude,
            'LANGUAGE_CODE': translation.get_language(),
        })
    except Exception as e:
        template_name = getattr(settings, 'LOG_HUB_TEMPLATE', 'log_hub/logging.html')
        return render(request, template_name, {
            "hata": _("An unexpected error occurred: %(error)s") % {"error": str(e)},
            'log_count': 0,
            'logs': [],
            'log_files': [],
            'selected_log_type': None,
            'search_query': '',
            'log_level': '',
            'start_date': '',
            'end_date': '',
            'limit': DEFAULT_LOG_LIMIT,
            'status_code': '',
            'exclude': '',
            'LANGUAGE_CODE': translation.get_language(),
        })


@staff_member_required
@require_http_methods(["POST"])
def clear_log(request, log_file_name):
    """
    Log dosyasını temizlemek için view
    """
    # Güvenlik: Dosya adı doğrulaması
    if not log_file_name or not log_file_name.endswith('.log') or '..' in log_file_name or '/' in log_file_name:
        return JsonResponse({"status": "error", "message": _("Invalid log file name")}, status=400)
    
    log_dir = getattr(settings, 'LOG_HUB_LOG_DIR', os.path.join(settings.BASE_DIR, 'logs'))
    log_file_path = os.path.join(log_dir, log_file_name)
    
    # Güvenlik: Path traversal kontrolü
    if not os.path.abspath(log_file_path).startswith(os.path.abspath(log_dir)):
        return JsonResponse({"status": "error", "message": _("Access denied")}, status=403)

    if not os.path.exists(log_file_path):
        raise Http404(_("Specified log file not found."))
    
    try:
        with open(log_file_path, 'w'):
            pass  # Dosya içeriğini temizle

        return JsonResponse({"status": "success", "message": _("'%(file)s' successfully cleared.") % {"file": log_file_name}})
    except Exception as e:
        return JsonResponse({"status": "error", "message": _("Error clearing file: %(error)s") % {"error": str(e)}}, status=500)


@staff_member_required
def download_log(request, log_file_name):
    """
    Log dosyasını indirmek için view
    """
    # Güvenlik: Dosya adı doğrulaması
    if not log_file_name or not log_file_name.endswith('.log') or '..' in log_file_name or '/' in log_file_name:
        raise Http404(_("Invalid log file name"))
    
    log_dir = getattr(settings, 'LOG_HUB_LOG_DIR', os.path.join(settings.BASE_DIR, 'logs'))
    log_file_path = os.path.join(log_dir, log_file_name)
    
    # Güvenlik: Path traversal kontrolü
    if not os.path.abspath(log_file_path).startswith(os.path.abspath(log_dir)):
        raise Http404(_("Access denied"))

    if not os.path.exists(log_file_path):
        raise Http404(_("Selected log file not found."))

    return FileResponse(open(log_file_path, 'rb'), as_attachment=True, filename=log_file_name)
