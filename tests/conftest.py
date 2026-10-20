import os, pytest

ROM = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rom', 'Dolucky no A.League Soccer (Japan).sfc')


def pytest_collection_modifyitems(items):
    # every test here reads the original ROM; a public checkout has none
    if not os.path.exists(ROM):
        for it in items:
            it.add_marker(pytest.mark.skip(reason='no ROM in rom/ (see README)'))
