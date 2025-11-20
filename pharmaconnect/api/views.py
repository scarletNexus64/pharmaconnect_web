from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import login
from django.db.models import Q, Sum, Count, Avg, F
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    User, Organization, Donor, HealthFacility, HealthFacilityDistributor, Project, MedicationCategory,
    Medication, StandardList, MedicationSubstitution, StockEntry,
    PrescriptionPhoto, Dispensation, DispensationItem, Inventory,
    InventoryItem, ConsumptionData, StockoutPeriod, Alert
)
from .serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer, OrganizationSerializer,
    DonorSerializer, HealthFacilitySerializer, HealthFacilityDistributorSerializer, ProjectSerializer,
    MedicationCategorySerializer, MedicationSerializer, MedicationSearchSerializer,
    StandardListSerializer, MedicationSubstitutionSerializer, StockEntrySerializer,
    PrescriptionPhotoSerializer, DispensationSerializer, DispensationItemSerializer,
    InventorySerializer, InventoryItemSerializer, ConsumptionDataSerializer,
    StockoutPeriodSerializer, AlertSerializer, StockSummarySerializer,
    ConsumptionAnalysisSerializer, ReceptionReportSerializer,
    PharmacoepidemioAnalysisSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Inscription d'un nouvel utilisateur"""
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Connexion utilisateur"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Déconnexion utilisateur"""
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Déconnexion réussie'})
    except:
        return Response({'message': 'Erreur lors de la déconnexion'}, 
                       status=status.HTTP_400_BAD_REQUEST)


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les organisations"""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'country']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Filtrer selon l'utilisateur connecté"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # L'utilisateur ne voit que son organisation
        if user.organization:
            return queryset.filter(id=user.organization.id)
        
        # Si pas d'organisation assignée, retourner queryset vide
        return queryset.none()

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Obtenir les utilisateurs d'une organisation"""
        organization = self.get_object()
        users = User.objects.filter(organization=organization)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        """Obtenir les projets d'une organisation"""
        organization = self.get_object()
        projects = Project.objects.filter(organization=organization)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)


