from utils import ui


def test_catalog_entries_have_actionable_metadata():
    assert ui.TOOLS
    for tool in ui.TOOLS:
        assert tool.title.strip()
        assert tool.short_title.strip()
        assert tool.description.strip()
        assert tool.path.startswith("pages/")
        assert tool.category in ui.SIDEBAR_CATEGORIES
        assert tool.professions


def test_catalog_aliases_and_related_handoffs_resolve():
    known_slugs = {tool.slug for tool in ui.TOOLS}
    aliases = [alias for tool in ui.TOOLS for alias in tool.aliases]
    assert len(aliases) == len(set(aliases))
    for tool in ui.TOOLS:
        assert tool.slug in known_slugs
        for alias in tool.aliases:
            assert tool in ui.filter_tools(query=alias)
        for related in ui.related_tools(tool.slug):
            assert related.slug in known_slugs


def test_guided_workflows_have_previewable_steps():
    assert ui.GUIDED_WORKFLOWS
    known_slugs = {tool.slug for tool in ui.TOOLS}
    for workflow in ui.GUIDED_WORKFLOWS:
        assert workflow.title.strip()
        assert workflow.description.strip()
        assert workflow.slugs
        assert all(slug in known_slugs for slug in workflow.slugs)
        assert ui.guided_workflows(query=workflow.title)
