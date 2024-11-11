from django import template
import re

register = template.Library()

# @register.filter
# def custom_paragraphs(value):
#     # Replace multiple newlines with HTML paragraphs
#     paragraphs = re.split(r'\n{2,}', value.strip())
#     return ''.join(f'<p>{p.replace("\n", "<br>")}</p>' for p in paragraphs)
