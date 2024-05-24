from rest_framework.permissions import BasePermission
from organizations.models import OrganizationUser, OrganizationOwner
from demo_organisation.org.models import CustomOrganization


class OrgCreation(BasePermission):
    def has_permission(self, request, view=None):
        if not request.user.is_authenticated:
            return False
        if request.data.get("parent") is not None:
            org = CustomOrganization.objects.filter(id=request.data.get("parent")).first()
            if org:
                org_user = OrganizationUser.objects.filter(user_id=request.user.id, organization=org).first()
                if org_user and (OrganizationOwner.objects.filter(organization_user=org_user).exists() or org_user.is_admin):
                    return True
            return False
        return True
    
class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view=None):
        if not request.user.is_authenticated:
            return False
        org = CustomOrganization.objects.filter(id=request.data.get("organization")).first()
        if org:
            org_user = OrganizationUser.objects.filter(user_id=request.user.id, organization=org).first()
            if org_user and (OrganizationOwner.objects.filter(organization_user=org_user).exists() or org_user.is_admin):
                return True
        return False
    
class IsOwner(BasePermission):
    def has_permission(self, request, view=None):
        if not request.user.is_authenticated:
            return False
        org_user = OrganizationUser.objects.filter(user=request.user, organization_id=request.data.get("organization"))
        if org_user and OrganizationOwner.objects.filter(organization_user=org_user, organization=request.data.get("organization")).exists():
            return True
        return False
    
class OrgUser(BasePermission):
    def has_permission(self, request, view=None):
        if request.user.is_authenticated:
            return False
        if not OrganizationUser.objects.filter(user=request.user, organization_id=request.data.get("organization")).exists():
            return False
        return True
    