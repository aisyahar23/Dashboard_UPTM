import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # UI Configuration
    BRAND_COLORS = {
        'primary': '#074e7e',
        'secondary': '#c92427',
        'success': '#10b981',
        'warning': '#f59e0b',
        'info': '#3b82f6',
        'neutral': '#6b7280'
    }
    
    # Chart Configuration
    CHART_DEFAULTS = {
        'animation_duration': 750,
        'responsive': True,
        'maintain_aspect_ratio': False
    }
    
    # Data Configuration
    ITEMS_PER_PAGE = 50
    MAX_EXPORT_ROWS = 10000
    
    # Database configuration (if needed later)
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///graduate_analytics.db'