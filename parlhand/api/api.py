from parlhand.popolo import api as popolo
from parlhand import models
from rest_framework import serializers

class MultiSerializerMixin(object):
    serializers = {
        'detail': None,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action,self.serializers['detail'])

class ParliamentarianSerializer(popolo.PersonSerializer):
    api_url = serializers.HyperlinkedIdentityField(view_name='parliamentarians-detail', format='html')
    class Meta:
        model = models.Person

class ParliamentarianViewSet(popolo.PersonViewSet):
    queryset = models.Person.objects.all()
    serializer_class = ParliamentarianSerializer

class ParliamentarianNameComponentViewSet(popolo.PersonNameComponentViewSet):
    queryset = models.Person.objects.all()

class PartyMembershipSerializer(popolo.MembershipSerializer):
    person = serializers.HyperlinkedRelatedField(lookup_field='pk',view_name='parliamentarians-detail',read_only=True, format='html')
    organization = serializers.HyperlinkedRelatedField(lookup_field='pk',view_name='party-detail',read_only=True, format='html')
    class Meta:
        model = models.PartyMembership
        #fields = filter(lambda f: f not in ['on_behalf_of','post'], popolo.MembershipSerializer.Meta.fields)
        fields = [f for f in popolo.MembershipSerializer.Meta.fields if f not in ['on_behalf_of','post']]

class PartyListSerializer(popolo.OrganizationSerializer):
    api_url = serializers.HyperlinkedIdentityField(view_name='party-detail', format='html')
    class Meta:
        model = models.Party
class PartyDetailSerializer(PartyListSerializer):
    members = PartyMembershipSerializer(many=True, read_only=True, source='partymembership_set')

class PartyViewSet(MultiSerializerMixin,popolo.PersonViewSet):
    queryset = models.Party.objects.all()
    #serializer_class = PartySerializer
    serializers = {
        'list':    PartyListSerializer,
        'detail':  PartyDetailSerializer,
    }
