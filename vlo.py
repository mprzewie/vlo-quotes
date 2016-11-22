# -*- coding: utf-8 -*-
import mechanicalsoup
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (Flowable, Paragraph, SimpleDocTemplate, Spacer)
from reportlab.pdfbase import pdfmetrics


class Quote:
    def __init__(self, div):
        self.div = div

    def who(self):
        return self.div.find_all('div', class_='kto')

    def what(self):
        return self.div.find_all('div', class_='co')

    def to_paragraph(self, tag, styles):
        what_went_down = tag.find('p')
        if what_went_down is None:
            return [Paragraph(tag.text, styles)]
        else:
            return [Paragraph(what_went_down.text, Stylesheets().wwd_style()),
                    Paragraph(tag.text[len(what_went_down.text):], styles)]

    def to_printable(self):
        res = []
        j = 0
        if len(self.who()) < len(self.what()):
            res += (self.to_paragraph(self.what()[j], Stylesheets().what_style()))
            j += 1
        for i in range(0, len(self.who())):
            res += (self.to_paragraph(self.who()[i], Stylesheets().who_style()))
            res.append(Spacer(0, 0.15 * inch))
            res += (self.to_paragraph(self.what()[j], Stylesheets().what_style()))
            res.append(Spacer(0, 0.1 * inch))
            j += 1
        res.append(MCLine(500))
        res.append(Spacer(0, 0.1 * inch))
        return res


class MCLine(Flowable):
    def __init__(self, width, height=0):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def __repr__(self):
        return "Line(w=%s)" % self.width

    def draw(self):
        """
        draw the line
        """
        self.canv.line(0, self.height, self.width, self.height)


class PDF:
    def __init__(self, name):
        self.canvas = SimpleDocTemplate(name + ".pdf", pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.spacer = Spacer(0, 0.25 * inch)
        self.line = 750

    def writeToPdf(self, quotes):
        self.canvas.build(quotes)


class Stylesheets:
    def __init__(self):
        pdfmetrics.registerFont(TTFont('Arial',
                                       "fonts/arial.ttf"))
        self.style_sheet = getSampleStyleSheet()
        self.style_sheet.add(ParagraphStyle(name='Who',
                                            fontName='arial',
                                            fontSize=11,
                                            leading=12))

        self.style_sheet.add(ParagraphStyle(name='What',
                                            fontName='arial',
                                            fontSize=10,
                                            leading=12,
                                            leftIndent=15))
        self.style_sheet.add(ParagraphStyle(name='WWD',
                                            fontName='arial',
                                            fontSize=10,
                                            leading=20,
                                            leftIndent=15,
                                            textColor='grey'))

    def who_style(self):
        return self.style_sheet["Who"]

    def what_style(self):
        return self.style_sheet["What"]

    def wwd_style(self):
        return self.style_sheet["WWD"]


browser = mechanicalsoup.Browser()
page = browser.get("http://users.v-lo.krakow.pl/~mkocot/najlepsze.php?s=1" )
hrefs=page.soup.find_all('div', class_='opcje')[1].find_all('a')
max_page=int(hrefs[len(hrefs)-2].text)
quotes_from_page = []
for i in range(1, max_page+1):
    print("Getting quotes from page " + str(i) + "/"+str(max_page))
    page = browser.get("http://users.v-lo.krakow.pl/~mkocot/najlepsze.php?s=" + str(i))
    quotes_from_page += (page.soup.find_all('div', class_='kartka'))

printable_quotes = []
for quote in quotes_from_page:
    printable_quotes += (Quote(quote).to_printable())
pdf = PDF("vlo")
pdf.writeToPdf(printable_quotes)
