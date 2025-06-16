"""
Intelligence Engine configuration section.
"""

from .base import ConfigSection


class IntelligenceSection(ConfigSection):
    """Intelligence engine configuration section."""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent, config_manager)
        self.create_section()
    
    def create_section(self):
        """Create the intelligence section."""
        self.create_section_frame("Intelligence Engine", requires_restart=False)
        
        # Enable Curation
        self.curation_switch = self.add_field(
            0, "Enable Curation:", "switch",
            command=self.update_curation
        )
        
        # Curation Similarity Threshold
        self.curation_threshold_slider, self.curation_threshold_value_label = self.add_slider_with_value(
            1, "Curation Threshold:",
            from_=0.1,
            to=1.0,
            number_of_steps=18,
            command=self.update_curation_threshold
        )
        
        # Curation Search Threshold  
        self.curation_search_slider, self.curation_search_value_label = self.add_slider_with_value(
            2, "Curation Search Threshold:",
            from_=0.1,
            to=1.0,
            number_of_steps=18,
            command=self.update_curation_search_threshold
        )
    
    def load_values(self):
        """Load configuration values."""
        # Curation
        curation = self.config.get('intelligence.enable_curation', True)
        if curation:
            self.curation_switch.select()
        else:
            self.curation_switch.deselect()
        
        # Curation threshold
        curation_threshold = self.config.get('intelligence.curation_similarity_threshold', 0.54)
        self.curation_threshold_slider.set(curation_threshold)
        self.curation_threshold_value_label.configure(text=f"{curation_threshold:.2f}")
        
        # Curation search threshold
        curation_search = self.config.get('intelligence.curation_search_threshold', 0.4)
        self.curation_search_slider.set(curation_search)
        self.curation_search_value_label.configure(text=f"{curation_search:.2f}")
    
    def update_curation(self):
        """Update curation setting."""
        value = self.curation_switch.get() == 1
        self.update_config('intelligence.enable_curation', value, requires_restart=False)
    
    def update_curation_threshold(self, value):
        """Update curation threshold."""
        rounded_value = round(float(value), 2)
        self.update_config('intelligence.curation_similarity_threshold', rounded_value, requires_restart=False)
        self.curation_threshold_value_label.configure(text=f"{rounded_value:.2f}")
    
    def update_curation_search_threshold(self, value):
        """Update curation search threshold."""
        rounded_value = round(float(value), 2)
        self.update_config('intelligence.curation_search_threshold', rounded_value, requires_restart=False)
        self.curation_search_value_label.configure(text=f"{rounded_value:.2f}")
