import os
import sys

import pytest
from _pytest.monkeypatch import MonkeyPatch

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
PKG_DIR = os.path.dirname(TESTS_DIR)

sys.path.insert(0, PKG_DIR)


CACHE_KEY = 'pip-cache/is-cache-built'


@pytest.fixture(scope='session')
def pip_cache_dir(request):
    path = request.config.cache.makedir('pip-cache-data')

    with MonkeyPatch().context() as patch:
        patch.setattr('pip_cache.get_pip_cache_data_dir', lambda: path)
        yield path


@pytest.fixture(scope='session', autouse=True)
def _build_package_cache(request, pip_cache_dir):
    import pip_cache

    if not request.config.cache.get(CACHE_KEY, None):
        pip_cache.update_package_list()
        request.config.cache.set(CACHE_KEY, True)
