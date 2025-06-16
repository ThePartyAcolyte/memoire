"""
Chunking configuration section.
"""

from .base import ConfigSection


class ChunkingSection(ConfigSection):
    """Chunking configuration section."""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent, config_manager)
        self.create_section()
    
    def create_section(self):
        """Create the chunking section."""
        self.create_section_frame("Memory & Chunking", requires_restart=True)
        
        # Min Chunk Words
        self.min_words_entry = self.add_field(
            0, "Min Chunk Words:", "entry",
            width=100
        )
        self.min_words_entry.bind("<FocusOut>", self.update_min_words)
        
        # Max Chunk Words
        self.max_words_entry = self.add_field(
            1, "Max Chunk Words:", "entry",
            width=100
        )
        self.max_words_entry.bind("<FocusOut>", self.update_max_words)
        
        # Semantic Overlap Threshold
        self.overlap_slider, self.overlap_value_label = self.add_slider_with_value(
            2, "Semantic Overlap:",
            from_=0.5,
            to=1.0,
            number_of_steps=10,
            command=self.update_overlap_threshold
        )
    
    def load_values(self):
        """Load configuration values."""
        # Min chunk words
        min_words = self.config.get('chunking.min_chunk_words', 20)
        self.min_words_entry.delete(0, "end")
        self.min_words_entry.insert(0, str(min_words))
        
        # Max chunk words
        max_words = self.config.get('chunking.max_chunk_words', 150)
        self.max_words_entry.delete(0, "end")
        self.max_words_entry.insert(0, str(max_words))
        
        # Semantic overlap threshold
        overlap = self.config.get('chunking.semantic_overlap_threshold', 0.9)
        self.overlap_slider.set(overlap)
        self.overlap_value_label.configure(text=f"{overlap:.2f}")
    
    def update_min_words(self, event=None):
        """Update min chunk words."""
        try:
            value = int(self.min_words_entry.get())
            self.update_config('chunking.min_chunk_words', value, requires_restart=True)
        except ValueError:
            # Reset to current value on invalid input
            current = self.config.get('chunking.min_chunk_words', 20)
            self.min_words_entry.delete(0, "end")
            self.min_words_entry.insert(0, str(current))
    
    def update_max_words(self, event=None):
        """Update max chunk words."""
        try:
            value = int(self.max_words_entry.get())
            self.update_config('chunking.max_chunk_words', value, requires_restart=True)
        except ValueError:
            # Reset to current value on invalid input
            current = self.config.get('chunking.max_chunk_words', 150)
            self.max_words_entry.delete(0, "end")
            self.max_words_entry.insert(0, str(current))
    
    def update_overlap_threshold(self, value):
        """Update semantic overlap threshold."""
        rounded_value = round(float(value), 2)
        self.update_config('chunking.semantic_overlap_threshold', rounded_value, requires_restart=True)
        self.overlap_value_label.configure(text=f"{rounded_value:.2f}")
