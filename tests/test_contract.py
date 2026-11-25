def test_package_imports():
    from scheduler.core import models
    assert models is not None
