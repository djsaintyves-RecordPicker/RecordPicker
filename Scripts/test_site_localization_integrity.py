from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from site_localization_integrity import page_digest


class SiteLocalizationIntegrityTests(unittest.TestCase):
    def digest(self, html: str) -> tuple[str, str] | None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "index.html"
            path.write_text(html, encoding="utf-8")
            return page_digest(path)

    def test_formatting_does_not_change_semantic_digest(self) -> None:
        compact = (
            '<html data-page-lang="fr"><head><title>Record Picker</title>'
            '<meta name="description" content="Choisissez un disque."></head>'
            '<body><main><h1>Votre collection</h1></main></body></html>'
        )
        spaced = (
            '<html data-page-lang="fr">\n<head><title> Record Picker </title>'
            '<meta name="description" content="Choisissez un disque."></head>'
            '<body><main>\n<h1>Votre   collection</h1>\n</main></body></html>'
        )
        self.assertEqual(self.digest(compact), self.digest(spaced))

    def test_visible_or_accessible_copy_changes_digest(self) -> None:
        before = '<html data-page-lang="fr"><main><img alt="Disque"></main></html>'
        after = '<html data-page-lang="fr"><main><img alt="Album"></main></html>'
        self.assertNotEqual(self.digest(before), self.digest(after))


if __name__ == "__main__":
    unittest.main()
