from organizations.models import OrganizationOwner, OrganizationUser
from rest_framework.response import Response

from demo_organisation.org.models import CustomOrganization


def change_owner(parent_id, org):
    parent_owner = OrganizationOwner.objects.filter(organization_id=parent_id).first()
    if parent_owner:
        parent_user = parent_owner.organization_user.user
    else:
        return Response({"details": "Organization does not exist"})

    org_user = OrganizationUser.objects.filter(
        user=parent_user, organization=org
).first()
    if not org_user:
        org_user = OrganizationUser(user=parent_user, organization=org)
        org_user.save()

    OrganizationOwner.objects.filter(organization=org).delete()
    org_owner = OrganizationOwner(organization_user=org_user, organization=org)
    org_owner.save()

    child_org = CustomOrganization.objects.filter(parent=org)
    for each_org in child_org:
        change_owner(parent_id, each_org)
