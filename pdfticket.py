# coding: utf-8
import os

from os.path import isdir, isfile, dirname

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.platypus import Paragraph, Frame, SimpleDocTemplate, PageTemplate
from reportlab.lib.colors import darkorange
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch

from models import User


class PDFTicket:
    def __init__(self, ticket, web_root):
        self.ticket = ticket
        self.web_root = web_root

        self.filename = 'cache/{}/billet.pdf'.format(self.ticket.qr_token)
        self.qrcode = '{}/qr/{}'.format(self.web_root, self.ticket.qr_token)

        user = User.query.filter(User.id == self.ticket.owner_id).one()
        self.fullname = '{} {}'.format(user.firstname, user.lastname)
        self.username = user.username

    def get_filename(self):
        return self.filename

    def build(self):
        if isfile(self.filename):
            return

        if not isdir(dirname(self.filename)):
            os.makedirs(dirname(self.filename))

        # If you ever need to add or remove content from the PDF, use these
        # frames bellow as a starting point. You will need to reposition
        # everything by hand until you get the desired result. Remove
        # `showBoundary=1` when you're done.

    # frame1 = Frame(inch, inch * 8.75, inch * 6.5, inch * 1.25, showBoundary=1)
    # frame2 = Frame(inch, inch * 5.25, inch * 3.5, inch * 3.5, showBoundary=1)
    # frame3 = Frame(inch * 4.5, inch * 7, inch * 3, inch * 1.7, showBoundary=1)
    # frame4 = Frame(inch, inch, inch * 6.5, inch * 4.25, showBoundary=1)

        # Every frame is used to display some of the content. Once a frame is
        # full, the content is sent to the next frame. Some trickery are
        # used to ensure that content is display to the next frame even if
        # there is place left (see `spaceBefore=999` down bellow).
        frame1 = Frame(inch, inch * 8.75, inch * 6.5, inch * 1.25)
        frame2 = Frame(inch * 0.7, inch * 5.4, inch * 3.5, inch * 3.5)
        frame3 = Frame(inch * 4.2, inch * 5.6, inch * 3.3, inch * 3)
        frame4 = Frame(inch, inch, inch * 6.5, inch * 4.4)
        frame5 = Frame(inch, inch, inch * 6.5, inch * 3.4)
        frames = [frame1, frame2, frame3, frame4, frame5]

        # Creating the document to the proper format
        doc = SimpleDocTemplate(self.filename, pagesize=letter)

        # Added a single page template with our frames
        doc.addPageTemplates([PageTemplate(frames=frames)])

        # Creating the QR code drawing
        qrw = QrCodeWidget(self.qrcode)
        b = qrw.getBounds()
        w = b[2] - b[0]
        h = b[3] - b[1]
        d = Drawing(240, 240, transform=[240 / w, 0, 0, 240 / h, 0, 0])
        d.add(qrw)

        if self.ticket.seat_num:
            ticket_type = 'BYOC'
            ticket_seat = self.ticket.seat_num
        else:
            ticket_type = 'Console'
            ticket_seat = '-'

        # Creating all the needed paragraph with their corresponding style
        name = Paragraph('Nom: {}'.format(self.fullname), style_n1)
        username = Paragraph('Pseudonyme: {}'.format(self.username), style_n1)
        ttype = Paragraph('Type: {}'.format(ticket_type), style_n1)
        seat = Paragraph('Siège: {}'.format(ticket_seat), style_n1)

        title = Paragraph('Billet LAN Montmorency 2015', style_h1)
        info = Paragraph("""De 10h samedi le 14 novembre jusqu'à 16h dimanche
            le 15 novembre""", style_h2)
        warning = Paragraph("""Attention! Vous devrez présenter votre carte
            étudiante lors de votre enregistrement, sans quoi vous devrez
            payer la différence du billet en argent comptant ou l'accès au
            site vous sera refusé.""", style_n2)
        note = Paragraph("""Veuillez présenter ce billet à l'acceuil lors de
            votre arrivée au LAN. Notez que vous devrez présenter une pièce
            d’identité avec photo lors de votre enregistrement. Il est
            recommandé de sauvegarder ce PDF sur un appareil mobile, mais il
            est aussi possible de l'imprimer.""", style_n3)

        # Creating the story in the right order
        story = []
        story.append(title)
        story.append(info)
        story.append(d)
        story.append(name)
        story.append(username)
        story.append(ttype)
        story.append(seat)
        if self.ticket.discount_amount:
            story.append(warning)
        story.append(note)

        # Build and save the document
        doc.build(story)


style_h1 = ParagraphStyle(name='Heading1',
                          fontName='Times-Bold',
                          fontSize=32,
                          leading=40,
                          spaceAfter=6
                          )
style_h2 = ParagraphStyle(name='Heading2',
                          fontName='Times-Roman',
                          fontSize=16,
                          leading=20,
                          spaceBefore=6
                          )
style_n1 = ParagraphStyle(name='Normal',
                          fontName='Helvetica',
                          fontSize=14,
                          leading=18,
                          spaceBefore=6
                          )
style_n2 = ParagraphStyle(name='Warning',
                          fontName='Helvetica',
                          fontSize=14,
                          leading=14,
                          # Needed to force push the content to the next frame
                          spaceBefore=999,
                          textColor=darkorange
                          )
style_n3 = ParagraphStyle(name='Notice',
                          fontName='Helvetica',
                          fontSize=12,
                          leading=12,
                          # Needed to force push the content to the next frame
                          spaceBefore=999
                          )
