import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


def enviar_email_codigo_recuperacao(email_destino: str, codigo_pin: str) -> bool:
    """
    Envia um e-mail HTML contendo o código PIN de 6 dígitos para recuperação de senha.
    Se o SMTP não estiver configurado ou ocorrer falha, faz fallback exibindo o código nos logs.
    """
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning(
            f"[SMTP DEV] Configuração SMTP não preenchida. Código PIN para '{email_destino}': {codigo_pin}"
        )
        return False

    assunto = "🔑 Gestão Motoca — Código para Redefinição de Senha"
    remetente = settings.smtp_from or settings.smtp_user

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }}
        .card {{ max-width: 480px; margin: 0 auto; background: #ffffff; border-radius: 12px; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-top: 5px solid #eab308; }}
        .header {{ text-align: center; margin-bottom: 24px; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #1e293b; }}
        .pin-box {{ background-color: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 8px; padding: 16px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #eab308; margin: 24px 0; }}
        .info {{ color: #64748b; font-size: 14px; line-height: 1.5; text-align: center; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #94a3b8; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 16px; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <div class="logo">🏍️ Gestão Motoca</div>
        </div>
        <p style="color: #334155; font-size: 16px; margin-bottom: 8px;">Olá,</p>
        <p style="color: #475569; font-size: 15px; line-height: 1.5;">
          Recebemos uma solicitação para redefinir a senha da sua conta no <strong>Gestão Motoca</strong>. Use o código de verificação abaixo:
        </p>
        
        <div class="pin-box">{codigo_pin}</div>

        <p class="info">
          Este código é válido por <strong>15 minutos</strong>.<br>
          Se você não solicitou a alteração, pode ignorar este e-mail com segurança.
        </p>
        
        <div class="footer">
          Gestão Motoca — O controle financeiro real do entregador.
        </div>
      </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = email_destino

    part_text = MIMEText(
        f"Seu código de redefinição de senha no Gestão Motoca é: {codigo_pin}. Válido por 15 minutos.",
        "plain",
        "utf-8",
    )
    part_html = MIMEText(html_content, "html", "utf-8")

    msg.attach(part_text)
    msg.attach(part_html)

    try:
        if settings.smtp_port == 465:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(remetente, [email_destino], msg.as_string())
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                if settings.smtp_tls:
                    server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(remetente, [email_destino], msg.as_string())

        logger.info(f"[SMTP SUCCESS] E-mail de recuperação enviado com sucesso para '{email_destino}'")
        return True
    except Exception as e:
        logger.error(f"[SMTP ERROR] Falha ao enviar e-mail para '{email_destino}': {str(e)}")
        logger.info(f"[SMTP FALLBACK] Código PIN para '{email_destino}': {codigo_pin}")
        return False
