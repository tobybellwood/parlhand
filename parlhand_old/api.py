from parlhand import models
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import pagination, serializers, viewsets

from parlhand.templatetags.parl_utils import days_to_years

class PersonPagination(pagination.PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100

class ParliamentarianSerializer(serializers.ModelSerializer):
    api_url = serializers.HyperlinkedIdentityField(view_name='parliamentarians-detail', format='html')
    parties = serializers.SerializerMethodField()
    electorates = serializers.SerializerMethodField()
    length_of_service = serializers.SerializerMethodField()

    class Meta:
        model = models.Person

    def get_length_of_service(self,instance):
        los = instance.length_of_service
        return {
            "days":los,
            "human_readable":days_to_years(los),
            "current":instance.current_seat is not None,
            "continuous":True
            }
    
    def get_parties(self,instance):
        return [
            {   "party" : {
                    "name": m.party.name,
                    "code": m.party.code
                    },
                "start":
                    {   "date": m.start_date,
                    },
                "end":
                    {   "date": m.end_date,
                    }
            } for m in instance.partymembership_set.all() ]

    def get_electorates(self,instance):
        return [
            {   "seat" : {
                    "type": e.seat_type,
                    "electorate": { "name": e.electorate.name,
                                    "code": e.electorate.id
                                }
                    },
                "start":
                    {   "date": e.start_date,
                        "reason": e.start_reason
                    },
                "end":
                    {   "date": e.end_date,
                        "reason": e.end_reason
                    }
            } for e in instance.service_set.all() ]

class ParliamentarianViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Person.objects.all()
    pagination_class = PersonPagination
    serializer_class = ParliamentarianSerializer

class CurrentViewSet(viewsets.ReadOnlyModelViewSet):
    pass

class CurrentSerializer(serializers.ModelSerializer):
    api_url = serializers.HyperlinkedIdentityField(view_name='senators-detail', format='html')
    party = serializers.SerializerMethodField()
    electorate = serializers.SerializerMethodField()

    class Meta:
        model = models.Person
    
    def get_party(self,instance):
        out = {"code":instance.current_party().code,'name':instance.current_party().name}
        return out
    def get_electorate(self,instance):
        return instance.current_seat().electorate.name
        
class SenatorViewSet(CurrentViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = models.senators()
    serializer_class = CurrentSerializer


class MemberViewSet(CurrentViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = models.senators()
    serializer_class = CurrentSerializer


class ElectorateSerializer(serializers.ModelSerializer):
    api_url = serializers.HyperlinkedIdentityField(view_name='electorates-detail', format='html')
    representatives = serializers.SerializerMethodField()
    class Meta:
        model = models.Electorate

    def get_representatives(self,instance):
        return [
            {   e.seat_type.lower() : {
                    "name": e.person.full_name,
                    "code": e.person.phid
                    },
                "start":
                    {   "date": e.start_date,
                        "reason": e.start_reason
                    },
                "end":
                    {   "date": e.end_date,
                        "reason": e.end_reason
                    }
            } for e in instance.service_set.all() ]

class ElectorateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Electorate.objects.all()
    serializer_class = ElectorateSerializer
