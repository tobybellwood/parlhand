from collections import OrderedDict
from django.http import JsonResponse
from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.response import Response
from parlhand import models
from parlhand.fields import ApproximateDate

class EventList(viewsets.ViewSet):
    """
    Returns the a collection of the number of people with particular membership at
    particular dates broken down by the requested aggregators.

    To return this, every change in a membership is found - specifically all start and end dates
    of a membership, then these dates are used to aggregate counts. As such, dates will not be
    regularly spaced. Aggregation over time (such as numbers in a given month) must be done on the client side.

    Possible query options are:
    
    * ``aggregator`` (repeatable) The field to aggregate on. For example ``&aggregator=person__gender`` will return the number of people in a membership, broken down by gender, and ``&aggregator=person__gender&aggregator=chamber__title`` will break down by gender and chamber.
    * ``filter`` (repeatable) The field and value to filter on with the field and value separated by a pipe ``|``. For example ``&filter=person__gender|Female`` will return only counts of women who have the given membership.
    * ``since`` (default: ``None``) Date from which to count memberships in ISO form, may be incomplete. For example, to restrict data to memberships from November 5, 1955 use ``&since=1955-11-05``, to restrict to anything from 2000 onwards, use ``&since=2000``
    * ``min`` (default: ``None``) The minimum number of members in an aggregator to be considered returned. For example, ``&aggregator=person__partymembership__party&min=25`` will return members, broken down by a persons party membership, and will only return those parties with at least 25 members.
    * ``smooth``  (default: ``False``) If this is set to true, events are only sampled at start dates. This reduces the number of results and may speed up the query.
    * ``totals``  (default: ``False``) Given an extra set of data ``totals`` that is the total number at a given date, inclusive of those excluded by ``min``
    * ``check_dates``  (default: ``False``) (warning - advanced use only) If this is set to true and if a secondary membership type is being used as an aggregator, this forces an additional set of filters to check that a person was a member of the secondary membership at the point in time being checked.
    
    **Additional info on ``check_dates``**
    
    Example: Consider a person 'Jack Politician' being a member of the 'Foo Party' from 1990-2000 and the 'Bar Party' from 2000-2010,
    and is also a Senator from "New South Wales"
    
    When aggregating on senators service on party, with ``check_dates`` set to False, Senator Politician would be
    double counted, as he was a member of two parties. When ``check_dates`` is set to True, when a date is queried
    it also check each of his party memberships to see if they were valid at that date as well.EventList
    
    In short, ``check_dates`` set to True will be more accurate, but may be slower overall.
    

    """
    def list(self, request, format=None):
        if len(request.GET.keys()) == 0:
            return Response({})
        return Response(events_api(request))

def events_api(request):
    aggregators = request.GET.getlist('aggregator',['chamber__title'])
    filters = request.GET.getlist('filter',[])
    since = request.GET.get('since',None)
    min_agg = request.GET.get('min',None)
    smooth = request.GET.get('smooth',False) is not False #samples only at start of service
    check_dates = request.GET.get('check_dates',False) is not False #and smooth # only do extra date checking if smooth otherwise this will thrash the DB
    show_totals = request.GET.get('totals',False) is not False
    fils = {}
    for f in filters:
        fil,val = f.split('|')
        fils[fil]=val
    event_type = models.Service.objects
    if since:
        since = ApproximateDate(*map(int,since.split('-'))).early()
    #events = event_type.filter(Q(end_date__gt=since)|Q(end_date='')).filter(**fils) # Pre-filter the events to look at
    events = event_type.filter(**fils) # Pre-filter the events to look at
    
    from datetime import timedelta, date

    available_keys = []
    candidate_keys = events.values(*aggregators).order_by().distinct()
    if min_agg:
        candidate_keys = candidate_keys.annotate(count=Count('person'))

    totals = {}
    ds = key_dates = {}
    for k in candidate_keys:
        if min_agg:
            l = [k[agg] for agg in aggregators if k[agg] is not None and k['count'] > int(min_agg)]
        else:
            l = [k[agg] for agg in aggregators if k[agg] is not None]
        if l:
            k = '-'.join(l)
            ds[k]={'keys':l,'data':{}} # set up whole date structure here
            available_keys.append(k)

    def get_date_data_for_query(query,query_date):
        # We call this in two places and only within this function, and it needs to modify a ton of local stuff
        # So a local function with 2 arguments is a better pattern than a module function with the 7 or so arguments.
        
        membership_aggs = [a for a in aggregators if "membership" in a]
        if check_dates and membership_aggs:
            for a in membership_aggs:
                f=a.split("membership",1)[0]+'membership' # Get just the membership part
                query &= Q(**{f+'__start_date__lte':query_date}) 
                query &= (Q(**{f+'__end_date__gte':query_date}) | Q(**{f+'__end_date__isnull':True}))

        val = events.filter(query).values(*aggregators).order_by().distinct().annotate(*[Count(a) for a in aggregators])
        #print val
        for k in ds.keys():
            ds[k]['data'][str(query_date)] = 0
        for v in val:
            agg_var = "-".join([str(v[x]) for x in aggregators])
            if agg_var in ds.keys():
                ds[agg_var]['data'][str(query_date)] = int(v[aggregators[0]+'__count'])

        if show_totals:
            total = events.filter(query).count()
            totals[str(query_date)] = total

    for e in events.order_by("start_date"):
        dates = [e.start_date,e.end_date]
        if smooth:
            dates = [e.start_date]
        for event_date in dates:
            if event_date:
                day_after = event_date + timedelta(days=1)
                days = [day_after]
                if not smooth:
                    day_before = event_date - timedelta(days=1)
                    days = [day_before,day_after]
                for query_date in days:
                    if not since or query_date > since:
                        query = Q(start_date__lte=query_date) & (Q(end_date__gt= query_date) | Q(end_date__isnull=True))
                        #get_date_data_for_query(key_dates,events,query,query_date,aggregators,available_keys)
                        get_date_data_for_query(query,query_date)

    today = date.today()
    if today not in key_dates.keys():
        query = Q(end_date__isnull=True)
        #get_date_data_for_query(key_dates,events,query,today,aggregators,available_keys)
        get_date_data_for_query(query,today)
    
    # sort the dates properly
    keys = []
    for agg,struct in key_dates.items():
        d = struct['data']
        struct['data'] = OrderedDict(sorted(d.items(), key=lambda t: t[0]))
    
    output = {'metadata':[],'data':key_dates}
    if show_totals:
        output['totals'] = totals
    return output
    