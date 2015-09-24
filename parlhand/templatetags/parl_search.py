from django import template
from django.core.urlresolvers import reverse, resolve
from django.utils import dateformat

register = template.Library()

@register.filter
def find_fragment(search_result,terms):
    #terms = getattr(form,'suggested_query',False) or getattr(form,'cleaned_data',{}).get('q','')
    text = search_result.text
    stubs = []
    clean_terms = [t for t in terms.split(' ') if t.strip() != '']
    if len(clean_terms) == 1:
        clean_terms = [t for t in terms.split('+') if t.strip() != '']
    for term in clean_terms:
        for line in text.split('\n'):
            if term.lower() in line.lower():
                if line not in stubs:
                    stubs.append(line)
                    break
    return " ... ".join(stubs)