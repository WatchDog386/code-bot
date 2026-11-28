"""Regression checks for importing project ZIP archives."""

import io
import stat
import unittest
import uuid
import zipfile

from codebot.projects import delete_uploaded_project, import_project_archive, project_files


class ProjectArchiveImportTests(unittest.TestCase):
    def setUp(self):
        self.archive_name = f"upload-check-{uuid.uuid4().hex}.zip"
        self.project_name = None

    def tearDown(self):
        if self.project_name:
            delete_uploaded_project(self.project_name)

    def test_keeps_nested_source_and_skips_linked_dependencies(self):
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("sample-app/src/main.py", "print('ready')\n")
            archive.writestr("sample-app/docs/README.md", "# Sample\n")
            link = zipfile.ZipInfo("sample-app/node_modules/pkg/link")
            link.create_system = 3
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(link, "outside-target")

        imported = import_project_archive(self.archive_name, payload.getvalue())
        self.project_name = imported["name"]
        self.assertEqual((imported["files"], imported["skipped"]), (2, 1))
        self.assertEqual([path for path, _ in project_files(self.project_name)], [
            "src/main.py", "docs/README.md",
        ])

    def test_rejects_parent_directory_paths(self):
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("../outside.py", "print('unsafe')\n")
        with self.assertRaisesRegex(ValueError, "unsafe file path"):
            import_project_archive(self.archive_name, payload.getvalue())


if __name__ == "__main__":
    unittest.main()
