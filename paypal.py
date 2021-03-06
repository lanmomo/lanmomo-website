import paypalrestsdk

from paypalrestsdk import Payment


class Paypal():
    def __init__(self):
        self.return_url = None
        self.cancel_url = None

    def configure(self, client_id, client_secret, mode,
                  return_url, cancel_url):
        paypalrestsdk. \
            configure({
                      "mode": mode,
                      "client_id": client_id,
                      "client_secret": client_secret})
        self.return_url = return_url
        self.cancel_url = cancel_url

    def create(self, ticket):
        if ticket.seat_num:
            item_name = "Billet LAN Montmorency 2015 BYOC {}" \
                .format(ticket.seat_num)
        else:
            item_name = "Billet LAN Montmorency 2015 Console"

        items = [{
            "name": item_name,
            "sku": "SKU2015REF{}".format(ticket.id),
            "price": "{:.2f}".format(ticket.price),
            "currency": "CAD",
            "quantity": 1
        }]

        if ticket.discount_amount > 0:
            items.append({
                "name": "Rabais pour étudiant du Collège Montmorency",
                "sku": "SKU2015RABAISMOMO",
                "price": "-{:.2f}".format(ticket.discount_amount),
                "currency": "CAD",
                "quantity": 1
            })

        payment = Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": self.return_url,
                "cancel_url": self.cancel_url
            },
            "transactions": [{
                "item_list": {
                    "items": items
                },
                "amount": {
                    "total": "{:.2f}".format(ticket.total),
                    "currency": "CAD"
                },
                "description": "Achat de votre billet LAN Montmorency 2015"
            }]
        })

        if payment.create():
            temp_payment = {}

            for link in payment.links:
                if link.method == "REDIRECT":
                    # Convert to str to avoid google appengine unicode issue
                    # https://github.com/paypal/rest-api-sdk-python/pull/58
                    temp_payment['redirect_url'] = str(link.href)

            temp_payment['paypal_payment_id'] = payment['id']
            return temp_payment
        else:
            raise Exception("Erreur lors de la création du paiment: {}"
                            .format(payment.error))
