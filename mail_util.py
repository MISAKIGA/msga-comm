# -*- coding:utf-8 -*-

import smtplib
import poplib

from email.header import decode_header
from email.mime.text import MIMEText
from email.utils import parseaddr
from loguru import logger
from email.parser import Parser


class MailManager(object):

    def __init__(self, pop_host='pop.qq.com', smtp_host='smtp.qq.com', port=587, username='', password='', send_mail=''):
        self.popHost = pop_host
        self.smtpHost = smtp_host
        self.port = port
        self.userName = username
        self.passWord = password
        self.sendMail = send_mail
        self.login()
        self.configMailBox()

    # 登录邮箱
    def login(self):
        try:
            self.mailLink = poplib.POP3_SSL(self.popHost)
            self.mailLink.set_debuglevel(0)
            self.mailLink.user(self.userName)
            self.mailLink.pass_(self.passWord)
            self.mailLink.list()
            logger.info('邮箱登录成功!')
        except Exception as e:
            logger.error('邮箱登录失败! {}', e)
            quit()

    # 获取邮件
    def retrMail(self, delete=False):
        try:
            mail_list = self.mailLink.list()[1]
            if len(mail_list) == 0:
                return None
            number = len(mail_list)
            resp, lines, octets = self.mailLink.retr(number)
            if delete:
                self.mailLink.dele(number)
            # lines是邮件内容，列表形式使用join拼成一个byte变量
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            # 解析出邮件:
            msg = Parser().parsestr(msg_content)

            content = []
            self.print_info(msg, content)

            return content
        except Exception as e:
            logger.error(e)
            return None

    def print_info(self, msg, arr, indent=0):
        if indent == 0:
            for header in ['From', 'To', 'Subject']:
                value = msg.get(header, '')
                if value:
                    if header == 'Subject':
                        value = self.decode_str(value)
                    else:
                        hdr, addr = parseaddr(value)
                        name = self.decode_str(hdr)
                        value = u'%s <%s>' % (name, addr)
                arr.append(str('%s%s: %s' % ('  ' * indent, header, value)))
        if msg.is_multipart():
            parts = msg.get_payload()
            for n, part in enumerate(parts):
                arr.append(str('%spart %s' % ('  ' * indent, n)))
                arr.append(str('%s--------------------' % ('  ' * indent)))
                self.print_info(part, arr=arr, indent=indent + 1)
        else:
            content_type = msg.get_content_type()
            if content_type == 'text/plain' or content_type == 'text/html':
                content = msg.get_payload(decode=True)
                charset = self.guess_charset(msg)
                if charset:
                    content = content.decode(charset)
                arr.append(str('%sText: %s' % ('  ' * indent, content + '...')))
            else:
                arr.append(str('%sAttachment: %s' % ('  ' * indent, content_type)))

    def decode_str(self, s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    def guess_charset(self, msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset

    def configMailBox(self):
        try:
            self.mail_box = smtplib.SMTP(self.smtpHost, self.port)
            self.mail_box.ehlo()
            self.mail_box.starttls()
            self.mail_box.login(self.userName, self.passWord)
            logger.info('config mailbox success!')
        except Exception as e:
            print(e)
            logger.error('config mailbox fail! ' + str(e))
            quit()

    def close(self):
        # 关闭连接:
        self.mailLink.quit()
        self.mail_box.close()

    # 发送邮件
    def sendMsg(self, mail_body='Success!'):
        try:
            msg = MIMEText(mail_body, 'plain', 'utf-8')
            msg['Subject'] = mail_body
            msg['from'] = self.userName
            self.mail_box.sendmail(self.userName, self.sendMail, msg.as_string())
            logger.info('send mail success!')
        except Exception as e:
            logger.error('send mail fail! ' + str(e))
