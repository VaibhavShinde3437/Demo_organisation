import jwt
from demo_organisation.org.models import CustomOrganization
from organizations.models import (
    OrganizationOwner,
    OrganizationUser,
    OrganizationInvitation,
)
from drf_spectacular.utils import OpenApiParameter, extend_schema
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from .serializer import (
    OrganizationOwnerSerializer,
    OrganizationUserSerializer,
    OrganizationSerializer,
    InviteSerailizer,
)
from rest_framework.viewsets import ModelViewSet
from urllib.parse import urlencode, urljoin
from django.core.mail import send_mail
from demo_organisation import settings
from django.db import transaction
from django.utils.html import strip_tags
from rest_framework.permissions import AllowAny
from demo_organisation.org.permission import OrgCreation, IsOwner, IsOwnerOrAdmin


class OrganisationViewSet(ModelViewSet):
    queryset = CustomOrganization.objects.all()
    serializer_class = OrganizationSerializer
    # permission_classes = [OrgCreation,]
    def get_serializer_class(self):
        if self.action == "invite":
            return InviteSerailizer
        return super().get_serializer_class()
    
    def get_permissions(self):
        if self.action == "accept":
            return [AllowAny(),]
        if self.action in ["destory",]:
            return [IsOwner,]
        # if self.action in ["partial_update"]:
        #     return [IsOwnerOrAdmin,]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org = serializer.save()

        parent_id = serializer.validated_data.get("parent")
        if parent_id is not None:
            parent_owner = OrganizationOwner.objects.filter(organization_id=parent_id).first()
            if parent_owner:
                parent_user = parent_owner.organization_user.user
            else:
                return Response({"details" : "Organization does not exist"})

        org_user = OrganizationUser.objects.filter(user=parent_user, organization=org).first()
        if not org_user:
            org_user = OrganizationUser(user=parent_user, organization=org)
            org_user.save()

        org_owner = OrganizationOwner(organization_user=org_user, organization=org)
        org_owner.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
    def partial_update(self, request, *args, **kwargs):
        org = self.get_object()
        with transaction.atomic():
            serializer = self.serializer_class(data=request.data, instance=org, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            parent_id = serializer.validated_data.get("parent")
            
            if parent_id is not None:
                parent_owner = OrganizationOwner.objects.filter(organization_id=parent_id).first()
                if parent_owner:
                    parent_user = parent_owner.organization_user.user
                else:
                    return Response({"details" : "Organization does not exist"})

                org_user = OrganizationUser.objects.filter(user=parent_user, organization=org).first()
                if not org_user:
                    org_user = OrganizationUser(user=parent_user, organization=org)
                    org_user.save()

                OrganizationOwner.objects.filter(organization=org).delete()
                org_owner = OrganizationOwner(organization_user=org_user, organization=org)
                org_owner.save()
                

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def invite(self, request, pk=None):
        with transaction.atomic():

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            invite_obj = serializer.save()

            token = jwt.encode(
                {
                    "invite": invite_obj.id,
                },
                key=settings.SECRET_KEY,
                algorithm="HS256",
            )
            url = urlencode({"key": token})
            api_name = request.headers.get("Origin") + "/api/org/accept"
            encoded_url = urljoin(api_name, f"?{url}")

            context = {
                "invitee": invite_obj.invitee.username,
                "url": encoded_url,
                "org_name": invite_obj.organization.name,
            }
            body = render_to_string("emails/invitation_email.html", context)
            send_mail(
                f"Invitation from {invite_obj.organization.name}",
                strip_tags(body),
                settings.EMAIL_HOST,
                [invite_obj.invitee.email],
                fail_silently=False,
            )

        return Response("Invited successfully")

    @extend_schema(
        parameters=[
            OpenApiParameter(name="key", type=str, location="query", required=True),
        ],
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[
            AllowAny,
        ],
    )
    def accept(self, request):
        with transaction.atomic():
            key = request.query_params.get("key")
            try:
                decoded_key = jwt.decode(key, settings.SECRET_KEY, algorithms=["HS256"])
            except Exception as e:
                raise Response({"details" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
            invite_obj = OrganizationInvitation.objects.filter(
                id=decoded_key["invite"]
            ).first()

            if (
                invite_obj is None
                and OrganizationUser.objects.filter(
                    user=invite_obj.invitee.id,
                    organization_id=invite_obj.organization.id,
                ).exists()
            ):
                return Response({"details": "Invalid invitation url"})
            OrganizationUser.objects.create(
                user=invite_obj.invitee, organization=invite_obj.organization
            )
        return Response(
            {"details": "Invitation accepted successfully!!"}
        )
        
class OrganizationUserViewset(ModelViewSet):
    queryset = OrganizationUser.objects.all()
    serializer_class = OrganizationUserSerializer
    
    def get_permissions(self):
        if self.action in ["destory"]:
            return [IsOwner,]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        if OrganizationUser.objects.filter(user=request.data.get("user"), organization_id=request.data.get("organization")).exists():
            return Response({"details" : "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return super().create(request, *args, **kwargs)
    
    

class OrganizationOwnerViewset(ModelViewSet):
    queryset = OrganizationOwner.objects.all()
    serializer_class = OrganizationOwnerSerializer
