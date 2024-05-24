from django.urls import path, include
from .views import OrganisationViewSet , OrganizationOwnerViewset, OrganizationUserViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router2 = DefaultRouter()


router.register("owner", OrganizationOwnerViewset, basename="user")
router.register("user", OrganizationUserViewset, basename="user")
router.register("", OrganisationViewSet, basename="org")

app_name = "Org"
urlpatterns = router.urls