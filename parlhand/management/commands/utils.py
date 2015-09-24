import datetime

def str_to_date(date_string):
    ds_format = None
    d = None
    date_string = unicode(date_string).encode('ascii','ignore')
    if len(date_string.split('/')) == 3:
        ds_format = "%d/%m/%Y"
    elif len(date_string.split('-')) == 3:
        ds_format = "%Y-%m-%d"
    elif len(date_string.split('.')) == 3:
        ds_format = "%d.%m.%y"
    elif len(date_string.split(' ')) == 2: #From wikipedia for PMs
        ds_format = "%d %B%Y"

    try:
        if ds_format:
            d = datetime.datetime.strptime(date_string,ds_format)
        else:
            pass #print date_string
    except:
        pass #print date_string
    
    return d