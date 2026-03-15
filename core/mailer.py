# core/mailer.py
from config import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mailer():
    def __init__(self):
        pass

    def sendMail(self, matches, receiverEmail):
        matchBlock = """
          <tr>
            <td style="padding:20px;">
              <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" class="match-card" style="width:100%; background-color:#ffffff; border:1px solid #e5e7eb; border-radius:8px;">
                <tr>
                  <td style="padding:30px 20px 20px;">
                    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                      <tr>
                        <td width="45%" align="center" valign="top" style="text-align:center; vertical-align:top;">
                          <img src="{{team1_logo}}" alt="{{team1_name}}" width="80" height="80" class="team-logo" style="display:block; width:80px; max-width:80px; height:auto; margin:0 auto; border:0;">
                          <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" style="margin:12px auto 0 auto;">
                            <tr>
                              <td width="110" class="team-name" style="width:110px; font-family:Arial, Helvetica, sans-serif; font-size:16px; font-weight:bold; line-height:1.4; color:#111827; text-align:center;">
                                {{team1_name}}
                              </td>
                            </tr>
                          </table>
                        </td>

                        <td width="10%" align="center" valign="middle" style="text-align:center; vertical-align:middle;">
                          <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center">
                            <tr>
                              <td class="vs-badge" style="background-color:#f3f4f6; border:2px solid #e5e7eb; border-radius:999px; padding:8px 12px; font-family:Arial, Helvetica, sans-serif; font-size:13px; font-weight:bold; line-height:1; color:#6b7280; text-align:center;">
                                VS
                              </td>
                            </tr>
                          </table>
                        </td>

                        <td width="45%" align="center" valign="top" style="text-align:center; vertical-align:top;">
                          <img src="{{team2_logo}}" alt="{{team2_name}}" width="80" height="80" class="team-logo" style="display:block; width:80px; max-width:80px; height:auto; margin:0 auto; border:0;">
                          <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" style="margin:12px auto 0 auto;">
                            <tr>
                              <td width="110" class="team-name" style="width:110px; font-family:Arial, Helvetica, sans-serif; font-size:16px; font-weight:bold; line-height:1.4; color:#111827; text-align:center;">
                                {{team2_name}}
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>

                <tr>
                  <td align="center" style="padding:20px; text-align:center;">
                    <p style="margin:0 0 8px 0; font-family:Arial, Helvetica, sans-serif; font-size:15px; font-weight:600; line-height:1.4; color:#059669; text-align:center;">
                      {{match_date}}
                    </p>
                    <p style="margin:0; font-family:Arial, Helvetica, sans-serif; font-size:13px; line-height:1.4; color:#6b7280; text-align:center; text-transform:uppercase; letter-spacing:0.5px;">
                      {{competition}}
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td height="10" style="height:10px; line-height:10px; font-size:0;">&nbsp;</td>
          </tr>
        """

        emailTemplate = """<!DOCTYPE html>
    <html lang="en" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="x-apple-disable-message-reformatting">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Football Match Notifications</title>
    <style>
      body, table, td, p, a, span, h1 {
        font-family: Arial, Helvetica, sans-serif !important;
      }

      .email-container {
        width: 100%;
        max-width: 600px;
      }

      @media only screen and (max-width: 600px) {
        .email-container {
          width: 100% !important;
          max-width: 100% !important;
        }

        .team-logo {
          width: 56px !important;
          max-width: 56px !important;
          height: auto !important;
        }

        .team-name {
          width: 84px !important;
          font-size: 14px !important;
        }

        .vs-badge {
          font-size: 12px !important;
          padding: 6px 10px !important;
        }
      }
    </style>
    </head>
    <body style="margin:0; padding:0; background-color:#f3f4f6; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%;">
      <center style="width:100%; background-color:#f3f4f6;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="width:100%; background-color:#f3f4f6; margin:0; padding:0;">
          <tr>
            <td align="center" style="padding:20px 10px;">
              <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600" class="email-container" style="width:100%; max-width:600px; background-color:#ffffff; border:1px solid #e5e7eb; border-radius:12px;">
                <tr>
                  <td align="center" style="padding:40px 20px 30px; background-color:#059669; border-radius:12px 12px 0 0;">
                    <h1 style="margin:0; font-family:Arial, Helvetica, sans-serif; font-size:28px; font-weight:bold; line-height:1.2; color:#ffffff; text-transform:uppercase; letter-spacing:1px;">
                      Match Notifications
                    </h1>
                    <p style="margin:10px 0 0 0; font-family:Arial, Helvetica, sans-serif; font-size:14px; line-height:1.4; color:#d1fae5;">
                      Stay updated with upcoming fixtures
                    </p>
                  </td>
                </tr>

                {{matches}}

                <tr>
                  <td align="center" style="padding:30px 20px; background-color:#f9fafb; border-top:1px solid #e5e7eb; border-radius:0 0 12px 12px;">
                    <p style="margin:0; font-family:Arial, Helvetica, sans-serif; font-size:12px; line-height:1.4; color:#6b7280; text-align:center;">
                      You received this notification because you subscribed to match updates.
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </center>
    </body>
    </html>
    """

        try:
            matchesHtml = ""
            for m in matches:
                block = matchBlock
                block = block.replace("{{team1_logo}}", m["team1_logo"])
                block = block.replace("{{team2_logo}}", m["team2_logo"])
                block = block.replace("{{team1_name}}", m["team1_name"])
                block = block.replace("{{team2_name}}", m["team2_name"])
                block = block.replace("{{match_date}}", m["match_date"])
                block = block.replace("{{competition}}", m["competition"])
                matchesHtml += block

            html = emailTemplate.replace("{{matches}}", matchesHtml)

            smtpServer = SMTP_SERVER
            port = SMTP_PORT
            senderEmail = SENDER_EMAIL
            appPassword = APP_PASSWORD

            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Match Notifications"
            msg["From"] = senderEmail
            msg["To"] = receiverEmail
            msg.attach(MIMEText(html, "html", "utf-8"))

            server = smtplib.SMTP(smtpServer, port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(senderEmail, appPassword)
            server.sendmail(senderEmail, [receiverEmail], msg.as_string())
            server.quit()

            return None
        except Exception as e:
            return e