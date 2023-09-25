from io import BytesIO
from pathlib import Path

from django.db.models import Sum
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from recipe.models import IngredientInRecipe


def generate_shopping_cart_pdf(user):
    ingredients = (
        IngredientInRecipe.objects.filter(recipe__shopping_cart__user=user)
        .values_list('ingredient__name', 'ingredient__measurement_unit')
        .order_by('ingredient__name')
        .annotate(ingredient_sum=Sum('amount'))
    )

    buffer = BytesIO()

    font_path = (
        Path(__file__).resolve().parent / 'front' / 'arialmt.ttf'
    ).resolve()

    pdfmetrics.registerFont(TTFont('arialmt', font_path))

    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont('arialmt', 12)

    title = 'Корзина покупок'
    title_font = 'arialmt'
    title_size = 24
    p.setFont(title_font, title_size)
    title_width = p.stringWidth(title, title_font, title_size)
    title_x = (letter[0] - title_width) / 2
    title_y = 750
    p.drawString(title_x, title_y, title)

    y = 700
    for ingredient in ingredients:
        name, measurement_unit, amount = (
            ingredient[0],
            ingredient[1],
            ingredient[2],
        )
        y -= 20
        p.drawString(100, y, f'{name} - {amount} {measurement_unit}')

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'
    ] = 'attachment; filename="shopping_cart.pdf"'
    response.write(buffer.read())

    return response
