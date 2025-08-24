# config/colors.py - Centralized Color Configuration for the Application

"""
Color palette configuration for the dashboard application.
This module provides a centralized way to manage colors across all components,
making it easy to maintain consistency and update the color scheme globally.
"""

class ColorPalette:
    """
    Centralized color palette management for consistent theming across charts and UI.
    All colors are defined here and can be easily modified for global changes.
    """
    
    # Primary color scheme for general charts and UI elements
    PRIMARY = [
        '#2066a8',  # Dark Blue - Primary brand color
        '#3594cc',  # Med Blue - Secondary brand color
        '#8cc5e3',  # Light Blue - Accent color
        '#a00000',  # Dark Red - Strong accent
        '#c46666',  # Med Red - Medium accent
        '#d8a6a6'   # Light Red - Soft accent
    ]
    
    # Extended palette for pie charts and complex visualizations
    EXTENDED = [
        '#296899',  # Deep blue-gray
        '#274754',  # Dark slate
        '#cc7700',  # Orange-amber
        '#e8c468',  # Light amber
        '#ba454d',  # Burgundy
        '#2066a8',  # Primary blue (repeated for consistency)
        '#cdecec',  # Very light blue-gray
        '#8eclda',  # Soft cyan
        '#f6d6c2',  # Peach
        '#ededed',  # Light gray
        '#d47264',  # Coral
        '#ae282c'   # Deep red
    ]
    
    # Secondary/Accent colors (red scheme) for special emphasis
    SECONDARY = {
        50: '#fef2f2',   # Very light red
        100: '#fde2e2',  # Light red
        200: '#fbc6c6',  # Soft red
        300: '#f59898',  # Medium-light red
        400: '#ee6b6b',  # Medium red
        500: '#c92427',  # Main secondary color (primary red)
        600: '#b91c1c',  # Dark red
        700: '#991b1b',  # Darker red
        800: '#7f1d1d',  # Very dark red
        900: '#651515'   # Deepest red
    }
    
    # Neutral colors for backgrounds, borders, and text
    NEUTRAL = [
        '#374151',  # Dark gray
        '#6b7280',  # Medium-dark gray
        '#9ca3af',  # Medium gray
        '#d1d5db',  # Light-medium gray
        '#e5e7eb',  # Light gray
        '#f3f4f6',  # Very light gray
        '#f9fafb'   # Near white
    ]
    
    # Status colors for notifications and states
    STATUS = {
        'success': '#059669',   # Green for success states
        'warning': '#d97706',   # Amber for warning states
        'danger': '#c92427',    # Red for error states (matches secondary 500)
        'info': '#2066a8'       # Blue for info states (matches primary)
    }
    
    # Gradient combinations for special effects
    GRADIENTS = {
        'primary': ['#2066a8', '#3594cc'],      # Blue gradient
        'secondary': ['#c92427', '#b91c1c'],    # Red gradient
        'accent': ['#cc7700', '#e8c468'],       # Orange-amber gradient
        'neutral': ['#6b7280', '#9ca3af']       # Gray gradient
    }
    
    @classmethod
    def get_colors(cls, chart_type='primary', count=8):
        """
        Get colors based on chart type and required count.
        
        Args:
            chart_type (str): Type of chart ('primary', 'pie', 'doughnut', 'secondary', 'neutral')
            count (int): Number of colors needed
            
        Returns:
            list: List of hex color codes
        """
        if chart_type in ['pie', 'doughnut']:
            colors = cls.EXTENDED.copy()
        elif chart_type == 'secondary':
            # Use secondary colors, excluding very light ones
            colors = [cls.SECONDARY[key] for key in [200, 300, 400, 500, 600, 700, 800, 900]]
        elif chart_type == 'neutral':
            colors = cls.NEUTRAL.copy()
        else:  # primary or default
            colors = cls.PRIMARY.copy()
        
        # Extend colors if needed by cycling through the palette
        while len(colors) < count:
            colors.extend(cls.EXTENDED)
        
        return colors[:count]
    
    @classmethod
    def get_gradient_colors(cls, start_color, end_color, steps):
        """
        Generate gradient colors between two hex colors.
        
        Args:
            start_color (str): Starting hex color (e.g., '#2066a8')
            end_color (str): Ending hex color (e.g., '#8cc5e3')
            steps (int): Number of color steps to generate
            
        Returns:
            list: List of hex colors forming a gradient
        """
        def hex_to_rgb(hex_color):
            """Convert hex color to RGB tuple."""
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            """Convert RGB tuple to hex color."""
            return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        
        start_rgb = hex_to_rgb(start_color)
        end_rgb = hex_to_rgb(end_color)
        
        colors = []
        for i in range(steps):
            factor = i / (steps - 1) if steps > 1 else 0
            rgb = tuple(
                start_rgb[j] + factor * (end_rgb[j] - start_rgb[j])
                for j in range(3)
            )
            colors.append(rgb_to_hex(rgb))
        
        return colors
    
    @classmethod
    def get_transparent_colors(cls, colors, opacity=0.2):
        """
        Convert hex colors to RGBA with transparency.
        
        Args:
            colors (list): List of hex colors
            opacity (float): Opacity level (0.0 to 1.0)
            
        Returns:
            list: List of RGBA color strings
        """
        def hex_to_rgba(hex_color, alpha):
            """Convert hex color to RGBA string."""
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f'rgba({r}, {g}, {b}, {alpha})'
        
        return [hex_to_rgba(color, opacity) for color in colors]
    
    @classmethod
    def get_chart_colors(cls, chart_type, data_count, with_transparency=False, opacity=0.2):
        """
        Get appropriate colors for a specific chart with optional transparency.
        
        Args:
            chart_type (str): Type of chart
            data_count (int): Number of data points
            with_transparency (bool): Whether to include transparent versions
            opacity (float): Opacity for transparent colors
            
        Returns:
            dict: Dictionary containing 'colors' and optionally 'transparent_colors'
        """
        colors = cls.get_colors(chart_type, data_count)
        result = {'colors': colors}
        
        if with_transparency:
            result['transparent_colors'] = cls.get_transparent_colors(colors, opacity)
        
        return result
    
    @classmethod
    def get_status_color(cls, status):
        """
        Get color for a specific status.
        
        Args:
            status (str): Status type ('success', 'warning', 'danger', 'info')
            
        Returns:
            str: Hex color code
        """
        return cls.STATUS.get(status, cls.STATUS['info'])
    
    @classmethod
    def get_gradient(cls, gradient_name='primary'):
        """
        Get predefined gradient colors.
        
        Args:
            gradient_name (str): Name of gradient ('primary', 'secondary', 'accent', 'neutral')
            
        Returns:
            list: Two-color gradient [start_color, end_color]
        """
        return cls.GRADIENTS.get(gradient_name, cls.GRADIENTS['primary'])
    
    @classmethod
    def to_dict(cls):
        """
        Export all color configurations as a dictionary.
        Useful for API endpoints or frontend synchronization.
        
        Returns:
            dict: Complete color configuration
        """
        return {
            'primary': cls.PRIMARY,
            'extended': cls.EXTENDED,
            'secondary': cls.SECONDARY,
            'neutral': cls.NEUTRAL,
            'status': cls.STATUS,
            'gradients': cls.GRADIENTS
        }
    
    @classmethod
    def to_css_variables(cls):
        """
        Generate CSS custom properties for the color palette.
        
        Returns:
            str: CSS custom properties string
        """
        css_vars = [":root {"]
        
        # Primary colors
        for i, color in enumerate(cls.PRIMARY):
            css_vars.append(f"  --color-primary-{i+1}: {color};")
        
        # Extended colors
        for i, color in enumerate(cls.EXTENDED):
            css_vars.append(f"  --color-extended-{i+1}: {color};")
        
        # Secondary colors
        for key, color in cls.SECONDARY.items():
            css_vars.append(f"  --color-secondary-{key}: {color};")
        
        # Neutral colors
        for i, color in enumerate(cls.NEUTRAL):
            css_vars.append(f"  --color-neutral-{(i+1)*100}: {color};")
        
        # Status colors
        for status, color in cls.STATUS.items():
            css_vars.append(f"  --color-{status}: {color};")
        
        css_vars.append("}")
        return "\n".join(css_vars)

