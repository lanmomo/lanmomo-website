import threading
import time
import requests


def _def_timeoutfn(x):
    if x <= 3:
        return 1 * 60
    else:
        return 15 * 60


def _send_mailgun_api(to_email, to_name, subject, message, sender, api_key,
                      domain, timeoutfn, times):
    count = 1
    while count <= times:
        timeout = timeoutfn(count)
        begin_ts = time.time()
        try:
            request_url = 'https://api.mailgun.net/v3/%s/messages' % domain

            request = requests.post(request_url, auth=('api', api_key), data={
                'from': 'LAN Montmorency <%s>' % sender,
                'to': '%s <%s>' % (to_name, to_email),
                'subject': subject,
                'text': message
            })
            if request.status_code == 200:
                return
            raise Exception(request.text)
        except Exception as e:
            print(e)
            # Erreur de connexion ou d'envoie de courriel
            #
            # Le temps à sleep restant est calculé avec:
            #    `le temps de début` + `le timeout` - `le temps maintenant`.
            # Si c'est supérieur à 0, on sleep ce temps la.
            if count < times:
                time.sleep(max(0, begin_ts + timeout - time.time()))

        count += 1
    # Si le code se rend ici, c'est que tous les essais ont échoués.
    # TODO log here
    return


def send_email(to_email, to_name, subject, message, sender, api_key, domain,
               timeoutfn=_def_timeoutfn, times=13):
    """
    Envoyer un courriel en background avec les informations données.
    `times` est le nombres de fois à essayer d'envoyer le courriel.
    `timeoutfn` est une fonction qui doit retourner un timeout en secondes
                en fonction du numéro de l'essai donné.
    """
    threading.Thread(target=_send_mailgun_api, args=(
        to_email, to_name, subject, message, sender, api_key, domain,
        timeoutfn, times)).start()
