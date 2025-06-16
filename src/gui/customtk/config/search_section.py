"""
Search and Retrieval configuration section.
"""

from .base import ConfigSection


class SearchSection(ConfigSection):
    """Search and retrieval configuration section."""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent, config_manager)
        self.create_section()
    
    def create_section(self):
        """Create the search section."""
        self.create_section_frame("Search & Retrieval", requires_restart=False)
        
        # Similarity Threshold
        self.threshold_slider, self.threshold_value_label = self.add_slider_with_value(
            0, "Similarity Threshold:",
            from_=0.1,
            to=1.0,
            number_of_steps=18,
            command=self.update_threshold
        )
        
        # Max Results
        self.results_entry = self.add_field(
            1, "Max Search Results:", "entry",
            width=100
        )
        self.results_entry.bind("<FocusOut>", self.update_max_results)
    
    def load_values(self):
        """Load configuration values."""
        # Similarity threshold
        threshold = self.config.get('search.similarity_threshold', 0.54)
        self.threshold_slider.set(threshold)
        self.threshold_value_label.configure(text=f"{threshold:.2f}")
        
        # Max results
        max_results = self.config.get('search.max_results', 50)
        self.results_entry.delete(0, "end")
        self.results_entry.insert(0, str(max_results))
    
    def update_threshold(self, value):
        """Update similarity threshold."""
        rounded_value = round(float(value), 2)
        self.update_config('search.similarity_threshold', rounded_value, requires_restart=False)
        self.threshold_value_label.configure(text=f"{rounded_value:.2f}")
    
    def update_max_results(self, event=None):
        """Update max results."""
        try:
            value = int(self.results_entry.get())
            self.update_config('search.max_results', value, requires_restart=False)
        except ValueError:
            # Reset to current value on invalid input
            current = self.config.get('search.max_results', 50)
            self.results_entry.delete(0, "end")
            self.results_entry.insert(0, str(current))
