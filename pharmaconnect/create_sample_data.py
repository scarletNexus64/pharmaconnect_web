#!/usr/bin/env python
"""
Script pour créer des données d'exemple pour le système PharmaConnect
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmaconnect.settings')
django.setup()

from api.models import (
    Organization, Donor, HealthFacility, Project, 
    MedicationCategory, Medication, Alert
)

def create_sample_data():
    """Créer des données d'exemple"""
    
    print("🏗️ Création des données d'exemple...")
    
    # Récupérer l'organisation existante
    org = Organization.objects.get(code='ORG001')
    print(f"✅ Organisation trouvée: {org.name}")
    
    # Créer des bailleurs
    donors = []
    donor_data = [
        {'name': 'Fonds Mondial', 'code': 'GFATM', 'description': 'Fonds mondial de lutte contre le sida, la tuberculose et le paludisme'},
        {'name': 'USAID', 'code': 'USAID', 'description': 'Agence américaine pour le développement international'},
        {'name': 'Fondation Gates', 'code': 'GATES', 'description': 'Fondation Bill et Melinda Gates'}
    ]
    
    for data in donor_data:
        donor, created = Donor.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        donors.append(donor)
        print(f"{'✅ Créé' if created else '📌 Existant'}: Bailleur {donor.name}")
    
    # Récupérer la formation sanitaire existante
    health_facility = HealthFacility.objects.get(code='CS001')
    print(f"✅ Formation sanitaire trouvée: {health_facility.name}")
    
    # Créer des formations sanitaires supplémentaires
    additional_facilities = [
        {
            'name': 'Hôpital Général de Yaoundé',
            'code': 'HGY001',
            'type': 'HOSPITAL',
            'level_of_care': 'SECONDARY',
            'location': 'Yaoundé, Cameroun'
        },
        {
            'name': 'CS Intégré Douala',
            'code': 'CSI002',
            'type': 'CSI',
            'level_of_care': 'PRIMARY',
            'location': 'Douala, Cameroun'
        }
    ]
    
    facilities = [health_facility]
    for data in additional_facilities:
        facility, created = HealthFacility.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        facilities.append(facility)
        print(f"{'✅ Créée' if created else '📌 Existante'}: Formation {facility.name}")
    
    # Créer des projets
    project_data = [
        {
            'name': 'Lutte contre le Paludisme Nord Cameroun',
            'code': 'PALU001',
            'organization': org,
            'donor': donors[0],  # Fonds Mondial
            'health_facility': facilities[0],
            'start_date': datetime.now().date() - timedelta(days=365),
            'end_date': datetime.now().date() + timedelta(days=365),
            'order_frequency_months': 3,
            'delivery_delay_months': 1.5,
            'buffer_stock_months': 0.5
        },
        {
            'name': 'Programme VIH/SIDA Yaoundé',
            'code': 'VIH001',
            'organization': org,
            'donor': donors[1],  # USAID
            'health_facility': facilities[1],
            'start_date': datetime.now().date() - timedelta(days=180),
            'end_date': datetime.now().date() + timedelta(days=545),
            'order_frequency_months': 6,
            'delivery_delay_months': 2.0,
            'buffer_stock_months': 1.0
        },
        {
            'name': 'Santé Maternelle et Infantile',
            'code': 'SMI001',
            'organization': org,
            'donor': donors[2],  # Gates
            'health_facility': facilities[2],
            'start_date': datetime.now().date() - timedelta(days=90),
            'end_date': datetime.now().date() + timedelta(days=635),
            'order_frequency_months': 4,
            'delivery_delay_months': 1.0,
            'buffer_stock_months': 0.75
        }
    ]
    
    projects = []
    for data in project_data:
        project, created = Project.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        projects.append(project)
        print(f"{'✅ Créé' if created else '📌 Existant'}: Projet {project.name}")
    
    # Créer des catégories de médicaments
    categories_data = [
        {'name': 'Antipaludiques', 'code': 'PALU', 'description': 'Médicaments pour traiter le paludisme'},
        {'name': 'Antirétroviraux', 'code': 'ARV', 'description': 'Médicaments pour traiter le VIH/SIDA'},
        {'name': 'Antibiotiques', 'code': 'ANTI', 'description': 'Médicaments pour traiter les infections bactériennes'},
        {'name': 'Vitamines et Suppléments', 'code': 'VIT', 'description': 'Vitamines et suppléments nutritionnels'},
        {'name': 'Antalgiques', 'code': 'ANALG', 'description': 'Médicaments contre la douleur'}
    ]
    
    categories = []
    for data in categories_data:
        category, created = MedicationCategory.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        categories.append(category)
        print(f"{'✅ Créée' if created else '📌 Existante'}: Catégorie {category.name}")
    
    # Créer des médicaments
    medications_data = [
        # Antipaludiques
        {
            'code': 'ARTE80',
            'name': 'Artémether',
            'dosage': '80mg/ml',
            'form': 'Solution injectable',
            'packaging': 'Ampoule 1ml',
            'unit_price': 2.50,
            'category': categories[0],
            'therapeutic_class': 'Antipaludique',
            'is_active': True
        },
        {
            'code': 'LUME20',
            'name': 'Luméfantrine',
            'dosage': '20mg',
            'form': 'Comprimé',
            'packaging': 'Boîte de 24 comprimés',
            'unit_price': 5.00,
            'category': categories[0],
            'therapeutic_class': 'Antipaludique',
            'is_active': True
        },
        # Antirétroviraux
        {
            'code': 'EFV600',
            'name': 'Efavirenz',
            'dosage': '600mg',
            'form': 'Comprimé pelliculé',
            'packaging': 'Flacon de 30 comprimés',
            'unit_price': 15.00,
            'category': categories[1],
            'therapeutic_class': 'Antirétroviral',
            'is_active': True
        },
        # Antibiotiques
        {
            'code': 'AMOX500',
            'name': 'Amoxicilline',
            'dosage': '500mg',
            'form': 'Gélule',
            'packaging': 'Boîte de 12 gélules',
            'unit_price': 3.20,
            'category': categories[2],
            'therapeutic_class': 'Antibiotique',
            'is_active': True
        },
        {
            'code': 'COTRI480',
            'name': 'Cotrimoxazole',
            'dosage': '480mg',
            'form': 'Comprimé',
            'packaging': 'Boîte de 20 comprimés',
            'unit_price': 1.80,
            'category': categories[2],
            'therapeutic_class': 'Antibiotique',
            'is_active': True
        },
        # Vitamines
        {
            'code': 'FER200',
            'name': 'Fer + Acide folique',
            'dosage': '200mg + 0.25mg',
            'form': 'Comprimé',
            'packaging': 'Flacon de 60 comprimés',
            'unit_price': 4.50,
            'category': categories[3],
            'therapeutic_class': 'Supplément nutritionnel',
            'is_active': True
        },
        # Antalgiques
        {
            'code': 'PARA500',
            'name': 'Paracétamol',
            'dosage': '500mg',
            'form': 'Comprimé',
            'packaging': 'Boîte de 20 comprimés',
            'unit_price': 1.20,
            'category': categories[4],
            'therapeutic_class': 'Antalgique',
            'is_active': True
        }
    ]
    
    medications = []
    for data in medications_data:
        medication, created = Medication.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        medications.append(medication)
        print(f"{'✅ Créé' if created else '📌 Existant'}: Médicament {medication.name}")
    
    # Créer quelques alertes d'exemple
    alerts_data = [
        {
            'title': 'Rupture de stock Artémether',
            'message': 'Stock épuisé au CS Bangangté depuis 2 jours',
            'alert_type': 'STOCKOUT',
            'severity': 'CRITICAL',
            'organization': org,
            'is_active': True
        },
        {
            'title': 'Expiration proche - Lot AMOX123',
            'message': 'Lot d\'Amoxicilline expire dans 30 jours',
            'alert_type': 'EXPIRY',
            'severity': 'WARNING',
            'organization': org,
            'is_active': True
        },
        {
            'title': 'Pré-rupture Paracétamol',
            'message': 'Stock faible détecté - moins de 7 jours restants',
            'alert_type': 'LOW_STOCK',
            'severity': 'MEDIUM',
            'organization': org,
            'is_active': True
        }
    ]
    
    alerts = []
    for data in alerts_data:
        alert, created = Alert.objects.get_or_create(
            title=data['title'],
            defaults=data
        )
        alerts.append(alert)
        print(f"{'✅ Créée' if created else '📌 Existante'}: Alerte {alert.title}")
    
    print(f"\n🎉 Données d'exemple créées avec succès!")
    print(f"📊 Résumé:")
    print(f"   - {len(donors)} bailleurs")
    print(f"   - {len(facilities)} formations sanitaires")
    print(f"   - {len(projects)} projets")
    print(f"   - {len(categories)} catégories de médicaments")
    print(f"   - {len(medications)} médicaments")
    print(f"   - {len(alerts)} alertes")

if __name__ == '__main__':
    try:
        create_sample_data()
    except Exception as e:
        print(f"\n❌ Erreur lors de la création des données: {e}")
        sys.exit(1)