class DonorViewSet(viewsets.ModelViewSet):
    """ViewSet pour les bailleurs"""
    queryset = Donor.objects.all()
    serializer_class = DonorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class HealthFacilityViewSet(viewsets.ModelViewSet):
    """ViewSet pour les formations sanitaires"""
    queryset = HealthFacility.objects.all()
    serializer_class = HealthFacilitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'code', 'location', 'address']
    filterset_fields = ['type', 'level_of_care']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def distributors(self, request, pk=None):
        """Récupère les distributeurs d'une formation sanitaire"""
        health_facility = self.get_object()
        distributors = HealthFacilityDistributor.objects.filter(
            health_facility=health_facility,
            is_active=True
        ).select_related('user')
        
        serializer = HealthFacilityDistributorSerializer(distributors, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def with_coordinates(self, request):
        """Récupère toutes les formations sanitaires avec coordonnées pour la carte"""
        facilities = self.get_queryset().filter(
            latitude__isnull=False,
            longitude__isnull=False
        )
        serializer = self.get_serializer(facilities, many=True)
        return Response(serializer.data)


class HealthFacilityDistributorViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des distributeurs des formations sanitaires"""
    queryset = HealthFacilityDistributor.objects.select_related('user', 'health_facility', 'assigned_by').all()
    serializer_class = HealthFacilityDistributorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'health_facility__name']
    filterset_fields = ['is_active', 'health_facility', 'user']
    ordering_fields = ['assigned_date']
    ordering = ['-assigned_date']
    
    def get_queryset(self):
        """Filtrer selon l'utilisateur connecté pour ne voir que les distributeurs de son organisation"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # L'utilisateur ne voit que les distributeurs des formations de son organisation
        if user.organization:
            return queryset.filter(user__organization=user.organization)
        
        # Si pas d'organisation assignée, retourner queryset vide
        return queryset.none()
    
    def perform_create(self, serializer):
        """Enregistre qui a effectué l'assignation"""
        serializer.save(assigned_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_facility(self, request):
        """Récupère les distributeurs groupés par formation sanitaire"""
        facility_id = request.query_params.get('facility_id')
        if facility_id:
            distributors = self.get_queryset().filter(
                health_facility_id=facility_id,
                is_active=True
            )
            serializer = self.get_serializer(distributors, many=True)
            return Response(serializer.data)
        return Response([])
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Récupère les formations sanitaires assignées à un utilisateur"""
        user_id = request.query_params.get('user_id', request.user.id)
        distributors = self.get_queryset().filter(
            user_id=user_id,
            is_active=True
        )
        serializer = self.get_serializer(distributors, many=True)
        return Response(serializer.data)


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet pour les projets"""
    queryset = Project.objects.select_related('organization', 'donor', 'health_facility').all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'code']
    filterset_fields = ['organization', 'donor', 'health_facility']
    ordering_fields = ['name', 'start_date', 'created_at']
    ordering = ['-start_date']

    def get_queryset(self):
        """Filtrer selon l'utilisateur connecté"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.access_level == 'COORDINATION':
            # Coordination peut voir tous les projets de son organisation
            return queryset.filter(organization=user.organization)
        elif user.access_level == 'FACILITY':
            # Formation sanitaire ne voit que ses projets
            return queryset.filter(health_facility=user.health_facility)
        
        return queryset


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet pour les utilisateurs"""
    queryset = User.objects.select_related('organization', 'health_facility').all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filterset_fields = ['organization', 'health_facility', 'access_level', 'is_active']
    ordering_fields = ['username', 'date_joined']
    ordering = ['username']

    def get_queryset(self):
        """Filtrer selon l'utilisateur connecté pour ne voir que les utilisateurs de son organisation"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # L'utilisateur ne voit que les utilisateurs de son organisation
        if user.organization:
            return queryset.filter(organization=user.organization)
        
        # Si pas d'organisation assignée, retourner queryset vide
        return queryset.none()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtenir les informations de l'utilisateur connecté"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available_distributors(self, request):
        """Récupère les utilisateurs disponibles pour être assignés comme distributeurs à une formation sanitaire"""
        facility_id = request.query_params.get('facility_id')
        
        # Commencer avec les utilisateurs de l'organisation (get_queryset applique déjà ce filtre)
        users_queryset = self.get_queryset().filter(is_active=True)
        
        # Si facility_id est fourni, exclure les utilisateurs déjà assignés à cette formation
        if facility_id:
            users_queryset = users_queryset.exclude(
                health_facility_assignments__health_facility_id=facility_id,
                health_facility_assignments__is_active=True
            )
        
        serializer = self.get_serializer(users_queryset, many=True)
        return Response(serializer.data)


class MedicationCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour les catégories de médicaments"""
    queryset = MedicationCategory.objects.all()
    serializer_class = MedicationCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Filtrer selon l'utilisateur connecté"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # L'utilisateur ne voit que les catégories de son organisation
        if user.organization:
            return queryset.filter(organization=user.organization)
        
        # Si pas d'organisation assignée, retourner queryset vide
        return queryset.none()

    def perform_create(self, serializer):
        """Associer automatiquement l'organisation lors de la création"""
        serializer.save(organization=self.request.user.organization)


class MedicationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les médicaments"""
    queryset = Medication.objects.select_related('category', 'organization').prefetch_related('allowed_facilities').all()
    serializer_class = MedicationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['code', 'name', 'dosage', 'therapeutic_class']
    filterset_fields = ['category', 'is_active', 'therapeutic_class']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']

    def get_queryset(self):
        """Filtrer selon l'utilisateur connecté"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # L'utilisateur ne voit que les médicaments de son organisation
        if user.organization:
            return queryset.filter(organization=user.organization)
        
        # Si pas d'organisation assignée, retourner queryset vide
        return queryset.none()

    def perform_create(self, serializer):
        """Associer automatiquement l'organisation lors de la création"""
        serializer.save(organization=self.request.user.organization)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Recherche optimisée de médicaments"""
        query = request.query_params.get('q', '')
        category = request.query_params.get('category', '')
        facility_type = request.query_params.get('facility_type', '')
        
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(
                Q(code__icontains=query) |
                Q(name__icontains=query) |
                Q(dosage__icontains=query) |
                Q(therapeutic_class__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(category_id=category)
            
        if facility_type:
            queryset = queryset.filter(allowed_facilities__type=facility_type)
        
        queryset = queryset.distinct()[:20]  # Limiter à 20 résultats
        serializer = MedicationSearchSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def substitutions(self, request, pk=None):
        """Obtenir les substitutions possibles pour un médicament"""
        medication = self.get_object()
        user = request.user
        
        substitutions = MedicationSubstitution.objects.filter(
            original_medication=medication,
            organization=user.organization
        ).select_related('substitute_medication')
        
        serializer = MedicationSubstitutionSerializer(substitutions, many=True)
        return Response(serializer.data)


class StandardListViewSet(viewsets.ModelViewSet):
    """ViewSet pour les listes standard"""
    queryset = StandardList.objects.select_related(
        'organization', 'project', 'medication__category'
    ).all()
    serializer_class = StandardListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['medication__name', 'medication__code', 'custom_name', 'custom_code']
    filterset_fields = ['organization', 'project', 'is_included', 'medication__category']
    ordering_fields = ['medication__name', 'created_at']
    ordering = ['medication__name']

    def get_queryset(self):
        """Filtrer selon l'utilisateur connecté"""
        queryset = super().get_queryset()
        user = self.request.user
        return queryset.filter(organization=user.organization)

    @action(detail=False, methods=['post'])
    def generate_standard_list(self, request):
        """Générer automatiquement la liste standard"""
        organization_id = request.data.get('organization')
        project_id = request.data.get('project')
        level_of_care = request.data.get('level_of_care')
        
        try:
            organization = Organization.objects.get(id=organization_id)
            project = Project.objects.get(id=project_id)
            
            # Logique de génération automatique selon le niveau de soins
            medications = Medication.objects.filter(
                allowed_facilities__level_of_care=level_of_care,
                is_active=True
            ).distinct()
            
            created_items = []
            for medication in medications:
                item, created = StandardList.objects.get_or_create(
                    organization=organization,
                    project=project,
                    medication=medication,
                    defaults={'is_included': True}
                )
                if created:
                    created_items.append(item)
            
            serializer = self.get_serializer(created_items, many=True)
            return Response({
                'message': f'{len(created_items)} médicaments ajoutés à la liste standard',
                'items': serializer.data
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StockEntryViewSet(viewsets.ModelViewSet):
    """ViewSet pour les entrées en stock"""
    queryset = StockEntry.objects.select_related(
        'organization', 'project', 'medication'
    ).all()
    serializer_class = StockEntrySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['medication__name', 'medication__code', 'supplier', 'batch_number']
    filterset_fields = ['organization', 'project', 'medication', 'delivery_date']
    ordering_fields = ['delivery_date', 'expiry_date', 'created_at']
    ordering = ['-delivery_date']

    def get_queryset(self):
        """Filtrer selon l'utilisateur connecté"""
        queryset = super().get_queryset()
        user = self.request.user

        if user.access_level == 'COORDINATION':
            return queryset.filter(organization=user.organization)
        elif user.access_level == 'FACILITY':
            return queryset.filter(project__health_facility=user.health_facility)

        return queryset

    def perform_create(self, serializer):
        """Associer automatiquement l'organisation lors de la création"""
        # Si l'organisation n'est pas fournie, utiliser celle de l'utilisateur
        if not serializer.validated_data.get('organization'):
            serializer.save(organization=self.request.user.organization)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def reception_report(self, request):
        """Rapport de réception"""
        queryset = self.get_queryset()
        organization_id = request.query_params.get('organization')
        project_id = request.query_params.get('project')
        
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Calculer les statistiques
        total_orders = queryset.count()
        avg_reception = queryset.aggregate(
            avg_reception=Avg(
                F('quantity_delivered') * 100.0 / F('quantity_ordered')
            )
        )['avg_reception'] or 0
        
        items = queryset.annotate(
            reception_rate=F('quantity_delivered') * 100.0 / F('quantity_ordered')
        ).order_by('-delivery_date')[:50]
        
        return Response({
            'total_orders': total_orders,
            'average_reception_rate': round(avg_reception, 2),
            'items': StockEntrySerializer(items, many=True).data
        })

    @action(detail=False, methods=['get'])
    def expiry_alerts(self, request):
        """Alertes de péremption"""
        queryset = self.get_queryset()
        today = datetime.now().date()
        
        # Produits expirés
        expired = queryset.filter(expiry_date__lt=today)
        
        # Produits à risque (< 2 mois)
        risk_date = today + timedelta(days=60)
        at_risk = queryset.filter(
            expiry_date__gte=today,
            expiry_date__lt=risk_date
        )
        
        return Response({
            'expired_count': expired.count(),
            'at_risk_count': at_risk.count(),
            'expired_items': StockEntrySerializer(expired[:10], many=True).data,
            'at_risk_items': StockEntrySerializer(at_risk[:10], many=True).data
        })


class PrescriptionPhotoViewSet(viewsets.ModelViewSet):
    """ViewSet pour les photos d'ordonnances"""
    queryset = PrescriptionPhoto.objects.all()
    serializer_class = PrescriptionPhotoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['uploaded_at']
    ordering = ['-uploaded_at']

    def get_queryset(self):
        """Filtrer selon l'utilisateur connecté"""
        return super().get_queryset().filter(user=self.request.user)


class DispensationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les dispensations"""
    queryset = Dispensation.objects.select_related(
        'prescription_photo', 'organization', 'project', 'created_by'
    ).prefetch_related('items__medication').all()
    serializer_class = DispensationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['patient_name', 'prescription_number', 'prescriber_name']
    filterset_fields = ['destination', 'status', 'organization', 'project']
    ordering_fields = ['dispensation_date']
    ordering = ['-dispensation_date']

    def get_queryset(self):
        """Filtrer selon l'utilisateur connecté"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.access_level == 'COORDINATION':
            return queryset.filter(organization=user.organization)
        elif user.access_level == 'FACILITY':
            return queryset.filter(project__health_facility=user.health_facility)
        
        return queryset

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques de dispensation"""
        queryset = self.get_queryset()
        
        # Filtres par date
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(dispensation_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(dispensation_date__lte=end_date)
        
        total_dispensations = queryset.count()
        by_status = queryset.values('status').annotate(count=Count('id'))
        by_destination = queryset.values('destination').annotate(count=Count('id'))
        
        return Response({
            'total_dispensations': total_dispensations,
            'by_status': list(by_status),
            'by_destination': list(by_destination)
        })


class InventoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour les inventaires"""
    queryset = Inventory.objects.select_related(
        'organization', 'project', 'created_by'
    ).prefetch_related('items__medication').all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['organization', 'project', 'month', 'year']
    ordering_fields = ['inventory_date', 'created_at']
    ordering = ['-inventory_date']

    def get_queryset(self):
        """Filtrer selon l'utilisateur connecté"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.access_level == 'COORDINATION':
            return queryset.filter(organization=user.organization)
        elif user.access_level == 'FACILITY':
            return queryset.filter(project__health_facility=user.health_facility)
        
        return queryset

    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        """Analyse d'inventaire"""
        inventory = self.get_object()
        items = inventory.items.all()
        
        total_items = items.count()
        positive_variances = items.filter(
            theoretical_stock__gt=F('physical_stock')
        ).count()
        negative_variances = items.filter(
            theoretical_stock__lt=F('physical_stock')
        ).count()
        
        total_variance = sum(item.variance for item in items)
        
        return Response({
            'total_items': total_items,
            'positive_variances': positive_variances,
            'negative_variances': negative_variances,
            'positive_variance_percentage': (positive_variances / total_items * 100) if total_items > 0 else 0,
            'negative_variance_percentage': (negative_variances / total_items * 100) if total_items > 0 else 0,
            'total_variance': total_variance,
            'items_with_variance': InventoryItemSerializer(
                items.exclude(theoretical_stock=F('physical_stock')), 
                many=True
            ).data
        })


class ConsumptionDataViewSet(viewsets.ModelViewSet):
    """ViewSet pour les données de consommation"""
    queryset = ConsumptionData.objects.select_related(
        'organization', 'project', 'medication'
    ).all()
    serializer_class = ConsumptionDataSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['organization', 'project', 'medication', 'week_number', 'year', 'is_week_closed']
    ordering_fields = ['week_number', 'year', 'created_at']
    ordering = ['-year', '-week_number']

    def get_queryset(self):
        """Filtrer selon l'utilisateur connecté"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.access_level == 'COORDINATION':
            return queryset.filter(organization=user.organization)
        elif user.access_level == 'FACILITY':
            return queryset.filter(project__health_facility=user.health_facility)
        
        return queryset

    @action(detail=False, methods=['get'])
    def weekly_analysis(self, request):
        """Analyse hebdomadaire de consommation"""
        queryset = self.get_queryset()
        medication_id = request.query_params.get('medication')
        year = request.query_params.get('year', datetime.now().year)
        
        if medication_id:
            queryset = queryset.filter(medication_id=medication_id)
        
        queryset = queryset.filter(year=year, is_week_closed=True)
        
        weekly_data = queryset.values('week_number').annotate(
            total_consumption=Sum('quantity_consumed')
        ).order_by('week_number')
        
        return Response(list(weekly_data))

    @action(detail=False, methods=['get'])
    def monthly_analysis(self, request):
        """Analyse mensuelle de consommation (CMM)"""
        queryset = self.get_queryset()
        medication_id = request.query_params.get('medication')
        months = int(request.query_params.get('months', 3))
        
        if medication_id:
            queryset = queryset.filter(medication_id=medication_id)
        
        # Calculer la CMM sur X mois
        queryset = queryset.filter(is_week_closed=True)
        total_consumption = queryset.aggregate(
            total=Sum('quantity_consumed')
        )['total'] or 0
        
        weeks_count = queryset.count()
        monthly_average = (total_consumption / weeks_count * 4.33) if weeks_count > 0 else 0
        
        return Response({
            'total_consumption': total_consumption,
            'weeks_analyzed': weeks_count,
            'monthly_average': round(monthly_average, 2)
        })


class AlertViewSet(viewsets.ModelViewSet):
    """ViewSet pour les alertes"""
    queryset = Alert.objects.select_related(
        'organization', 'project', 'medication'
    ).all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['title', 'message']
    filterset_fields = ['alert_type', 'severity', 'is_active', 'organization', 'project']
    ordering_fields = ['created_at', 'severity']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filtrer selon l'utilisateur connecté"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.access_level == 'COORDINATION':
            return queryset.filter(organization=user.organization)
        elif user.access_level == 'FACILITY':
            return queryset.filter(project__health_facility=user.health_facility)
        
        return queryset

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Résoudre une alerte"""
        alert = self.get_object()
        alert.is_active = False
        alert.resolved_at = datetime.now()
        alert.save()
        
        return Response({'message': 'Alerte résolue avec succès'})

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard des alertes"""
        queryset = self.get_queryset().filter(is_active=True)
        
        by_severity = queryset.values('severity').annotate(count=Count('id'))
        by_type = queryset.values('alert_type').annotate(count=Count('id'))
        
        critical_alerts = queryset.filter(severity='CRITICAL')[:5]
        
        return Response({
            'total_active_alerts': queryset.count(),
            'by_severity': list(by_severity),
            'by_type': list(by_type),
            'critical_alerts': AlertSerializer(critical_alerts, many=True).data
        })

# Vues pour les analyses avancées
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_summary(request):
    """Résumé global des stocks"""
    user = request.user
    
    # Filtrer selon l'accès utilisateur
    if user.access_level == 'COORDINATION':
        stock_entries = StockEntry.objects.filter(organization=user.organization)
    elif user.access_level == 'FACILITY':
        stock_entries = StockEntry.objects.filter(project__health_facility=user.health_facility)
    else:
        stock_entries = StockEntry.objects.none()
    
    today = datetime.now().date()
    
    # Calculer les métriques
    total_medications = stock_entries.values('medication').distinct().count()
    total_value = stock_entries.aggregate(
        total=Sum(F('quantity_delivered') * F('unit_price'))
    )['total'] or 0
    
    expired_items = stock_entries.filter(expiry_date__lt=today).count()
    risk_date = today + timedelta(days=60)
    expiry_risk_items = stock_entries.filter(
        expiry_date__gte=today,
        expiry_date__lt=risk_date
    ).count()
    
    # Calculer ruptures et pré-ruptures (logique simplifiée)
    stockout_items = 0  # À implémenter selon la logique métier
    pre_stockout_items = 0  # À implémenter selon la logique métier
    
    data = {
        'total_medications': total_medications,
        'total_stock_value': total_value,
        'expired_items': expired_items,
        'expiry_risk_items': expiry_risk_items,
        'stockout_items': stockout_items,
        'pre_stockout_items': pre_stockout_items
    }
    
    serializer = StockSummarySerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pharmacoepidemio_analysis(request):
    """Analyses pharmacoépidémiologiques"""
    user = request.user
    
    # Filtrer selon l'accès utilisateur
    if user.access_level == 'COORDINATION':
        dispensations = Dispensation.objects.filter(organization=user.organization)
    elif user.access_level == 'FACILITY':
        dispensations = Dispensation.objects.filter(project__health_facility=user.health_facility)
    else:
        dispensations = Dispensation.objects.none()
    
    # Filtres par date
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if start_date:
        dispensations = dispensations.filter(dispensation_date__gte=start_date)
    if end_date:
        dispensations = dispensations.filter(dispensation_date__lte=end_date)
    
    total_prescriptions = dispensations.count()
    
    # Prescriptions d'antibiotiques (logique simplifiée)
    antibiotic_prescriptions = dispensations.filter(
        items__medication__therapeutic_class__icontains='antibiotique'
    ).distinct().count()
    
    # Prescriptions antipaludiques
    malaria_prescriptions = dispensations.filter(
        items__medication__therapeutic_class__icontains='antipaludique'
    ).distinct().count()
    
    # Prescriptions femmes enceintes
    pregnant_women_prescriptions = dispensations.filter(
        patient_service__icontains='CPN'
    ).count()
    
    # Prescriptions enfants < 5 ans
    children_under_5_prescriptions = dispensations.filter(
        patient_age__lt=5
    ).count()
    
    # Multithérapies antibiotiques (logique simplifiée)
    multitherapy_prescriptions = 0  # À implémenter selon la logique métier
    
    data = {
        'total_prescriptions': total_prescriptions,
        'antibiotic_prescriptions': antibiotic_prescriptions,
        'antibiotic_percentage': (antibiotic_prescriptions / total_prescriptions * 100) if total_prescriptions > 0 else 0,
        'multitherapy_prescriptions': multitherapy_prescriptions,
        'malaria_prescriptions': malaria_prescriptions,
        'malaria_percentage': (malaria_prescriptions / total_prescriptions * 100) if total_prescriptions > 0 else 0,
        'pregnant_women_prescriptions': pregnant_women_prescriptions,
        'children_under_5_prescriptions': children_under_5_prescriptions
    }
    
    serializer = PharmacoepidemioAnalysisSerializer(data)
    return Response(serializer.data)
