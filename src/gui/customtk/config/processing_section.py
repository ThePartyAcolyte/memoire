"""
Processing Models configuration section.
"""

from .base import ConfigSection


class ProcessingSection(ConfigSection):
    """Processing models configuration section."""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent, config_manager)
        self.create_section()
    
    def create_section(self):
        """Create the processing section."""
        self.create_section_frame("Processing Models", requires_restart=True)
        
        # Processing Model
        self.model_combo = self.add_field(
            0, "Processing Model:", "combo",
            values=[
                "gemini-2.5-flash-preview-05-20",  # default
                "gemini-2.5-pro-preview-06-05",
                "gemini-2.0-flash",
                "gemini-2.0-flash-lite"
            ],
            command=self.update_model
        )
        
        # Temperature
        self.temperature_slider, self.temperature_value_label = self.add_slider_with_value(
            1, "Temperature:",
            from_=0.0,
            to=1.0,
            number_of_steps=20,
            command=self.update_temperature
        )
        
        # Max Tokens
        self.tokens_entry = self.add_field(
            2, "Max Tokens:", "entry",
            width=100
        )
        self.tokens_entry.bind("<FocusOut>", self.update_max_tokens)
        
        # Embedding Model
        self.embedding_combo = self.add_field(
            3, "Embedding Model:", "combo",
            values=[
                "text-embedding-004",
                "text-embedding-005"
            ],
            command=self.update_embedding_model
        )
    
    def load_values(self):
        """Load configuration values."""
        # Processing model
        current_model = self.config.get('processing.model', 'gemini-2.5-flash-preview-05-20')
        self.model_combo.set(current_model)
        
        # Temperature
        temperature = self.config.get('processing.temperature', 0.3)
        self.temperature_slider.set(temperature)
        self.temperature_value_label.configure(text=f"{temperature:.2f}")
        
        # Max tokens
        max_tokens = self.config.get('processing.max_tokens', 8192)
        self.tokens_entry.delete(0, "end")
        self.tokens_entry.insert(0, str(max_tokens))
        
        # Embedding model
        embedding_model = self.config.get('embedding.model', 'text-embedding-004')
        self.embedding_combo.set(embedding_model)
    
    def update_model(self, value):
        """Update processing model."""
        self.update_config('processing.model', value, requires_restart=True)
    
    def update_temperature(self, value):
        """Update temperature."""
        rounded_value = round(float(value), 2)
        self.update_config('processing.temperature', rounded_value, requires_restart=False)
        self.temperature_value_label.configure(text=f"{rounded_value:.2f}")
    
    def update_max_tokens(self, event=None):
        """Update max tokens."""
        try:
            value = int(self.tokens_entry.get())
            self.update_config('processing.max_tokens', value, requires_restart=True)
        except ValueError:
            # Reset to current value on invalid input
            current = self.config.get('processing.max_tokens', 8192)
            self.tokens_entry.delete(0, "end")
            self.tokens_entry.insert(0, str(current))
    
    def update_embedding_model(self, value):
        """Update embedding model."""
        self.update_config('embedding.model', value, requires_restart=True)
