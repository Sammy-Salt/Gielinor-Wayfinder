from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]/"site"

def test_every_page_has_static_shell_tools():
    pages=list(ROOT.glob("*.html"))
    assert pages
    for page in pages:
        text=page.read_text()
        if 'id="site-nav"' not in text: continue
        assert text.count('id="site-nav"')==1, page
        assert text.count('id="app-tools-host"')==1, page
        assert text.count('id="app-tools"')==1, page
        assert 'id="globalSearch"' in text, page
        assert 'id="globalSearchResults"' in text, page
        assert 'character.html' in text, page
        assert 'crafting.html' in text, page

def test_enhancer_does_not_create_or_remove_shell_nodes():
    text=(ROOT/"js/components/app-enhancer.js").read_text()
    assert 'document.createElement("section")' not in text
    assert 'nav.replaceChildren' not in text
    assert 'nav.remove' not in text
    assert 'tools.dataset.bound' in text

def test_item_uses_same_static_shell():
    text=(ROOT/"item.html").read_text()
    assert 'id="app-tools-host"' in text
    assert 'id="app-tools"' in text
    assert 'js/pages/item.js?v=41' in text
