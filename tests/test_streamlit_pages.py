from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_all_streamlit_pages_render_without_exceptions():
    paths = [Path("app.py"), *sorted(Path("pages").glob("*.py"))]

    for path in paths:
        app = AppTest.from_file(str(path), default_timeout=30)
        app.run()

        assert not app.exception, f"{path} raised {app.exception}"
