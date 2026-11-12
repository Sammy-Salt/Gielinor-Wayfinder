# PASS31.68 – Copy and spacing cleanup

- Removed leading emoji from page h1/h2 headings (14 pages); nav icons unchanged.
- Item page: replaced developer-voice copy ("Trusted acquisition relationships from the project's canonical data model", "No trusted … relationships") with plain wording.
- `site.css`: the dark map-panel rule (`#toolbar,#legend,#info,#results`) is now scoped to `body[data-page="map"]`, removing the stray panel strip behind the Monsters list.
- Crafting and other pages: smaller gap between header subtitle and first controls card.
- No data changes. Validation: `tests/test_pass31_68.py`, all pass31 gates, verify_project, pytest.
