import smtplib


def enviarCorreo(data):
	gmail_user = ""
	gmail_password = ""

	sent_from = gmail_user
	to = data["destinataries"]
	subject = data["subject"]
	body = data["body"]

	email_text = """\
	From: %s
	To: %s
	Subject: %s

	%s
	""" % (sent_from, ", ".join(to), subject, body)

	feedback=""

	try:
		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		server.ehlo()
		server.login(gmail_user, gmail_password)
		server.sendmail(sent_from, to, email_text)
		server.close()

		feedback = 'Correo Enviado!'
	except:
		feedback = 'No se pudo enviar el correo...'


	print(feedback)

	return feedback

