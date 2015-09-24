from parlhand.popolo import models
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import pagination, serializers, viewsets

class OtherNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OtherName
        fields = ('contact_type','label','note','value')

class HasOtherNameMixin(serializers.Serializer):
    pass #contact_details = serializers.SerializerMethodField()
    #def get_contact_details(self,instance):
    #    return [ContactDetailSerializer(cd).data for cd in instance.contact_details.all()]

class PopoloPagination(pagination.PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100

class PersonSerializer(serializers.ModelSerializer,HasOtherNameMixin):
    api_url = serializers.HyperlinkedIdentityField(view_name='persons-detail', format='html')
    class Meta:
        model = models.Person
        exclude = ["created","updated"]

class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    #queryset = models.Person.objects.all()
    pagination_class = PopoloPagination
    serializer_class = PersonSerializer

class PersonNameComponentSerializer(serializers.ModelSerializer,HasOtherNameMixin):
    full = serializers.HyperlinkedIdentityField(view_name='personnames-detail', format='html')
    class Meta:
        model = models.Person
        fields = ["name", "family_name", "given_name", "additional_name", "honorific_prefix", "honorific_suffix"]

class PersonNameComponentViewSet(viewsets.ReadOnlyModelViewSet):
    #queryset = models.Person.objects.all()
    pagination_class = PopoloPagination
    serializer_class = PersonNameComponentSerializer

class OrganizationSerializer(serializers.ModelSerializer,HasOtherNameMixin):
    class Meta:
        #model = models.Organization
        exclude = ["created","updated"]
    api_url = serializers.HyperlinkedIdentityField(view_name='organization-detail', format='html')
    classification = serializers.SerializerMethodField()
    def get_classification(self,instance):
        return instance.organization_type
        
class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    #queryset = models.Organization.objects.all()
    pagination_class = PopoloPagination
    serializer_class = OrganizationSerializer

class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Membership
        fields = ('label','role','person', 'start_date', 'end_date','post','organization','on_behalf_of')
        exclude = ['id']
    person = serializers.HyperlinkedRelatedField(lookup_field='pk',view_name='persons-detail',read_only=True, format='html')
    organization = serializers.HyperlinkedRelatedField(lookup_field='pk',view_name='organisations-detail',read_only=True, format='html')

def generate_membership_serializer(model):
    class subclass(serializers.ModelSerializer):
        class Meta:
            model = models.Membership

    return subclass