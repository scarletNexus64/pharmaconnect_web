#!/usr/bin/env python
"""
Script pour créer des données de test pour le stock
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmaconnect.settings')
django.setup()

from api.models import (
    Organization, Project, Medication, MedicationCategory,
    StockEntry, HealthFacility, Donor
)


def create_stock_test_data():
    """Créer des données de test pour le stock"""
    print("🚀 Création de données de test pour le stock...")

    # Récupérer ou créer une organisation de test
    org, created = Organization.objects.get_or_create(
        code='TEST_ORG',
        defaults={
            'name': 'Organisation Test',
            'type': 'NGO',
            'country': 'Mali'
        }
    )
    if created:
        print(f"✅ Organisation créée: {org.name}")
    else:
        print(f"ℹ️  Organisation existante: {org.name}")

    # Récupérer ou créer un bailleur
    donor, created = Donor.objects.get_or_create(
        code='DONOR_TEST',
        defaults={
            'name': 'Bailleur Test',
            'description': 'Bailleur de fonds pour les tests'
        }
    )
    if created:
        print(f"✅ Bailleur créé: {donor.name}")

    # Récupérer ou créer une formation sanitaire
    facility, created = HealthFacility.objects.get_or_create(
        code='FS_TEST_001',
        defaults={
            'name': 'Formation Sanitaire Test',
            'type': 'CSI',
            'level_of_care': 'PRIMARY',
            'location': 'Bamako, Mali'
        }
    )
    if created:
        print(f"✅ Formation sanitaire créée: {facility.name}")

    # Récupérer ou créer un projet
    project, created = Project.objects.get_or_create(
        code='PROJ_TEST_001',
        defaults={
            'name': 'Projet Test Stock',
            'organization': org,
            'donor': donor,
            'health_facility': facility,
            'start_date': datetime.now().date(),
            'end_date': (datetime.now() + timedelta(days=365)).date(),
            'order_frequency_months': 3,
            'delivery_delay_months': Decimal('1.0'),
            'buffer_stock_months': Decimal('0.5')
        }
    )
    if created:
        print(f"✅ Projet créé: {project.name}")

    # Créer ou récupérer des catégories de médicaments
    category_arv, _ = MedicationCategory.objects.get_or_create(
        code='ARV',
        organization=org,
        defaults={
            'name': 'Antirétroviraux',
            'description': 'Médicaments pour le traitement du VIH/SIDA'
        }
    )

    category_paludisme, _ = MedicationCategory.objects.get_or_create(
        code='PALU',
        organization=org,
        defaults={
            'name': 'Antipaludiques',
            'description': 'Médicaments pour le traitement du paludisme'
        }
    )

    print(f"✅ Catégories de médicaments créées")

    # Créer des médicaments de test
    medications_data = [
        {
            'code': 'MED_001',
            'name': 'Efavirenz',
            'designation': 'Efavirenz 600mg comprimé',
            'dosage': '600mg',
            'form': 'Comprimé',
            'packaging': 'Boîte de 30 comprimés',
            'unit_price': Decimal('15000'),
            'category': category_arv,
            'therapeutic_class': 'Antirétroviral',
            'administration_route': 'ORAL'
        },
        {
            'code': 'MED_002',
            'name': 'Lamivudine',
            'designation': 'Lamivudine 150mg comprimé',
            'dosage': '150mg',
            'form': 'Comprimé',
            'packaging': 'Boîte de 60 comprimés',
            'unit_price': Decimal('8000'),
            'category': category_arv,
            'therapeutic_class': 'Antirétroviral',
            'administration_route': 'ORAL'
        },
        {
            'code': 'MED_003',
            'name': 'Artéméther + Luméfantrine',
            'designation': 'Artéméther 20mg + Luméfantrine 120mg comprimé',
            'dosage': '20mg + 120mg',
            'form': 'Comprimé',
            'packaging': 'Boîte de 24 comprimés',
            'unit_price': Decimal('5000'),
            'category': category_paludisme,
            'therapeutic_class': 'Antipaludique',
            'administration_route': 'ORAL'
        },
        {
            'code': 'MED_004',
            'name': 'Artésunate injectable',
            'designation': 'Artésunate 60mg injectable',
            'dosage': '60mg',
            'form': 'Injectable',
            'packaging': 'Boîte de 6 ampoules',
            'unit_price': Decimal('12000'),
            'category': category_paludisme,
            'therapeutic_class': 'Antipaludique',
            'administration_route': 'IV'
        },
        {
            'code': 'MED_005',
            'name': 'Ténofovir',
            'designation': 'Ténofovir 300mg comprimé',
            'dosage': '300mg',
            'form': 'Comprimé',
            'packaging': 'Boîte de 30 comprimés',
            'unit_price': Decimal('18000'),
            'category': category_arv,
            'therapeutic_class': 'Antirétroviral',
            'administration_route': 'ORAL'
        }
    ]

    medications = []
    for med_data in medications_data:
        med, created = Medication.objects.get_or_create(
            code=med_data['code'],
            organization=org,
            defaults=med_data
        )
        medications.append(med)
        if created:
            print(f"✅ Médicament créé: {med.name}")

    # Créer des entrées de stock
    stock_entries_data = [
        # Stock normal - livré récemment, expiration lointaine
        {
            'medication': medications[0],  # Efavirenz
            'delivery_date': (datetime.now() - timedelta(days=15)).date(),
            'quantity_ordered': 1000,
            'quantity_delivered': 1000,
            'expiry_date': (datetime.now() + timedelta(days=700)).date(),
            'unit_price': Decimal('15000'),
            'supplier': 'PharmaCorp International',
            'batch_number': 'EFV-2024-001'
        },
        # Stock avec réception partielle
        {
            'medication': medications[1],  # Lamivudine
            'delivery_date': (datetime.now() - timedelta(days=30)).date(),
            'quantity_ordered': 500,
            'quantity_delivered': 450,
            'expiry_date': (datetime.now() + timedelta(days=600)).date(),
            'unit_price': Decimal('8000'),
            'supplier': 'MediSupply SARL',
            'batch_number': 'LAM-2024-002'
        },
        # Stock proche de l'expiration (60 jours)
        {
            'medication': medications[2],  # Artéméther + Luméfantrine
            'delivery_date': (datetime.now() - timedelta(days=300)).date(),
            'quantity_ordered': 800,
            'quantity_delivered': 800,
            'expiry_date': (datetime.now() + timedelta(days=60)).date(),
            'unit_price': Decimal('5000'),
            'supplier': 'Global Health Suppliers',
            'batch_number': 'ART-2023-045'
        },
        # Stock expiré
        {
            'medication': medications[3],  # Artésunate injectable
            'delivery_date': (datetime.now() - timedelta(days=400)).date(),
            'quantity_ordered': 200,
            'quantity_delivered': 200,
            'expiry_date': (datetime.now() - timedelta(days=10)).date(),
            'unit_price': Decimal('12000'),
            'supplier': 'AfriMed Distribution',
            'batch_number': 'ARS-2023-012'
        },
        # Stock normal mais grande quantité
        {
            'medication': medications[4],  # Ténofovir
            'delivery_date': (datetime.now() - timedelta(days=5)).date(),
            'quantity_ordered': 2000,
            'quantity_delivered': 2000,
            'expiry_date': (datetime.now() + timedelta(days=800)).date(),
            'unit_price': Decimal('18000'),
            'supplier': 'PharmaCorp International',
            'batch_number': 'TEN-2024-089'
        },
        # Stock avec expiration dans 45 jours
        {
            'medication': medications[0],  # Efavirenz (ancien lot)
            'delivery_date': (datetime.now() - timedelta(days=320)).date(),
            'quantity_ordered': 500,
            'quantity_delivered': 500,
            'expiry_date': (datetime.now() + timedelta(days=45)).date(),
            'unit_price': Decimal('15000'),
            'supplier': 'MediSupply SARL',
            'batch_number': 'EFV-2023-067'
        },
        # Stock normal
        {
            'medication': medications[1],  # Lamivudine
            'delivery_date': (datetime.now() - timedelta(days=10)).date(),
            'quantity_ordered': 1200,
            'quantity_delivered': 1200,
            'expiry_date': (datetime.now() + timedelta(days=650)).date(),
            'unit_price': Decimal('8000'),
            'supplier': 'Global Health Suppliers',
            'batch_number': 'LAM-2024-078'
        }
    ]

    created_count = 0
    for stock_data in stock_entries_data:
        stock, created = StockEntry.objects.get_or_create(
            organization=org,
            project=project,
            medication=stock_data['medication'],
            batch_number=stock_data['batch_number'],
            defaults={
                'delivery_date': stock_data['delivery_date'],
                'quantity_ordered': stock_data['quantity_ordered'],
                'quantity_delivered': stock_data['quantity_delivered'],
                'expiry_date': stock_data['expiry_date'],
                'unit_price': stock_data['unit_price'],
                'supplier': stock_data['supplier']
            }
        )
        if created:
            created_count += 1
            # Afficher le statut de l'entrée
            days_until_expiry = (stock.expiry_date - datetime.now().date()).days
            if days_until_expiry < 0:
                status = "❌ EXPIRÉ"
            elif days_until_expiry <= 90:
                status = f"⚠️  Expire dans {days_until_expiry} jours"
            else:
                status = "✅ Normal"
            print(f"  • {stock.medication.name} (Lot: {stock.batch_number}) - {status}")

    print(f"\n✅ {created_count} entrées de stock créées sur {len(stock_entries_data)}")

    # Afficher un résumé
    total_value = sum(
        (entry.quantity_delivered * entry.unit_price)
        for entry in StockEntry.objects.filter(organization=org)
    )
    print(f"\n📊 Résumé du stock:")
    print(f"   - Total d'entrées: {StockEntry.objects.filter(organization=org).count()}")
    print(f"   - Valeur totale: {total_value:,.0f} XOF")
    print(f"   - Médicaments différents: {Medication.objects.filter(organization=org).count()}")

    expired_count = StockEntry.objects.filter(
        organization=org,
        expiry_date__lt=datetime.now().date()
    ).count()
    expiring_soon = StockEntry.objects.filter(
        organization=org,
        expiry_date__gte=datetime.now().date(),
        expiry_date__lt=(datetime.now() + timedelta(days=90)).date()
    ).count()

    print(f"   - Produits expirés: {expired_count}")
    print(f"   - Produits expirant bientôt (<90j): {expiring_soon}")

    print("\n✅ Données de test créées avec succès!")
    print(f"\n💡 Vous pouvez maintenant vous connecter et tester la page Stock")
    print(f"   Organization: {org.name} (code: {org.code})")
    print(f"   Projet: {project.name} (code: {project.code})")


if __name__ == '__main__':
    create_stock_test_data()
