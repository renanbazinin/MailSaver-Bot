# Gmail Email Downloader with Labeling and Review

This application connects to your Gmail account, downloads large emails based on a specified size threshold, saves email content and attachments to your computer, and labels these emails for easy manual deletion later. The app provides a GUI (Graphical User Interface) where you can specify your settings and track download progress through real-time logs.

---

## Installation

### Prerequisites

1. **Python 3.x**: Make sure Python 3.x is installed. You can download it from [python.org](https://www.python.org/downloads/).
2. **Gmail App Password**: If you have 2-Step Verification enabled for Gmail, you'll need an App Password. Follow [this guide](https://support.google.com/accounts/answer/185833?hl=en) to create an App Password.
3. **IMAP Access**: Ensure IMAP access is enabled in your Gmail settings:
   - Go to Gmail > Settings > See all settings > Forwarding and POP/IMAP.
   - Enable IMAP.

### Required Libraries

- **Standard Libraries**:
  - `imaplib`, `email`, `os`, `zipfile`, `datetime`, `re`, `tkinter`

- **External Libraries** (install with pip):

```bash
pip install beautifulsoup4 requests
```

### Downloading and Running the Application

1. **Clone or Download the Repository**: 

   ```bash
   git clone https://github.com/renanbazinin/Email-Downloader-and-label-for-delete.git
   ```

   Or download the ZIP file and extract it.

2. **Run the Application**:

   Navigate to the directory and start the application:

   ```bash
   python email_downloader.py
   ```

---

## Usage

Upon launching the application, you’ll see a GUI window where you can configure the settings for email downloading. Follow these steps:

1. **Enter Gmail Username**: Enter your Gmail address.
2. **Enter Gmail App Password**: Enter your Gmail App Password.
3. **Specify Download Directory**: Choose or enter the directory where emails should be saved. Default is `Downloaded_Emails`.
4. **Custom Label for Marking**: Provide a label name (e.g., `MARKED_TO_DELETE_BY_RENANS_BOT`) to apply to emails after downloading. This label will make it easier to review and delete these emails manually.
5. **Size Threshold**: Specify the minimum email size (in MB) to download. Only emails larger than this size will be downloaded.
6. **Number of Emails to Download**: Set the maximum number of large emails to download in this session.

### Important Note:

- **Review Before Deletion**: After downloading, the emails will be labeled as specified (e.g., `MARKED_TO_DELETE_BY_RENANS_BOT`). Review them in Gmail on your computer **before** deleting to ensure you don’t lose important information.

### Logs and Progress Tracking

The application displays live logs as it processes each email. This log includes each step, any errors encountered, and details of each attachment saved.

---

## Features

- **Download Attachments and Content**: The app downloads email attachments and saves email content in a text file, even when the content is HTML-based.
- **Unique Filename Handling**: For emails with multiple attachments of the same name, the app automatically appends numbers to filenames to prevent overwriting.
- **Inline Images**: The app detects and saves inline images embedded in HTML emails.
- **Labeling for Manual Deletion**: All downloaded emails are labeled for easy review and deletion.

### Disclaimer on Email Content

The application attempts to save all email content, including HTML-based templates, as plain text in `email_content.txt` files. **However**, certain complex HTML structures or unique encoding types may not render correctly as plain text. Please manually review the downloaded content if it contains critical information.

---

## Example Usage

Once configured, click **Start Download**. The log will display each email being processed, attachments saved, and any errors. After the process is complete, you’ll be prompted with a message that the download and labeling are complete.

### Screenshots and Media

- **Downloaded Attachments and Label Example**  
  ![Download Example](https://i.imgur.com/WXN6CZc.png)

- **Text Content from HTML Email Example**  
  ![Text Content Example](https://i.imgur.com/MJZ0GSP.png)

- **Usage Demonstration Video**  
  [![Usage Video](https://img.youtube.com/vi/1e290CW/0.jpg)](https://i.imgur.com/1e290CW.mp4)

---

## Troubleshooting

### Common Errors

1. **Authentication Error**: Ensure your App Password is correct and that IMAP is enabled in your Gmail settings.
2. **Failed to Save Attachment**: Occasionally, attachments with unusual filenames or encoding issues might fail to save. Check the logs for details.

### Additional Notes

- **Responsibility Disclaimer**: The user is responsible for verifying the downloaded content **before** deleting emails in Gmail. The app assists in saving and organizing emails but does not guarantee the accuracy of rendered HTML content.
  
---

## Contributions

Feel free to submit pull requests to add features or fix bugs. This is an open-source project, and contributions are welcome!

## License

This project is licensed under the MIT License - see the `LICENSE.md` file for details.
