import imaplib
import email
from email.header import decode_header
import os
import zipfile
from datetime import datetime
import re
from bs4 import BeautifulSoup
import requests
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext


# Email download function with live log updates and auto-scrolling
# Imports and GUI setup (same as your previous code)


def save_attachment(filepath, payload, log_text):
    """
    Save an attachment file, avoiding overwriting by appending numbers if a file with the same name exists.
    """
    base, extension = os.path.splitext(filepath)
    counter = 1
    # Check if the file exists; if so, add a number to make it unique
    while os.path.exists(filepath):
        filepath = f"{base}_{counter}{extension}"
        counter += 1

    with open(filepath, "wb") as f:
        f.write(payload)
    log_text.insert(tk.END, f"Saved attachment: {filepath}\n")
    log_text.see(tk.END)  # Auto-scroll to the end
    log_text.update_idletasks()




def download_emails(username, password, base_dir, label_name, size_threshold_mb, n_emails, log_text):
    try:
        log_text.insert(tk.END, "Connecting to Gmail...\n")
        log_text.see(tk.END)
        log_text.update_idletasks()
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(username, password)
        log_text.insert(tk.END, "Connected successfully. Please wait...\n")
        log_text.see(tk.END)
        log_text.update_idletasks()

        status, messages = imap.select("INBOX")
        size_threshold = size_threshold_mb * 1024 * 1024  # Convert MB to bytes
        status, email_ids = imap.search(None, f"(LARGER {size_threshold})")
        email_ids = email_ids[0].split()

        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        for i, email_id in enumerate(email_ids[:n_emails]):
            log_text.insert(tk.END, f"\nProcessing email ID {email_id} ({i + 1}/{n_emails})\n")
            log_text.see(tk.END)
            log_text.update_idletasks()
            res, msg_data = imap.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg["Subject"]
                    date = msg["Date"]
                    if subject:
                        subject, encoding = decode_header(subject)[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                    else:
                        subject = "No_Subject"

                    log_text.insert(tk.END, f"Processing email with subject: {subject}\n")
                    log_text.see(tk.END)
                    log_text.update_idletasks()

                    if date:
                        email_date = email.utils.parsedate_to_datetime(date)
                        formatted_date = email_date.strftime("%Y-%m-%d")
                    else:
                        formatted_date = "No_Date"

                    safe_subject = re.sub(r'[<>:"/\\|?*]', '', subject).strip()
                    folder_name = os.path.join(base_dir, f"Email_{i + 1}_{formatted_date}_{safe_subject}")
                    os.makedirs(folder_name, exist_ok=True)

                    content_file_path = os.path.join(folder_name, "email_content.txt")
                    with open(content_file_path, "w", encoding="utf-8") as f:
                        f.write(f"Subject: {subject}\nDate: {formatted_date}\n\n")
                        if msg.is_multipart():
                            inline_image_count = 1
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                log_text.insert(tk.END, f"Processing part with content type: {content_type}\n")
                                log_text.see(tk.END)
                                log_text.update_idletasks()

                                if content_type == "text/html" and "attachment" not in content_disposition:
                                    html_content = part.get_payload(decode=True)
                                    if isinstance(html_content, bytes):
                                        html_content = html_content.decode(part.get_content_charset() or "utf-8")
                                    soup = BeautifulSoup(html_content, "html.parser")
                                    visible_text = soup.get_text(separator="\n", strip=True)
                                    try:
                                        f.write(visible_text)
                                    except Exception as e:
                                        log_text.insert(tk.END, f"Error writing visible text for email '{subject}': {e}\n")
                                        log_text.see(tk.END)
                                        log_text.update_idletasks()

                                elif content_disposition and "attachment" in content_disposition:
                                    filename = part.get_filename()
                                    if filename:
                                        filename = decode_header(filename)[0][0]
                                        if isinstance(filename, bytes):
                                            filename = filename.decode()

                                        filepath = os.path.join(folder_name, filename)
                                        save_attachment(filepath, part.get_payload(decode=True), log_text)

                                elif content_type.startswith("image/") and "attachment" not in content_disposition:
                                    # Inline image handling
                                    filename = f"inline_image_{inline_image_count}.{content_type.split('/')[-1]}"
                                    filepath = os.path.join(folder_name, filename)
                                    with open(filepath, "wb") as f:
                                        f.write(part.get_payload(decode=True))
                                    log_text.insert(tk.END, f"Saved inline image: {filepath}\n")
                                    log_text.see(tk.END)
                                    log_text.update_idletasks()
                                    inline_image_count += 1
                        else:
                            body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8")
                            try:
                                f.write(body)
                            except Exception as e:
                                log_text.insert(tk.END, f"Error writing body text for email '{subject}': {e}\n")
                                log_text.see(tk.END)
                                log_text.update_idletasks()

                    imap.store(email_id, "+X-GM-LABELS", f"({label_name})")
                    log_text.insert(tk.END, f"Labeled email '{subject}' with '{label_name}'\n")
                    log_text.see(tk.END)
                    log_text.update_idletasks()

        imap.close()
        imap.logout()
        log_text.insert(tk.END, "\nDownload complete. Please review and delete emails in the marked label.\n")
        log_text.see(tk.END)
        log_text.update_idletasks()
        messagebox.showinfo("Download Complete", "Email download and labeling complete. Please manually review and delete emails in the marked label.")
    except Exception as e:
        log_text.insert(tk.END, f"Error: {str(e)}\n")
        log_text.see(tk.END)
        log_text.update_idletasks()
        messagebox.showerror("Error", str(e))

# GUI setup (same as your previous code)
# Run the GUI (same as your previous code)


# GUI setup
def run_gui():
    def start_download():
        username = entry_username.get()
        password = entry_password.get()
        base_dir = filedialog.askdirectory() if not entry_base_dir.get() else entry_base_dir.get()
        label_name = entry_label.get().replace(" ", "_")
        size_threshold_mb = int(entry_size.get())
        n_emails = int(entry_n.get())

        if not label_name.isidentifier():
            messagebox.showerror("Invalid Label",
                                 "Label name must not contain spaces and should be in format text_text_text.")
            return

        if messagebox.askyesno("Disclaimer",
                               "You are responsible for verifying downloaded content before deletion. Proceed?"):
            log_text.delete("1.0", tk.END)  # Clear the log area
            download_emails(username, password, base_dir, label_name, size_threshold_mb, n_emails, log_text)

    # GUI window
    root = tk.Tk()
    root.title("Gmail Email Downloader")
    root.geometry("600x600")

    # Labels and entries with default values
    tk.Label(root, text="Enter Gmail Username:").pack()
    entry_username = tk.Entry(root, width=40)
    entry_username.pack()

    tk.Label(root, text="Enter Gmail App Password:").pack()
    entry_password = tk.Entry(root, show="*", width=40)
    entry_password.pack()

    tk.Label(root, text="Base Directory to Save Emails:").pack()
    entry_base_dir = tk.Entry(root, width=40)
    entry_base_dir.insert(0, "Downloaded_Emails")  # Default value
    entry_base_dir.pack()

    tk.Label(root, text="Custom Label (no spaces):").pack()
    entry_label = tk.Entry(root, width=40)
    entry_label.insert(0, "MARKED_TO_DELETE_BY_RENANS_BOT")  # Default value
    entry_label.pack()

    tk.Label(root, text="Size Threshold (in MB):").pack()
    entry_size = tk.Entry(root, width=10)
    entry_size.insert(0, "10")  # Default value
    entry_size.pack()

    tk.Label(root, text="Number of Emails to Download (N):").pack()
    entry_n = tk.Entry(root, width=10)
    entry_n.insert(0, "10")  # Default value
    entry_n.pack()

    # Explanation and disclaimer
    tk.Label(root,
             text="\nThis app downloads emails larger than the specified size\nand labels them for manual deletion.\n",
             fg="blue").pack()
    tk.Label(root, text="DISCLAIMER: Verify content before deleting.\nYou are responsible for email management.",
             fg="red").pack()

    # Start button
    tk.Button(root, text="Start Download", command=start_download, bg="green", fg="white").pack(pady=10)

    # Log area with auto-scroll
    tk.Label(root, text="Log Output:").pack()
    log_text = scrolledtext.ScrolledText(root, width=70, height=15, wrap=tk.WORD, state='normal')
    log_text.pack()

    root.mainloop()


# Run the GUI

run_gui()
