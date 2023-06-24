from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

def generate_certificate(self, text_array, image1_path=None, image2_path=None, response=None):

    page_width, page_height = landscape((11*inch, 6.5*inch))  # Tamanho personalizado com a proporção de uma página A4 em paisagem

    c = canvas.Canvas(response, pagesize=(page_width, page_height))

    # Calcula o tamanho máximo permitido para a imagem
    image_width = page_width * 0.4
    image_height = page_height * 0.2

    # Carrega as imagens, redimensiona e desenha no canvas
    if image1_path:
        image1 = Image.open(image1_path)
        image1.thumbnail((image_width, image_height))
        x = (page_width - image1.width) / 2
        c.drawImage(ImageReader(image1), x, page_height - image1.height - 60, width=image1.width, height=image1.height, mask='auto')

    # Centraliza cada linha de texto
    font_size = 12
    y_position = page_height / 2
    for text in text_array:
        text_width = c.stringWidth(text)
        c.drawCentredString(page_width / 2, y_position, text)
        y_position -= font_size * 1.2

    # Carrega as imagens, redimensiona e desenha no canvas
    if image2_path:
        image2 = Image.open(image2_path)
        image2.thumbnail((image_width, image_height))
        x = (page_width - image2.width) / 2
        c.drawImage(ImageReader(image2), x, 60, width=image2.width, height=image2.height, mask='auto')

    # Fecha o arquivo PDF
    c.save()

    return response
