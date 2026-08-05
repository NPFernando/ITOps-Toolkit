from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import github_issues


# Newer streamlit resolves AppTest.from_file()'s relative paths against the
# file that calls it (this test file's directory), not the working
# directory -- build absolute paths from the project root instead.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_all_streamlit_pages_render_without_exceptions(monkeypatch):
    monkeypatch.setattr(
        github_issues,
        "fetch_public_issues",
        lambda *args, **kwargs: github_issues.GitHubIssuesResult(()),
    )
    paths = [PROJECT_ROOT / "app.py", *sorted((PROJECT_ROOT / "pages").glob("*.py"))]

    for path in paths:
        app = AppTest.from_file(str(path), default_timeout=30)
        app.run()

        assert not app.exception, f"{path} raised {app.exception}"
