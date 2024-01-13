import smtplib
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, parseaddr
from os.path import basename, isfile
from typing import Any
from urllib.parse import quote

import orjson
from starlette.responses import JSONResponse

import settings


class OrjsonResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return orjson.dumps(content)


def _build_attachments(attachments):
    result = []
    for attachment in attachments:
        if not isfile(attachment):
            continue
        mime_app = MIMEApplication(open(attachment, "rb").read())
        filename = basename(attachment)
        mime_app.add_header(
            "Content-Disposition", f"attachment; filename*=UTF-8''{quote(filename)}"
        )
        mime_app.add_header("Content-ID", f"<{filename}>")
        result.append(mime_app)
    return result


def _format_addr(email):
    name, addr = parseaddr(email)
    return formataddr((Header(name, "utf-8").encode(), addr))


def _format_addr_list(addr_list):
    return ",".join(list(map(_format_addr, addr_list)))


def _build_message(
    to, subject, content, cc=None, bcc=None, attachments=None, sender=None, **kwargs
):
    if not sender:
        sender = "alert-bot"
    EMAIL_SENDER = f"{sender}<bozhou_0728@qq.com>"
    msg = MIMEMultipart("ALTERNATIVE")
    msg["Subject"] = subject
    msg["From"] = _format_addr(EMAIL_SENDER)
    msg["Sender"] = _format_addr(EMAIL_SENDER)
    msg["To"] = _format_addr_list(to)
    msg["Date"] = formatdate(localtime=True)
    content = MIMEText(content, "html", "utf8")
    msg.attach(content)
    if cc:
        msg["CC"] = _format_addr_list(cc)
    if bcc:
        msg["BCC"] = _format_addr_list(bcc)
    if attachments:
        if isinstance(attachments, str):
            attachments = [attachments]
        for attachment in _build_attachments(attachments):
            msg.attach(attachment)
    return msg


def _send_email(message, **kwargs):
    with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT) as s:
        s.login(settings.EMAIL_USER, settings.EMAIL_PASS)
        s.send_message(message)
        s.quit()


def send_mail(
    subject,
    content,
    to=["myalertmail@foxmail.com"],
    cc=None,
    bcc=None,
    attachments=None,
    sender=None,
):
    msg = _build_message(to, subject, content, cc, bcc, attachments, sender)
    _send_email(msg)
