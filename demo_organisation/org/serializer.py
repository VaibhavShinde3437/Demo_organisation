from rest_framework import serializers
from organizations.models import OrganizationOwner, OrganizationUser, OrganizationInvitation
from demo_organisation.org.models import CustomOrganization

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomOrganization
        fields = "__all__"
        
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        childs = CustomOrganization.objects.filter(parent=instance.id)
        rep.update({
            "child" : [
                self.to_representation(child)
                for child in childs
            ]
        })
        return rep
        
class OrganizationOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationOwner
        fields = "__all__"

class OrganizationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationUser
        fields = "__all__"
        
class InviteSerailizer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInvitation
        fields = "__all__"
        
        
