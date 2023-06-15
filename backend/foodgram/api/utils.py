import io

from django.conf import settings
from django.http import FileResponse
from reportlab import rl_config
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from api.serializers import RecipeSerializer
from recipes.models import Recipe


PDF_FORNT = settings.PDF_FONTS_FILE
PDF_FONTS_FONTSIZE = settings.PDF_FONTS_FONTSIZE
PDF_FORNT_NAME = PDF_FORNT.split('.')[0]


def get_ingredients_for_pfd(request):
    recipes = Recipe.objects.filter(shoppingcarts_recipe__user=request.user)
    context = {'request': request}
    serialiser = RecipeSerializer(instance=recipes, many=True, context=context)

    ingredient_list = {}
    for recipe in serialiser.data:
        for ingredient in recipe['ingredients']:
            name = ingredient['name']
            amount = ingredient['amount']
            measurement_unit = ingredient['measurement_unit']
            if name in ingredient_list:
                ingredient_list[name][0] += amount
            else:
                ingredient_list[name] = [amount, measurement_unit]
    shopping_list = []
    for key, value in ingredient_list.items():
        shopping_list.append(f'{key} ({value[1]}) - {value[0]}')
    # text = '\n'.join(shopping_list)
    return shopping_list


def generatePDF(request):
    rl_config.TTFSearchPath.append(str(settings.PDF_FONTS_DIR))
    shopping_list = get_ingredients_for_pfd(request)
    buffer = io.BytesIO()
    page = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(TTFont(PDF_FORNT_NAME, PDF_FORNT))
    page.setFont(PDF_FORNT_NAME, PDF_FONTS_FONTSIZE)
    y_coordinate = 800
    page.drawString(200, y_coordinate, "Список покупок:")
    for item in shopping_list:
        y_coordinate -= 20
        page.drawString(100, y_coordinate, item)
    page.showPage()
    page.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='shopping_cart.pdf')
