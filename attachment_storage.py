"""Save untrusted email attachments inside a chosen email directory."""

import os
from pathlib import Path
import re


def save_attachment_file(folder, filename, payload):
    """Reject unsafe names and create a new file without replacing existing files."""
    if (
        not isinstance(filename, str)
        or not filename
        or filename in {".", ".."}
        or filename.endswith((".", " "))
        or re.search(r'[<>:"/\\|?*\x00-\x1f]', filename)
    ):
        raise ValueError("Unsafe attachment filename: expected a plain file name")

    # Windows device names remain special even when followed by an extension.
    device_name = filename.split(".", 1)[0].rstrip(" ").upper()
    reserved = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
    if device_name in reserved or re.fullmatch(r"(?:COM|LPT)[1-9¹²³]", device_name):
        raise ValueError("Unsafe attachment filename: reserved device name")

    directory = Path(folder).resolve(strict=True)
    stem, extension = os.path.splitext(filename)
    counter = 0
    while True:
        name = filename if counter == 0 else f"{stem}_{counter}{extension}"
        destination = directory / name
        if destination.resolve().parent != directory:
            raise ValueError("Attachment destination escapes the email directory")
        try:
            # Exclusive creation also prevents overwrites and symlink races.
            with destination.open("xb") as attachment:
                attachment.write(payload)
        except FileExistsError:
            counter += 1
            continue
        return destination
