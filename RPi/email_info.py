import subprocess
import smtplib
from email.mime.text import MIMEText
from datetime import datetime


def send_mail_with_ip_as_content():
    to = 'showmyway10@gmail.com'
    gmail_user = 'showmyway10@gmail.com'
    gmail_password = '******'  # use our email password and fill this in: CG3002T10
    smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(gmail_user, gmail_password)
    arg = 'ip route list'
    p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE)
    data = p.communicate()
    split_data = data[0].split()
    ipaddr = split_data[split_data.index('src') + 1]
    my_ip = 'Your IP is %s' % ipaddr
    msg = MIMEText(my_ip)
    msg['Subject'] = 'IP For RaspberryPi on %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg['From'] = gmail_user
    msg['To'] = to
    smtpserver.sendmail(gmail_user, [to], msg.as_string())
    smtpserver.quit()

if __name__ == '__main__':
    send_mail_with_ip_as_content()
