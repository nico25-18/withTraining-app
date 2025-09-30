"""
WSGI config for withTrainningPj project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'withTrainningPj.settings')

application = get_wsgi_application()

# BASE_DIR = プロジェクトのルートディレクトリ
BASE_DIR = Path(__file__).resolve().parent.parent
# 正しい staticfiles パスを指定
application = WhiteNoise(application, root=os.path.join(BASE_DIR, 'staticfiles'))