"""
Configuration Jazzmin en français pour l'interface admin de PharmaConnect
"""

JAZZMIN_SETTINGS = {
    # Titre de l'administration
    "site_title": "PharmaConnect Admin",
    "site_header": "PharmaConnect",
    "site_brand": "PharmaConnect",
    "login_logo": None,
    "login_logo_dark": None,
    "site_logo": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    
    # Texte de bienvenue
    "welcome_sign": "Bienvenue dans l'administration PharmaConnect",
    "copyright": "PharmaConnect - Gestion pharmaceutique pour ONG",
    
    # Recherche dans l'en-tête
    "search_model": ["api.Medication", "api.Organization", "api.Project"],
    
    # User menu on the top right
    "user_avatar": None,
    
    # Sidebar
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    
    # Configuration des applications dans le menu
    "order_with_respect_to": [
        "api",
        "auth",
    ],
    
    # Menu personnalisé en français
    "custom_links": {
        "api": [{
            "name": "Tableau de bord",
            "url": "admin:index",
            "icon": "fas fa-tachometer-alt",
            "permissions": ["api.view_user"]
        }]
    },
    
    # Top Menu - Entièrement en français
    "topmenu_links": [
        {"name": "Accueil", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Documentation API", "url": "/api/docs/", "new_window": True},
        {"name": "Site Web", "url": "/", "new_window": True},
        {"app": "api"},
    ],
    
    # User Menu - En français
    "usermenu_links": [
        {"name": "Mon Profil", "url": "admin:api_user_change", "icon": "fas fa-user"},
        {"name": "Déconnexion", "url": "admin:logout", "icon": "fas fa-sign-out-alt"},
    ],
    
    # Sidebar icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "api.Organization": "fas fa-building",
        "api.Donor": "fas fa-hand-holding-heart",
        "api.HealthFacility": "fas fa-hospital",
        "api.Project": "fas fa-project-diagram",
        "api.User": "fas fa-user-md",
        "api.MedicationCategory": "fas fa-list",
        "api.Medication": "fas fa-pills",
        "api.StandardList": "fas fa-clipboard-list",
        "api.MedicationSubstitution": "fas fa-exchange-alt",
        "api.StockEntry": "fas fa-boxes",
        "api.PrescriptionPhoto": "fas fa-camera",
        "api.Dispensation": "fas fa-hand-holding-medical",
        "api.DispensationItem": "fas fa-prescription-bottle",
        "api.Inventory": "fas fa-warehouse",
        "api.InventoryItem": "fas fa-box-open",
        "api.ConsumptionData": "fas fa-chart-line",
        "api.StockoutPeriod": "fas fa-exclamation-triangle",
        "api.Alert": "fas fa-bell",
    },
    
    # Icônes par défaut
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # Liens utiles
    "related_modal_active": False,
    
    # Custom CSS/JS
    "custom_css": None,
    "custom_js": None,
    
    # Whether to display the side menu
    "show_ui_builder": False,
    
    # Thème
    "theme": "flatly",
    "dark_mode_theme": "darkly",
    
    # Navbar
    "navbar_small_text": False,
    "footer_small_text": False,
    
    # Sidebar
    "sidebar_disable_expand": False,
    "sidebar_nav_small_text": False,
    "sidebar_nav_flat_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_compact_style": False,
    
    # Utilisation des icônes personnalisées
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    
    # Changement des libellés de l'interface
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "horizontal_tabs",
        "auth.group": "horizontal_tabs",
    },
    
    # Libellés personnalisés en français pour les applications
    "custom_apps": {
        "api": {
            "name": "Gestion PharmaConnect",
            "icon": "fas fa-heartbeat",
            "models": {
                "Organization": {
                    "name": "Organisations",
                    "icon": "fas fa-building",
                },
                "Donor": {
                    "name": "Bailleurs de fonds",
                    "icon": "fas fa-hand-holding-heart",
                },
                "HealthFacility": {
                    "name": "Formations sanitaires",
                    "icon": "fas fa-hospital",
                },
                "Project": {
                    "name": "Projets",
                    "icon": "fas fa-project-diagram",
                },
                "User": {
                    "name": "Utilisateurs",
                    "icon": "fas fa-user-md",
                },
                "MedicationCategory": {
                    "name": "Catégories de médicaments",
                    "icon": "fas fa-list",
                },
                "Medication": {
                    "name": "Médicaments",
                    "icon": "fas fa-pills",
                },
                "StandardList": {
                    "name": "Listes standard",
                    "icon": "fas fa-clipboard-list",
                },
                "MedicationSubstitution": {
                    "name": "Substitutions",
                    "icon": "fas fa-exchange-alt",
                },
                "StockEntry": {
                    "name": "Entrées en stock",
                    "icon": "fas fa-boxes",
                },
                "PrescriptionPhoto": {
                    "name": "Photos d'ordonnances",
                    "icon": "fas fa-camera",
                },
                "Dispensation": {
                    "name": "Dispensations",
                    "icon": "fas fa-hand-holding-medical",
                },
                "Inventory": {
                    "name": "Inventaires",
                    "icon": "fas fa-warehouse",
                },
                "ConsumptionData": {
                    "name": "Données de consommation",
                    "icon": "fas fa-chart-line",
                },
                "StockoutPeriod": {
                    "name": "Périodes de rupture",
                    "icon": "fas fa-exclamation-triangle",
                },
                "Alert": {
                    "name": "Alertes",
                    "icon": "fas fa-bell",
                },
            }
        },
        "auth": {
            "name": "Authentification et autorisations",
            "icon": "fas fa-users-cog",
            "models": {
                "Group": {
                    "name": "Groupes",
                    "icon": "fas fa-users",
                },
            }
        }
    },
}

# Configuration UI Builder
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-primary navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success"
    },
    "actions_sticky_top": True
}