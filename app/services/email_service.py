"""
Servicio de envío de emails
Soporta Resend, Gmail SMTP y modo desarrollo
"""
import resend
from typing import Optional
from app.config import settings
from jinja2 import Template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configurar Resend
if settings.EMAIL_PROVIDER == "resend" and settings.RESEND_API_KEY:
    resend.api_key = settings.RESEND_API_KEY

class EmailService:
    """Servicio para envío de emails con múltiples proveedores"""
    
    @staticmethod
    def send_verification_email(email: str, username: str, token: str) -> bool:
        """
        Envía email de verificación
        
        Args:
            email: Email del destinatario
            username: Nombre del usuario
            token: Token de verificación
        
        Returns:
            bool: True si se envió correctamente
        """
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        subject = "Verifica tu email - Pet HealthCare"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px;
                    border-radius: 10px;
                    text-align: center;
                }}
                .content {{
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    margin-top: 20px;
                }}
                .logo {{
                    font-size: 40px;
                    margin-bottom: 10px;
                }}
                h1 {{
                    color: #667eea;
                    margin-bottom: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 30px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 12px;
                    color: #666;
                }}
                .token {{
                    background: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    font-family: monospace;
                    word-break: break-all;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">🐾</div>
                <h2 style="color: white; margin: 0;">Pet HealthCare</h2>
            </div>
            
            <div class="content">
                <h1>¡Bienvenido, {username}! 🎉</h1>
                
                <p>Gracias por registrarte en <strong>Pet HealthCare</strong>, tu plataforma para cuidar la salud de tus mascotas.</p>
                
                <p>Para completar tu registro, por favor verifica tu email haciendo clic en el botón:</p>
                
                <a href="{verification_url}" class="button">Verificar Email</a>
                
                <p style="margin-top: 30px; font-size: 14px; color: #666;">
                    Si el botón no funciona, copia y pega este enlace en tu navegador:
                </p>
                <div class="token">{verification_url}</div>
                
                <div class="footer">
                    <p>Este enlace expirará en {settings.EMAIL_VERIFICATION_EXPIRE_HOURS} horas.</p>
                    <p>Si no creaste esta cuenta, puedes ignorar este email.</p>
                    <p style="margin-top: 20px;">
                        <strong>Pet HealthCare</strong><br>
                        Cuidamos de quienes más amas 💚
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        ¡Bienvenido a Pet HealthCare, {username}!
        
        Gracias por registrarte. Para completar tu registro, verifica tu email usando este enlace:
        
        {verification_url}
        
        Este enlace expirará en {settings.EMAIL_VERIFICATION_EXPIRE_HOURS} horas.
        
        Si no creaste esta cuenta, puedes ignorar este email.
        
        ---
        Pet HealthCare - Cuidamos de quienes más amas
        """
        
        return EmailService._send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    @staticmethod
    def send_password_reset_email(email: str, username: str, token: str) -> bool:
        """
        Envía email de reseteo de contraseña
        
        Args:
            email: Email del destinatario
            username: Nombre del usuario
            token: Token de reseteo
        
        Returns:
            bool: True si se envió correctamente
        """
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        subject = "Resetea tu contraseña - Pet HealthCare"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px;
                    border-radius: 10px;
                    text-align: center;
                }}
                .content {{
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    margin-top: 20px;
                }}
                .logo {{
                    font-size: 40px;
                    margin-bottom: 10px;
                }}
                h1 {{
                    color: #667eea;
                    margin-bottom: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 30px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 12px;
                    color: #666;
                }}
                .token {{
                    background: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    font-family: monospace;
                    word-break: break-all;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">🔐</div>
                <h2 style="color: white; margin: 0;">Pet HealthCare</h2>
            </div>
            
            <div class="content">
                <h1>Reseteo de Contraseña</h1>
                
                <p>Hola <strong>{username}</strong>,</p>
                
                <p>Recibimos una solicitud para resetear la contraseña de tu cuenta en Pet HealthCare.</p>
                
                <a href="{reset_url}" class="button">Resetear Contraseña</a>
                
                <p style="margin-top: 30px; font-size: 14px; color: #666;">
                    Si el botón no funciona, copia y pega este enlace en tu navegador:
                </p>
                <div class="token">{reset_url}</div>
                
                <div class="warning">
                    <strong>⚠️ Importante:</strong><br>
                    Este enlace expirará en <strong>{settings.PASSWORD_RESET_EXPIRE_HOURS} hora(s)</strong>.<br>
                    Si no solicitaste este cambio, ignora este email y tu contraseña permanecerá sin cambios.
                </div>
                
                <div class="footer">
                    <p>Por tu seguridad, nunca compartas este enlace con nadie.</p>
                    <p style="margin-top: 20px;">
                        <strong>Pet HealthCare</strong><br>
                        Cuidamos de quienes más amas 💚
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Reseteo de Contraseña - Pet HealthCare
        
        Hola {username},
        
        Recibimos una solicitud para resetear la contraseña de tu cuenta.
        
        Usa este enlace para crear una nueva contraseña:
        {reset_url}
        
        Este enlace expirará en {settings.PASSWORD_RESET_EXPIRE_HOURS} hora(s).
        
        Si no solicitaste este cambio, ignora este email.
        
        Por tu seguridad, nunca compartas este enlace con nadie.
        
        ---
        Pet HealthCare - Cuidamos de quienes más amas
        """
        
        return EmailService._send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    @staticmethod
    def _send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """
        Método interno para enviar emails usando el proveedor configurado
        
        Args:
            to_email: Email del destinatario
            subject: Asunto del email
            html_content: Contenido HTML
            text_content: Contenido en texto plano
        
        Returns:
            bool: True si se envió correctamente
        """
        try:
            if settings.EMAIL_PROVIDER == "resend":
                return EmailService._send_with_resend(
                    to_email, subject, html_content, text_content
                )
            elif settings.EMAIL_PROVIDER == "smtp":
                return EmailService._send_with_smtp(
                    to_email, subject, html_content, text_content
                )
            else:
                # Modo desarrollo - solo imprimir
                print(f"\n{'='*60}")
                print(f"📧 EMAIL (MODO DESARROLLO)")
                print(f"{'='*60}")
                print(f"Para: {to_email}")
                print(f"Asunto: {subject}")
                print(f"Contenido:\n{text_content}")
                print(f"{'='*60}\n")
                return True
        except Exception as e:
            print(f"❌ Error enviando email: {str(e)}")
            return False
    
    @staticmethod
    def _send_with_resend(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """Envía email usando Resend"""
        try:
            params = {
                "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content
            }
            
            response = resend.Emails.send(params)
            print(f"✅ Email enviado via Resend: {response}")
            return True
        except Exception as e:
            print(f"❌ Error con Resend: {str(e)}")
            return False
    
    @staticmethod
    def _send_with_smtp(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """Envía email usando SMTP (Gmail u otro)"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.SMTP_USER}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Agregar contenido texto y HTML
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Conectar y enviar
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            print(f"✅ Email enviado via SMTP a {to_email}")
            return True
        except Exception as e:
            print(f"❌ Error con SMTP: {str(e)}")
            return False