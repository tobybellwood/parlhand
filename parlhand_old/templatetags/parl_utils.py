import datetime

from django import template
from django.core.urlresolvers import reverse, resolve
from django.utils import dateformat

register = template.Library()

@register.filter
def end_or_today(date):
    if date:
        return date
    else:
        return datetime.date.today()

@register.simple_tag
def date_range(start,end,sep=" to ",empty_end="Present",frmt="d/m/Y"):
    # start dates shouldn't be empty
    if start is None:
        start = "Start date unknown"
    else:
        start = dateformat.format(start,frmt)
    if end is None:
        end = empty_end
    else:
        end = dateformat.format(end,frmt)
    
    return "%s %s %s"%(start,sep,end)
    
@register.filter
def days_to_years(los):
    years = los / 365
    months = (los % 365) / 30
    days = (los % 365) % 30
    out = []
    if years:
        out.append("%s years"%years)
    if months:
        out.append("%s months"%months)
    if days:
        out.append("%s days"%days)
    return ", ".join(out)

@register.simple_tag
def adminEdit(model,pk):
    """
    A tag for easily generating the link to an admin page for editing an item. For example::

        <a href="{% adminEdit item %}"Edit for {{item.name}}</a>
    """
    app,model = model
    return reverse("admin:%s_%s_change"%(app.lower(),model.lower()),args=[pk])

@register.simple_tag
def fuz_date(approx_date,date_format="Y-m-d",mode="e"):
    """
    A tag for transforming approximate dates into actual dates
    """
    return dateformat.format(approx_date.date(mode),date_format)
