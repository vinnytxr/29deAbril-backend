from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

def generate_certificate(self, text_array, image1_path=None, image2_path=None, output_file_address=None, response=None):

    # print(response)

    # p = canvas.Canvas(response, pagesize=letter)
    # p.drawString(100, 100, "Olá mundo!")
    # p.showPage()
    # p.save()

    # return response

    # Define o tamanho da página em modo paisagem e cria o objeto canvas
    c = canvas.Canvas(response, pagesize=landscape(letter))

    # Calcula o tamanho máximo permitido para a imagem
    image_width = letter[0] * 0.4
    image_height = letter[1] * 0.2

    # Carrega as imagens, redimensiona e desenha no canvas
    if image1_path:
        image1 = Image.open(image1_path)
        image1.thumbnail((image_width, image_height))
        x = (letter[1] - image1.width) / 2
        c.drawImage(ImageReader(image1), x, c._pagesize[1] - image1.height - 120, width=image1.width, height=image1.height, mask='auto')

    # Centraliza cada linha de texto
    font_size = 12
    y_position = letter[0] / 2
    for text in text_array:
        text_width = c.stringWidth(text)
        c.drawCentredString(letter[1] / 2, y_position, text)
        y_position -= font_size * 1.2

    # Carrega as imagens, redimensiona e desenha no canvas
    if image2_path:
        image2 = Image.open(image2_path)
        image2.thumbnail((image_width, image_height))
        x = (letter[1] - image2.width) / 2
        c.drawImage(ImageReader(image2), x, 120, width=image2.width, height=image2.height, mask='auto')

    # Fecha o arquivo PDF
    c.save()

    return response

# # Exemplo de uso
# pdf_path = generate_certificate(["Alessandro Neves dos Santos", "Concluiu o curso Curso de Python para Iniciantes", "em 14 de maio de 2023", "", "", "", "Professor: Alessandro Neves dos Santos"], "./a.png", "./c.png", "output.pdf")
# print(f"Arquivo PDF gerado em: {pdf_path}")