# Utility functions for easy access
def get_chart_colors(chart_type='primary', count=8):
    """Convenience function to get chart colors."""
    return ColorPalette.get_colors(chart_type, count)

def get_status_color(status):
    """Convenience function to get status color."""
    return ColorPalette.get_status_color(status)

def create_chart_data(chart_type, labels, values, dataset_label='Data', **kwargs):
    """
    Create standardized chart data with consistent color scheme.
    
    Args:
        chart_type (str): Type of chart ('pie', 'bar', 'line', etc.)
        labels (list): Chart labels
        values (list): Chart values
        dataset_label (str): Label for the dataset
        **kwargs: Additional chart options
        
    Returns:
        dict: Chart.js compatible data structure
    """
    color_count = len(labels) if labels else len(values) if isinstance(values, list) else 1
    colors = ColorPalette.get_colors(chart_type, color_count)
    
    if chart_type in ['pie', 'doughnut']:
        return {
            'labels': labels,
            'datasets': [{
                'data': values,
                'backgroundColor': colors,
                'borderColor': '#ffffff',
                'borderWidth': 3,
                'hoverBorderWidth': 4,
                'hoverOffset': 8,
                **kwargs
            }]
        }
    elif chart_type == 'bar':
        return {
            'labels': labels,
            'datasets': [{
                'label': dataset_label,
                'data': values,
                'backgroundColor': colors,
                'borderColor': colors,
                'borderWidth': 0,
                'borderRadius': 8,
                'borderSkipped': False,
                **kwargs
            }]
        }
    elif chart_type == 'line':
        transparent_colors = ColorPalette.get_transparent_colors(colors, 0.2)
        return {
            'labels': labels,
            'datasets': [{
                'label': dataset_label,
                'data': values,
                'backgroundColor': transparent_colors[0] if transparent_colors else f'{colors[0]}20',
                'borderColor': colors[0],
                'borderWidth': 3,
                'tension': 0.4,
                'fill': False,
                'pointBackgroundColor': '#ffffff',
                'pointBorderColor': colors[0],
                'pointBorderWidth': 2,
                'pointRadius': 4,
                **kwargs
            }]
        }
    else:
        return {
            'labels': labels,
            'datasets': [{
                'label': dataset_label,
                'data': values,
                'backgroundColor': colors,
                'borderColor': colors,
                'borderWidth': 1,
                **kwargs
            }]
        }

