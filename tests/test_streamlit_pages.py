from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import github_issues


def test_all_streamlit_pages_render_without_exceptions(monkeypatch):
    monkeypatch.setattr(
        github_issues,
        "fetch_public_issues",
        lambda *args, **kwargs: github_issues.GitHubIssuesResult(()),
    )
    paths = [Path("app.py"), *sorted(Path("pages").glob("*.py"))]

    for path in paths:
        app = AppTest.from_file(str(path), default_timeout=30)
        app.run()

        assert not app.exception, f"{path} raised {app.exception}"
