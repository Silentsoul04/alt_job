import io
import re
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import socket
import traceback
import threading
import time
from datetime import datetime
import io
import scrapy.mail
import datetime
from string import Template
from .utils import get_valid_filename, log
from .utils import get_xlsx_file_bytes
from .jobs import Job

# Date format used everywhere
DATE_FORMAT='%Y-%m-%dT%H-%M-%S'

class MailSender():
    '''Send jobs alerts'''

    def __init__(self, smtphost, mailfrom, smtpuser, smtppass, smtpport, smtptls, mailto):
        if not isinstance(mailto, list):
            raise TypeError('mailto must be a list, not '+str(type(mailto)))
        self.smtphost=smtphost
        self.mailfrom=mailfrom
        self.smtpuser=smtpuser
        self.smtppass=smtppass
        self.smtpport=smtpport
        self.smtptls=smtptls
        self.mailto=mailto

    def send_mail_alert(self, jobs):
        '''Sending the report'''
        date = datetime.datetime.now().isoformat(timespec='minutes')
        # Building message
        message = MIMEMultipart("html")
        message['Subject'] = 'New job postings - {}'.format(date)
        message['From'] = self.mailfrom
        message['To'] = ','.join(self.mailto)
        body = self.build_message(jobs)
        message.attach(MIMEText(body, 'html'))

        log.debug('Mail HTML :\n'+body)

        # if self.attach_jobs_description:
        #     for job in jobs:
        #         file = io.BytesIO()
        #         file.write(job.get_text().encode('utf-8'))
        #         file.seek(0)
        #         attachment=MIMEApplication(file.read(), Name=get_valid_filename(job['title'])+'.txt')
        #         attachment.add_header("Content-Disposition", "attachment; filename=%s.txt"%(get_valid_filename(job['title'])))
        #         message.attach(attachment)

        # Attach excel file
        attachment=MIMEApplication(get_xlsx_file_bytes(items=jobs), Name=get_valid_filename(message['Subject'])+'.xlsx')
        attachment.add_header("Content-Disposition", "attachment; filename={}".format(get_valid_filename(message['Subject'])+'.xlsx'))
        message.attach(attachment)

        server=smtplib.SMTP(host=self.smtphost, port=self.smtpport)
        server.ehlo_or_helo_if_needed()
        # SSL
        if self.smtptls: server.starttls()
        # SMTP Auth
        if self.smtpuser and self.smtppass: server.login(self.smtpuser, self.smtppass)
        # Send Email
        server.sendmail(self.mailfrom, self.mailto, message.as_string())
        server.quit()


    def build_message(self, jobs):
        '''Build mail message text base on jobs'''
        message=''
        message+='<p style="font-family: sans-serif; font-size: 14px; font-weight: normal; margin: 0; Margin-bottom: 15px;">Hello,</p>'
        message+='<p style="font-family: sans-serif; font-size: 14px; font-weight: normal; margin: 0; Margin-bottom: 15px;"><b>{} new job postings have been found.</b><br />You can review the jobs from this email or download the attached Excel file.</p>'.format(len(jobs))
                        
        all_sources=set([j['source'] for j in jobs])
        for src in all_sources:
            src_posting=[j for j in jobs if j['source']==src]
            message += "<h4>{} job postings from {}</h4>".format(len(src_posting), src)
            message += '<p style="font-family: sans-serif; font-size: 14px; font-weight: normal; margin: 0; Margin-bottom: 15px;">'
            for job in src_posting:
                message+="""<a href="{url}">{title}</a>{org} | """.format(
                    title=job['title'],
                    url=job['url'],
                    org='' if not job['organisation'] else ' ({})'.format(job['organisation'])
                )
            message += "</p>"

        message+='<p style="font-family: sans-serif; font-size: 14px; font-weight: normal; margin: 0; Margin-bottom: 15px;">Good luck!</p>'

        message = self.TEMPLATE_EMAIL.substitute(content=message)
        return message

    TEMPLATE_EMAIL=Template("""
<!doctype html>
<html>
  <head>
    <meta name="viewport" content="width=device-width">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>Simple Transactional Email</title>
    <style>
    /* -------------------------------------
        INLINED WITH htmlemail.io/inline
    ------------------------------------- */
    /* -------------------------------------
        RESPONSIVE AND MOBILE FRIENDLY STYLES
    ------------------------------------- */
    @media only screen {
      table[class=body] h1 {
        font-size: 28px !important;
        margin-bottom: 10px !important;
      }
      table[class=body] p,
            table[class=body] ul,
            table[class=body] ol,
            table[class=body] td,
            table[class=body] span,
            table[class=body] a {
        font-size: 16px !important;
      }
      table[class=body] .wrapper,
            table[class=body] .article {
        padding: 10px !important;
      }
      table[class=body] .content {
        padding: 0 !important;
      }
      table[class=body] .container {
        padding: 0 !important;
        width: 100% !important;
      }
      table[class=body] .main {
        border-left-width: 0 !important;
        border-radius: 0 !important;
        border-right-width: 0 !important;
      }
      table[class=body] .btn table {
        width: 100% !important;
      }
      table[class=body] .btn a {
        width: 100% !important;
      }
      table[class=body] .img-responsive {
        height: auto !important;
        max-width: 100% !important;
        width: auto !important;
      }
    }

    /* -------------------------------------
        PRESERVE THESE STYLES IN THE HEAD
    ------------------------------------- */
    @media all {
      .ExternalClass {
        width: 100%;
      }
      .ExternalClass,
            .ExternalClass p,
            .ExternalClass span,
            .ExternalClass font,
            .ExternalClass td,
            .ExternalClass div {
        line-height: 100%;
      }
      .apple-link a {
        color: inherit !important;
        font-family: inherit !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
        text-decoration: none !important;
      }
      #MessageViewBody a {
        color: inherit;
        text-decoration: none;
        font-size: inherit;
        font-family: inherit;
        font-weight: inherit;
        line-height: inherit;
      }
      .btn-primary table td:hover {
        background-color: #34495e !important;
      }
      .btn-primary a:hover {
        background-color: #34495e !important;
        border-color: #34495e !important;
      }
    }
    </style>
  </head>
  <body class="" style="background-color: #f6f6f6; font-family: sans-serif; -webkit-font-smoothing: antialiased; font-size: 14px; line-height: 1.4; margin: 0; padding: 0; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%;">
    <table border="0" cellpadding="0" cellspacing="0" class="body" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%; background-color: #f6f6f6;">
      <tr>
        <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;">&nbsp;</td>
        <td class="container" style="font-family: sans-serif; font-size: 14px; vertical-align: top; display: block; Margin: 0 auto; max-width: 800px; padding: 10px; width: 800px;">
          <div class="content" style="box-sizing: border-box; display: block; Margin: 0 auto; max-width: 800px; padding: 10px;">

            <!-- START CENTERED WHITE CONTAINER -->
            <span class="preheader" style="color: transparent; display: none; height: 0; max-height: 0; max-width: 0; opacity: 0; overflow: hidden; mso-hide: all; visibility: hidden; width: 0;">This is preheader text. Some clients will show this text as a preview.</span>
            <table class="main" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%; background: #ffffff; border-radius: 3px;">

              <!-- START MAIN CONTENT AREA -->
              <tr>
                <td class="wrapper" style="font-family: sans-serif; font-size: 14px; vertical-align: top; box-sizing: border-box; padding: 20px;">
                  <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%;">
                    <tr>
                      <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;">

                      <!-- START DYNAMIC CONTENT AREA -->
                      $content
                      <!-- END DYNAMIC CONTENT AREA -->

                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

            <!-- END MAIN CONTENT AREA -->
            </table>

            <!-- START FOOTER -->
            <div class="footer" style="clear: both; Margin-top: 10px; text-align: center; width: 100%;">
              <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%;">
                <tr>
                  <td class="content-block powered-by" style="font-family: sans-serif; vertical-align: top; padding-bottom: 10px; padding-top: 10px; font-size: 12px; color: #999999; text-align: center;">
                    Powered by open source software: <a href="https://github.com/tristanlatr/alt_job" style="color: #999999; font-size: 12px; text-align: center; text-decoration: none;">Alt Job</a>.
                  </td>
                </tr>
              </table>
            </div>
            <!-- END FOOTER -->

          <!-- END CENTERED WHITE CONTAINER -->
          </div>
        </td>
        <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;">&nbsp;</td>
      </tr>
    </table>
  </body>
</html>""")