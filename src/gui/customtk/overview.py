"""
Overview tab for MnemoX GUI.
System statistics and metrics only (projects moved to dedicated tab).
"""

import customtkinter as ctk
import logging
import psutil
from pathlib import Path

logger = logging.getLogger(__name__)


class OverviewTab:
    """Overview tab containing system statistics and metrics."""
    
    def __init__(self, parent, storage, embedding, memory, config):
        self.parent = parent
        self.storage = storage
        self.embedding = embedding
        self.memory = memory
        self.config = config
        
        self.overview_frame = None
        self.stats_cards = {}
        
        self.create_overview()
    
    def create_overview(self):
        """Create overview tab content."""
        self.overview_frame = ctk.CTkScrollableFrame(self.parent)
        self.overview_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self.overview_frame,
            text="System Overview",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        # Stats grid
        self.create_stats_section()
        
        # System info section
        self.create_system_info_section()
        
        # Performance section
        self.create_performance_section()
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            self.overview_frame,
            text="🔄 Refresh",
            command=self.refresh_stats,
            width=120,
            height=35
        )
        refresh_btn.grid(row=4, column=0, pady=20)
    
    def create_stats_section(self):
        """Create statistics cards section."""
        stats_frame = ctk.CTkFrame(self.overview_frame)
        stats_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        stats_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Stats cards
        self.stats_cards["projects"] = self.create_stat_card(stats_frame, "Projects", "0", 0, 0)
        self.stats_cards["fragments"] = self.create_stat_card(stats_frame, "Total Fragments", "0", 0, 1)
        self.stats_cards["contexts"] = self.create_stat_card(stats_frame, "Total Contexts", "0", 1, 0)
        self.stats_cards["memory"] = self.create_stat_card(stats_frame, "RAM Usage", "0 MB", 1, 1)
    
    def create_system_info_section(self):
        """Create system information section with clarified metrics."""
        system_frame = ctk.CTkFrame(self.overview_frame)
        system_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        system_frame.grid_columnconfigure(1, weight=1)
        
        system_title = ctk.CTkLabel(
            system_frame,
            text="System Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        system_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 10))
        
        # Storage size (disk usage)
        self.storage_size_label = ctk.CTkLabel(
            system_frame, 
            text="💾 Disk Storage: 0 MB",
            font=ctk.CTkFont(size=12)
        )
        self.storage_size_label.grid(row=1, column=0, sticky="w", padx=20, pady=5)
        
        # API usage estimate
        self.api_usage_label = ctk.CTkLabel(
            system_frame, 
            text="🌐 API Calls (est.): ~0 calls",
            font=ctk.CTkFont(size=12)
        )
        self.api_usage_label.grid(row=2, column=0, sticky="w", padx=20, pady=5)
        
        # Process info
        self.process_info_label = ctk.CTkLabel(
            system_frame, 
            text="⚡ Process: Active",
            font=ctk.CTkFont(size=12),
            text_color=("#10B981", "#059669")
        )
        self.process_info_label.grid(row=3, column=0, sticky="w", padx=20, pady=5)
        
        # MCP Status
        self.mcp_status_label = ctk.CTkLabel(
            system_frame, 
            text="🔗 MCP Server: Running",
            font=ctk.CTkFont(size=12),
            text_color=("#10B981", "#059669")
        )
        self.mcp_status_label.grid(row=4, column=0, sticky="w", padx=20, pady=(5, 15))
    
    def create_performance_section(self):
        """Create performance metrics section."""
        perf_frame = ctk.CTkFrame(self.overview_frame)
        perf_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        perf_frame.grid_columnconfigure(1, weight=1)
        
        perf_title = ctk.CTkLabel(
            perf_frame,
            text="Performance Metrics",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        perf_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 10))
        
        # CPU usage
        self.cpu_usage_label = ctk.CTkLabel(
            perf_frame, 
            text="🖥️ CPU Usage: 0%",
            font=ctk.CTkFont(size=12)
        )
        self.cpu_usage_label.grid(row=1, column=0, sticky="w", padx=20, pady=5)
        
        # Memory percentage
        self.memory_percent_label = ctk.CTkLabel(
            perf_frame, 
            text="📊 Memory Usage: 0%",
            font=ctk.CTkFont(size=12)
        )
        self.memory_percent_label.grid(row=2, column=0, sticky="w", padx=20, pady=5)
        
        # Uptime
        self.uptime_label = ctk.CTkLabel(
            perf_frame, 
            text="⏱️ Uptime: 0s",
            font=ctk.CTkFont(size=12)
        )
        self.uptime_label.grid(row=3, column=0, sticky="w", padx=20, pady=(5, 15))
    
    def create_stat_card(self, parent, title, value, row, col):
        """Create a statistics card."""
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
        card.grid_columnconfigure(0, weight=1)
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#3B82F6", "#60A5FA")
        )
        value_label.grid(row=0, column=0, padx=20, pady=(15, 5))
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        title_label.grid(row=1, column=0, padx=20, pady=(0, 15))
        
        return {"value": value_label, "title": title_label}
    
    def refresh_stats(self):
        """Refresh statistics data."""
        try:
            logger.info("Refreshing overview stats...")
            
            # Get stats from backend
            projects = self.storage.list_projects()
            total_fragments = 0
            total_contexts = 0
            
            for project in projects:
                try:
                    fragments = self.storage.list_fragments_by_project(project.id, limit=10000)
                    contexts = self.storage.list_contexts_by_project(project.id)
                    total_fragments += len(fragments)
                    total_contexts += len(contexts)
                except Exception as e:
                    logger.warning(f"Error getting stats for project {project.id}: {e}")
            
            # Process metrics
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            memory_percent = process.memory_percent()
            cpu_percent = process.cpu_percent()
            
            # Process uptime
            import time
            uptime_seconds = time.time() - process.create_time()
            if uptime_seconds < 60:
                uptime_text = f"{uptime_seconds:.0f}s"
            elif uptime_seconds < 3600:
                uptime_text = f"{uptime_seconds/60:.0f}m"
            else:
                uptime_text = f"{uptime_seconds/3600:.1f}h"
            
            # Storage size calculation (disk usage)
            data_dir = self.config.get("storage.data_dir", "data")
            if not Path(data_dir).is_absolute():
                project_root = Path(__file__).parent.parent.parent.parent
                data_path = project_root / data_dir
            else:
                data_path = Path(data_dir)
            
            storage_size = "0 MB"
            if data_path.exists():
                total_size = sum(f.stat().st_size for f in data_path.rglob("*") if f.is_file())
                size_mb = total_size / 1024 / 1024
                storage_size = f"{size_mb:.1f} MB" if size_mb >= 1 else f"{total_size / 1024:.1f} KB"
            
            # Update UI - Statistics cards
            self.stats_cards["projects"]["value"].configure(text=str(len(projects)))
            self.stats_cards["fragments"]["value"].configure(text=str(total_fragments))
            self.stats_cards["contexts"]["value"].configure(text=str(total_contexts))
            self.stats_cards["memory"]["value"].configure(text=f"{memory_mb:.1f} MB")
            
            # Update system info
            self.storage_size_label.configure(text=f"💾 Disk Storage: {storage_size}")
            self.api_usage_label.configure(text=f"🌐 API Calls (est.): ~{total_fragments} calls")
            
            # Update performance metrics
            self.cpu_usage_label.configure(text=f"🖥️ CPU Usage: {cpu_percent:.1f}%")
            self.memory_percent_label.configure(text=f"📊 Memory Usage: {memory_percent:.1f}%")
            self.uptime_label.configure(text=f"⏱️ Uptime: {uptime_text}")
            
            logger.info(f"Overview stats updated: {len(projects)} projects, {total_fragments} fragments")
            
        except Exception as e:
            logger.error(f"Error refreshing overview stats: {e}", exc_info=True)
    
    def grid(self, **kwargs):
        """Grid the overview frame."""
        if self.overview_frame:
            self.overview_frame.grid(**kwargs)
    
    def grid_remove(self):
        """Remove the overview frame from grid."""
        if self.overview_frame:
            self.overview_frame.grid_remove()
