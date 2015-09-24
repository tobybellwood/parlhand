# Based on (but a rewrite of) django_date_extensions
import datetime
import re

from django.conf import settings
from django.contrib.admin.widgets import AdminDateWidget
from django.db import models
from django.forms import widgets,fields,ValidationError
from django.utils import dateformat
from django.utils.six import with_metaclass

OUTPUT_FORMAT_DAY_MONTH_YEAR = getattr(settings, 'DATE_EXTENSIONS_OUTPUT_FORMAT_DAY_MONTH_YEAR', "jS F Y")
OUTPUT_FORMAT_MONTH_YEAR = getattr(settings, 'DATE_EXTENSIONS_OUTPUT_FORMAT_MONTH_YEAR', "F Y")
OUTPUT_FORMAT_YEAR = getattr(settings, 'DATE_EXTENSIONS_OUTPUT_FORMAT_YEAR', "Y")
ansi_date_re = re.compile(r'^\d{4}(-\d{1,2}(-\d{1,2})?)?$')

from django.utils.translation import ugettext_lazy as _

#class ConfidenceDate(datetime.date):
#    def __init__(self, confidence='YYYY-MM-DD',*args,**kwargs):
#        self.confidence=confidence
#        super(ConfidenceDate, self).__init__(*args, **kwargs)

from parlhand.multi_field import MultiColumnField

class ConfidenceDate(MultiColumnField):
    #fields = {
    #    'date': models.DateField(_("date"), null=True, blank=True),
    #    'confidence': models.CharField(max_length=200, null=True),
    #}
    def __init__(self, *args, **kwargs):
        args
        help_text = kwargs.get('help_text','An uncertain date')
        kwargs['fields'] = {
            'date': models.DateField(null=True, blank=True, help_text=help_text),
            'confidence': models.CharField(max_length=200, null=True, default="YYYY-MM-DD",help_text="The confidence of "+help_text.lower()+". Use 'YYYY','YYYY-MM' or 'YYYY-MM-DD'" ),
        }
        super(ConfidenceDate, self).__init__(*args, **kwargs)


    def __set__(self, instance, value):
        value = str(value)
        confidence = 'YYYY-MM-DD'[0:len(value)]
        
        value = (value+'-01-01')[0:10]
        value = {'date':value,'confidence':confidence}
        super(ConfidenceDate,self).__set__(instance, value)

    def __str__(self):
        return "sup"

class ApproximateDate(object):
    """A date object that accepts 0 for month or day to mean we don't
       know when it is within that month/year."""
    def __init__(self, year=0, month=0, day=0):
        if year and month and day:
            datetime.date(year, month, day)
        elif year and month:
            datetime.date(year, month, 1)
        elif year and day:
            raise ValueError("You cannot specify just a year and a day")
        elif year:
            datetime.date(year, 1, 1)
        else:
            raise ValueError("You must specify a year")

        self.year = year
        self.month = month
        self.day = day

    def __repr__(self):
        return "{year:04d}-{month:02d}-{day:02d}".format(year=self.year, month=self.month, day=self.day)

    def __str__(self):
        if not self.month:
            return "{year:04d}".format(year=self.year)
        if not self.day:
            return "{year:04d}-{month:02d}".format(year=self.year, month=self.month)
        return "{year:04d}-{month:02d}-{day:02d}".format(year=self.year, month=self.month, day=self.day)

        if self.year and self.month and self.day:
            return dateformat.format(self, OUTPUT_FORMAT_DAY_MONTH_YEAR)
        elif self.year and self.month:
            return dateformat.format(self, OUTPUT_FORMAT_MONTH_YEAR)
        elif self.year:
            return dateformat.format(self, OUTPUT_FORMAT_YEAR)

    def __eq__(self, other):
        if isinstance(other, (ApproximateDate, datetime.date, datetime.datetime)):
            return (self.year, self.month, self.day) ==\
                   (other.year, other.month, other.day)
        else:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        if other is None:
            return False
        if isinstance(other, (ApproximateDate, datetime.date, datetime.datetime)):
            return (self.year, self.month, self.day) <\
                   (other.year, other.month, other.day)
        else:
            return False

    def __len__(self):
        return len(self.__repr__())

    def early(self):
        return self.date(mode="early")
    def mid(self):
        return self.date(mode="mid")
    def late(self):
        return self.date(mode="late")

    def date(self,mode="early"):
        mode = mode.lower()
        year,month,day = self.year,self.month,self.day
        if mode in ["early",'e']:
            if not month:
                month = 1
            if not day:
                day = 1
        elif mode in ["mid",'m']:
            if not month:
                month = 7
                day = 1
            if not day:
                day = 1
        elif mode in ["late",'l']:
            if not month:
                month = 12
            if not day:
                day = 28
        return datetime.date(year,month,day)

class ApproximateDateFormField(fields.Field):
    widget = AdminDateWidget()
    def __init__(self, max_length=10, *args, **kwargs):
        super(ApproximateDateFormField, self).__init__(*args, **kwargs)
    def clean(self, value):
        super(ApproximateDateFormField, self).clean(value)
        if not value.strip():
            return None
        try:
            vals = value.split('-')
            year,month,day = int(vals[0]),0,0
            if len(vals) > 1:
                month = int(vals[1])
            if len(vals) > 2:
                day = int(vals[2])
            return ApproximateDate(year,month,day)
        except:
            raise ValidationError('Please enter a valid date.')

class ApproximateDateField(with_metaclass(models.SubfieldBase, models.CharField)):
    """A model field to store ApproximateDate objects in the database
       (as a CharField because MySQLdb intercepts dates from the
       database and forces them to be datetime.date()s."""
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        super(ApproximateDateField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value in (None, ''):
            return None
        if isinstance(value, ApproximateDate):
            return value
        if isinstance(value, datetime.date):
            return ApproximateDate(value.year, value.month, value.day)

        if not ansi_date_re.search(value):
            raise ValidationError('Enter a valid date in YYYY-MM-DD format.')
        
        cand = value.split('-')+[0,0]
        year, month, day = map(int, cand[:3])
        try:
            return ApproximateDate(year, month, day)
        except ValueError as e:
            msg = 'Invalid date: %s' % str(e)
            raise ValidationError(msg)

    def get_prep_value(self, value):
        if value in (None, ''):
            return ''
        if isinstance(value, ApproximateDate):
            return repr(value)
        if isinstance(value, datetime.date):
            return dateformat.format(value, "Y-m-d")
        if not ansi_date_re.search(value):
            raise ValidationError('Enter a valid date in YYYY-MM-DD format. - [%s]'%value)
        return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {'form_class': ApproximateDateFormField}
        defaults.update(kwargs)
        return super(ApproximateDateField, self).formfield(**defaults)
