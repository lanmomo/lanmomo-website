import threading
import time
import requests

import app


def _def_timeoutfn(x):
    if x <= 3:
        return 1 * 60
    else:
        return 15 * 60


def _prepapre_attachments(attachement_files):
    attachements = []

    if attachement_files:
        for file in attachement_files:
            attachements.append(("attachment", open(file, 'rb')))

    return attachements


def _send_mailgun_api(to_email, to_name, subject, message, sender, api_key,
                      domain, timeoutfn, times, attachements):
    count = 1
    while count <= times:
        timeout = timeoutfn(count)
        begin_ts = time.time()
        try:
            request_url = 'https://api.mailgun.net/v3/%s/messages' % domain
            attachements_mailgun = _prepapre_attachments(attachements)

            request = requests.post(
                request_url,
                auth=('api', api_key),
                data={
                    'from': 'LAN Montmorency <%s>' % sender,
                    'to': '%s <%s>' % (to_name, to_email),
                    'subject': subject,
                    'text': message,
                    'html': message,
                },
                files=attachements_mailgun
            )

            if request.status_code == 200:
                return
            raise Exception(request.text)
        except Exception as e:
            app.get_logger().error(
                'Exception lors de l\'envoie de courriel à "%s": "%s"'
                % (to_email, str(e)))
            # Erreur de connexion ou d'envoie de courriel
            #
            # Le temps à sleep restant est calculé avec:
            #    `le temps de début` + `le timeout` - `le temps maintenant`.
            # Si c'est supérieur à 0, on sleep ce temps la.
            if count < times:
                time.sleep(max(0, begin_ts + timeout - time.time()))

        count += 1
    # Si le code se rend ici, c'est que tous les essais ont échoués.
    app.get_logger().critical(
        'Échec lors de l\'envoie de courriel à "%s": "%s"'
        % (to_email, str(e)))
    return


def send_email(to_email, to_name, subject, message, sender, api_key, domain,
               timeoutfn=_def_timeoutfn, times=13, attachements=None):
    """
    Envoyer un courriel en background avec les informations données.
    `times` est le nombres de fois à essayer d'envoyer le courriel.
    `timeoutfn` est une fonction qui doit retourner un timeout en secondes
                en fonction du numéro de l'essai donné.
    """
    threading.Thread(target=_send_mailgun_api, args=(
        to_email, to_name, subject, message, sender, api_key, domain,
        timeoutfn, times, attachements)).start()