def create_stacked_chart_data(labels, datasets_info):
    """
    Create stacked chart data with consistent color scheme.
    
    Args:
        labels (list): Chart labels
        datasets_info (list): List of tuples (label, data)
        
    Returns:
        dict: Chart.js compatible stacked chart data
    """
    colors = ColorPalette.get_colors('primary', len(datasets_info))
    
    datasets = []
    for i, (label, data) in enumerate(datasets_info):
        datasets.append({
            'label': label,
            'data': data,
            'backgroundColor': colors[i % len(colors)],
            'borderColor': colors[i % len(colors)],
            'borderWidth': 0,
            'borderRadius': 6,
            'borderSkipped': False
        })
    
    return {
        'labels': labels,
        'datasets': datasets
    }

# Export main color palette for easy importing
COLORS = ColorPalette.to_dict()

# Example usage and testing
if __name__ == "__main__":
    # Test the color palette
    print("Primary Colors:", ColorPalette.PRIMARY)
    print("Extended Colors:", ColorPalette.EXTENDED)
    print("Chart Colors (pie, 8):", ColorPalette.get_colors('pie', 8))
    print("Status Success Color:", ColorPalette.get_status_color('success'))
    print("Primary Gradient:", ColorPalette.get_gradient('primary'))
    
    # Test chart data creation
    sample_data = create_chart_data('bar', ['A', 'B', 'C'], [10, 20, 30], 'Sample Data')
    print("Sample Chart Data:", sample_data)