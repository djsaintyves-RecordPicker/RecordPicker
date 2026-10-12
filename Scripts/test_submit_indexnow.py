"""Verify deployment notifications never re-submit unchanged pages."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from submit_indexnow import changed_urls


class ChangedURLTests(unittest.TestCase):
    def test_added_changed_deleted_and_alias_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root, text=True).strip()
            def page(name, url, body='old'):
                (root / name).write_text(f'<link rel="canonical" href="{url}"><main>{body}</main>')
            git('init', '-q')
            git('config', 'user.name', 'Test')
            git('config', 'user.email', 'test@example.invalid')
            page('unchanged.html', 'https://recordpicker.app/unchanged/')
            page('changed.html', 'https://recordpicker.app/changed/')
            page('deleted.html', 'https://recordpicker.app/deleted/')
            page('alias.html', 'https://recordpicker.app/changed/')
            git('add', '.')
            git('commit', '-qm', 'baseline')
            baseline = git('rev-parse', 'HEAD')
            page('changed.html', 'https://recordpicker.app/changed/', 'new')
            page('alias.html', 'https://recordpicker.app/changed/', 'new')
            page('added.html', 'https://recordpicker.app/added/')
            page('external.html', 'https://example.org/private/')
            (root / 'deleted.html').unlink()
            (root / 'feed.json').write_text('{}')
            git('add', '-A')
            git('commit', '-qm', 'deployment')
            self.assertEqual(changed_urls(baseline, root), [
                'https://recordpicker.app/added/',
                'https://recordpicker.app/changed/',
                'https://recordpicker.app/deleted/',
            ])
            self.assertEqual(changed_urls('HEAD', root), [])
            self.assertEqual(changed_urls('0' * 40, root), [])


if __name__ == '__main__':
    unittest.main()
