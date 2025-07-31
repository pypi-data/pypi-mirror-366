# modal-hj3415

모달창을 띄우는 모듈.


1. 프로젝트의 settings.py 에 추가한다.
```python
INSTALLED_APPS = [
    'modal_hj3415',
]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

2. makemigration, migrate 실행

3. urls.py
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    ...
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

3. 사용 위치의 html에 작성한다.
```html
{% load modal_tags %}
...
{% show_modal %}
```