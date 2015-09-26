import threading
import time
from smtplib import SMTP
from email.mime.text import MIMEText


def _def_timeoutfn(x):
    if x <= 3:
        return 1 * 60
    else:
        return 15 * 60


def _send_email(smtp, email, times, timeoutfn):
    count = 1
    while count <= times:
        timeout = timeoutfn(count)
        begin_ts = time.time()
        try:
            with SMTP(host=smtp['host'], port=smtp['port'],
                      timeout=timeout) as co:
                # Si on est rendu ici c'est que la connexion est ok
                msg = MIMEText(email['message'].encode('utf-8'),
                               'html', 'utf-8')
                msg['Subject'] = email['subject']
                msg['From'] = 'LAN Montmorency <%s>' % smtp['user']
                msg['To'] = '%s <%s>' % (email['name'].encode('utf-8'),
                                         email['address'])

                co.starttls()
                co.login(user=smtp['user'], password=smtp['pass'])
                co.sendmail(smtp['user'], email['address'], msg.as_string())
                # Si on arrive ici, c'est qu'il n'y a pas d'erreurs.
                return
        except:
            # Erreur de connexion ou d'envoie de courriel
            #
            # Le temps à sleep restant est calculé avec:
            #    `le temps de début` + `le timeout` - `le temps maintenant`.
            # Si c'est supérieur à 0, on sleep ce temps la.
            time.sleep(max(0, begin_ts + timeout - time.time()))

        count += 1
    # Si le code se rend ici, c'est que tous les essais ont échoués.
    # TODO log here


def send_email(to_email, to_name, subject, message,
               smtp_user, smtp_pass, host='mail.lanmomo.org', port=587,
               times=13, timeoutfn=_def_timeoutfn):
    """
    Envoyer un courriel en background avec les informations données.
    `times` est le nombres de fois à essayer d'envoyer le courriel.
    `timeoutfn` est une fonction qui doit retourner un timeout en secondes
                en fonction du numéro de l'essai donné.
    """
    smtp = {'user': smtp_user,
            'pass': smtp_pass,
            'host': host,
            'port': port}
    email = {'address': to_email,
             'name': to_name,
             'subject': subject,
             'message': message}
    threading.Thread(target=_send_email,
                     args=(smtp, email, times, timeoutfn)).start()
