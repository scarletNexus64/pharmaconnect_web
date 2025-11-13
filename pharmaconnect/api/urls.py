from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Créer le router pour les ViewSets
router = DefaultRouter()

# Enregistrer tous les ViewSets
router.register('organizations', views.OrganizationViewSet)
router.register('donors', views.DonorViewSet)
router.register('health-facilities', views.HealthFacilityViewSet)
router.register('health-facility-distributors', views.HealthFacilityDistributorViewSet)
router.register('projects', views.ProjectViewSet)
router.register('users', views.UserViewSet)
router.register('medication-categories', views.MedicationCategoryViewSet)
router.register('medications', views.MedicationViewSet)
router.register('standard-lists', views.StandardListViewSet)
router.register('stock-entries', views.StockEntryViewSet)
router.register('prescription-photos', views.PrescriptionPhotoViewSet)
router.register('dispensations', views.DispensationViewSet)
router.register('inventories', views.InventoryViewSet)
router.register('consumption-data', views.ConsumptionDataViewSet)
router.register('alerts', views.AlertViewSet)

urlpatterns = [
    # Authentification
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # Analyses avancées
    path('analytics/stock-summary/', views.stock_summary, name='stock_summary'),
    path('analytics/pharmacoepidemio/', views.pharmacoepidemio_analysis, name='pharmacoepidemio_analysis'),
    
    # Inclure toutes les routes du router
    path('', include(router.urls)),
]