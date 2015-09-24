import datetime

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.utils import dateformat

from parlhand.fields import ApproximateDate

register = template.Library()

@register.simple_tag
def approx_date_diff(start,end,mode="e",as_years=False):
    """
    A tag for transforming approximate dates into actual dates
    """
    if not end:
        end = datetime.date.today()
    elif not hasattr(end,'date'):
        print end.split('-')
        end = ApproximateDate(*map(int,end.split('-'))).date(mode)
    if not start:
        start = datetime.date.today()
    elif not hasattr(start,'date'):
        print "s", start
        print start.split('-')
        start = ApproximateDate(*map(int,start.split('-'))).date(mode)
    days = (end - start).days
    if as_years:
        days_to_years(days)
    else:
        return days

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
    los = los.days
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

@register.simple_tag
def confidence_date(date):
    confidence = date.confidence
    date = date.date
    if confidence == "YYYY-MM-DD":
        return dateformat.format(date, settings.DATE_FORMAT)
    elif confidence == "YYYY":
        return date.year
    elif confidence == "YYYY-MM":
        return dateformat.format(date,'%m %Y')
    else:
        return date.year