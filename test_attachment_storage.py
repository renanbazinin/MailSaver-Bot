import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from attachment_storage import save_attachment_file


class AttachmentStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folder = self.root / "email"
        self.folder.mkdir()

    def test_preserves_ordinary_and_unicode_filenames(self):
        for name in ["report.pdf", "my photo.png", "דוח שנתי.pdf", "archive.tar.gz"]:
            with self.subTest(name=name):
                path = save_attachment_file(self.folder, name, b"content")
                self.assertEqual(path, self.folder.resolve() / name)
                self.assertEqual(path.read_bytes(), b"content")

    def test_rejects_paths_on_both_windows_and_unix(self):
        names = [
            "../outside.txt", "../../outside.txt", r"..\outside.txt",
            r"..\../outside.txt", "/tmp/outside.txt", r"\outside.txt",
            r"C:\outside.txt", "C:outside.txt", r"\\server\share\outside.txt",
            "folder/file.txt", r"folder\file.txt", str(self.root / "outside.txt"),
        ]
        for name in names:
            with self.subTest(name=name), self.assertRaises(ValueError):
                save_attachment_file(self.folder, name, b"untrusted")
        self.assertEqual(list(self.folder.iterdir()), [])
        self.assertFalse((self.root / "outside.txt").exists())

    def test_rejects_special_or_ambiguous_windows_names(self):
        names = [
            "", ".", "..", "file.", "file ", "file\x00.txt", "file\n.txt",
            "file:stream", 'a"b.txt', "a<b", "a>b", "a|b", "a?b", "a*b",
            "NUL", "con.txt", "AUX.log", "PRN", "COM1.txt", "LPT9",
            "COM¹.txt", "CON .txt", "CONIN$", "CONOUT$.txt",
        ]
        for name in names:
            with self.subTest(name=name), self.assertRaises(ValueError):
                save_attachment_file(self.folder, name, b"untrusted")
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_existing_attachments_and_email_content_are_not_overwritten(self):
        for name in ["report.pdf", "email_content.txt", "inline_image_1.png"]:
            with self.subTest(name=name):
                original = save_attachment_file(self.folder, name, b"original")
                second = save_attachment_file(self.folder, name, b"second")
                third = save_attachment_file(self.folder, name, b"third")
                self.assertEqual(original.read_bytes(), b"original")
                self.assertEqual(second.read_bytes(), b"second")
                self.assertEqual(third.read_bytes(), b"third")
                self.assertEqual(second.name, f"{original.stem}_1{original.suffix}")
                self.assertEqual(third.name, f"{original.stem}_2{original.suffix}")

    def test_exclusive_create_handles_a_file_appearing_after_validation(self):
        original_open = Path.open
        target = self.folder / "report.pdf"
        raced = False

        def competing_open(path, mode="r", *args, **kwargs):
            nonlocal raced
            if path == target and mode == "xb" and not raced:
                raced = True
                with original_open(path, "wb") as existing:
                    existing.write(b"other writer")
            return original_open(path, mode, *args, **kwargs)

        with patch.object(Path, "open", competing_open):
            saved = save_attachment_file(self.folder, "report.pdf", b"download")
        self.assertEqual(target.read_bytes(), b"other writer")
        self.assertEqual(saved.name, "report_1.pdf")
        self.assertEqual(saved.read_bytes(), b"download")

    def test_existing_symlink_cannot_redirect_an_attachment_outside(self):
        outside = self.root / "outside.txt"
        outside.write_bytes(b"original")
        link = self.folder / "report.pdf"
        try:
            os.symlink(outside, link)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Symlink creation unavailable: {error}")
        with self.assertRaises(ValueError):
            save_attachment_file(self.folder, "report.pdf", b"untrusted")
        self.assertEqual(outside.read_bytes(), b"original")


class DownloadIntegrationTests(unittest.TestCase):
    def run_download(self, message):
        import emailDownGUI as gui

        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        imap = Mock()
        imap.select.return_value = ("OK", [b"1"])
        imap.search.return_value = ("OK", [b"1"])
        imap.fetch.return_value = ("OK", [(b"1 (RFC822)", message.as_bytes())])
        with patch.object(gui.imaplib, "IMAP4_SSL", return_value=imap), \
                patch.object(gui.messagebox, "showerror") as error, \
                patch.object(gui.messagebox, "showinfo") as info:
            gui.download_emails("user", "password", temp.name, "review", 1, 1, Mock())
        return Path(temp.name), imap, error, info

    def message(self):
        from email.message import EmailMessage

        message = EmailMessage()
        message["Subject"] = "Test"
        message["Date"] = "Sun, 01 Nov 2026 12:00:00 +0000"
        message.set_content("Email body")
        return message

    def test_rejected_attachment_does_not_label_the_email_for_deletion(self):
        message = self.message()
        message.add_attachment(b"untrusted", maintype="application",
                               subtype="octet-stream", filename="../outside.txt")
        root, imap, error, info = self.run_download(message)
        error.assert_called_once()
        self.assertIn("Unsafe attachment filename", error.call_args.args[1])
        imap.store.assert_not_called()
        info.assert_not_called()
        self.assertFalse((root / "outside.txt").exists())

    def test_attachments_and_inline_images_share_safe_duplicate_handling(self):
        from email.message import EmailMessage

        message = self.message()
        message.add_attachment(b"attachment", maintype="image", subtype="png",
                               filename="inline_image_1.png")
        inline = EmailMessage()
        inline.set_content(b"inline", maintype="image", subtype="png")
        inline["Content-Disposition"] = "inline"
        message.attach(inline)
        root, imap, error, info = self.run_download(message)
        folder = root / "Email_1_2026-11-01_Test"
        self.assertEqual((folder / "inline_image_1.png").read_bytes(), b"attachment")
        self.assertEqual((folder / "inline_image_1_1.png").read_bytes(), b"inline")
        error.assert_not_called()
        imap.store.assert_called_once_with(b"1", "+X-GM-LABELS", "(review)")
        info.assert_called_once()


if __name__ == "__main__":
    unittest.main()
