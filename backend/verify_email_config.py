import os
print("Starting verification script...")
try:
    from app import create_app
    from app.configs.extensions import mail
    from flask_mail import Message
    print("Imports successful.")
except Exception as e:
    print(f"Import failed: {e}")
    exit(1)

print("Creating app...")
try:
    app = create_app()
    print("App created.")
except Exception as e:
    print(f"Failed to create app: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

with app.app_context():
    # Print config (masking password)
    print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
    print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
    print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
    pwd = app.config.get('MAIL_PASSWORD')
    print(f"MAIL_PASSWORD: {'*' * (len(pwd) if pwd else 0)}")
    
    sender = app.config.get('MAIL_DEFAULT_SENDER') or 'noreply@quizzy.com'

    msg = Message(
        subject="Test Email from Verif Script",
        recipients=[app.config.get('MAIL_USERNAME')], # Send to self
        body="If you see this, email configuration is correct!",
        sender=sender
    )
    
    print("\nAttempting to send email...")
    try:
        mail.send(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"FAILED to send email.\nError: {e}")
        import traceback
        traceback.print_exc()
