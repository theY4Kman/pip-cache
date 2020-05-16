import pytest

import pip_cache


@pytest.mark.benchmark(
    group='pkgnames',
)
@pytest.mark.parametrize('prefix', [
    pytest.param('', id='<all>'),
    '0',
    'i',
    'ipy',
])
def test_pkgnames_speed(benchmark, prefix):
    benchmark(pip_cache.pkgnames, prefix)
