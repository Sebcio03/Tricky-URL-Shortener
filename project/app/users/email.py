import pyotp
from fastapi_mail import FastMail, MessageSchema

from app import settings


async def send_account_verification_mail(recipent, secret):

    code = pyotp.TOTP(secret).now()

    template = settings.env.get_template("verify_user_account.html")
    body = template.render(code=code, domain=settings.DOMAIN)

    message = MessageSchema(
        subject=f"Verify your account on {settings.DOMAIN} with code {code}",
        recipients=[recipent],
        subtype="html",
    )
    message.template_body = body

    fm = FastMail(settings.conf)
    await fm.send_message(message)
