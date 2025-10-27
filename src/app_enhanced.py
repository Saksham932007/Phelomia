"""
Enhanced Phelomia Application
AI-Powered Document Analysis & Conversion Platform with Modern UI
"""

import html
import os
import random
import re
import time
import logging
from pathlib import Path
from threading import Thread
from typing import Dict, List, Optional, Tuple, Any

import gradio as gr
import numpy as np
import torch
from docling_core.types.doc import DoclingDocument
from docling_core.types.doc.document import DocTagsDocument
from PIL import Image, ImageDraw, ImageOps
from transformers import (
    AutoProcessor,
    Idefics3ForConditionalGeneration,
    TextIteratorStreamer,
)

# Import our enhanced modules
from config import get_settings, create_directories, get_device
from analytics import analytics
from document_intelligence import analyze_document_type
from modern_ui import modern_ui
from batch_processing import batch_processor
from themes.carbon import theme as carbon_theme
from themes.research_monochrome import theme as mono_theme

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/phelomia.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get configuration
settings = get_settings()
create_directories()

# Setup paths
dir_ = Path(__file__).parent.parent
SAMPLES_PATH = dir_ / "data" / "images"

# Application metadata
TITLE = "Phelomia - AI Document Analysis Platform"
DESCRIPTION = """
<div style="text-align: center; margin: 20px 0;">
    <h2 style="color: #2c3e50; margin-bottom: 10px;">🚀 Welcome to Phelomia</h2>
    <p style="font-size: 18px; color: #34495e; margin-bottom: 15px;">
        Transform any document into structured data with cutting-edge AI technology
    </p>
    <p style="color: #7f8c8d;">
        Powered by IBM's Granite Docling model • Intelligent analysis • Real-time processing
    </p>
</div>
"""

# Enhanced sample data with metadata
sample_data = [
    {
        "preview_image": str(SAMPLES_PATH / "new_arxiv.png"),
        "prompts": [
            "Convert this page to docling.",
            "Does the document contain tables?",
            "Can you extract the 2nd section header?",
            "What element is located at <loc_84><loc_403><loc_238><loc_419>",
            "How can effective temperature be computed?",
            "Extract all picture elements on the page.",
        ],
        "image": str(SAMPLES_PATH / "new_arxiv.png"),
        "name": "📄 Academic Paper",
        "description": "Research paper with complex layout, equations, and references",
        "pad": False,
        "category": "document",
        "difficulty": "Advanced"
    },
    {
        "preview_image": str(SAMPLES_PATH / "image-2.jpg"),
        "prompts": ["Convert this table to OTSL.", "What is the Net income in 2008?"],
        "image": str(SAMPLES_PATH / "image-2.jpg"),
        "name": "📊 Financial Table",
        "description": "Structured financial data with numbers and calculations",
        "pad": True,
        "category": "table",
        "difficulty": "Intermediate"
    },
    {
        "preview_image": str(SAMPLES_PATH / "code.jpg"),
        "prompts": ["Convert code to text.", "What programming language is this?"],
        "image": str(SAMPLES_PATH / "code.jpg"),
        "name": "💻 Code Snippet",
        "description": "Programming code with syntax highlighting",
        "pad": True,
        "category": "code",
        "difficulty": "Easy"
    },
    {
        "preview_image": str(SAMPLES_PATH / "lake-zurich-switzerland-view-nature-landscapes-7bbda4-1024.jpg"),
        "prompts": ["Describe this image.", "What's the weather like?"],
        "image": str(SAMPLES_PATH / "lake-zurich-switzerland-view-nature-landscapes-7bbda4-1024.jpg"),
        "name": "🖼️ Natural Image",
        "description": "Beautiful landscape photo for image captioning",
        "pad": False,
        "category": "image",
        "difficulty": "Easy"
    },
    {
        "preview_image": str(SAMPLES_PATH / "87664.png"),
        "prompts": ["Convert formula to latex.", "Explain this mathematical expression."],
        "image": str(SAMPLES_PATH / "87664.png"),
        "name": "🧮 Mathematical Formula",
        "description": "Complex mathematical equations and formulas",
        "pad": True,
        "category": "formula",
        "difficulty": "Advanced"
    },
    {
        "preview_image": str(SAMPLES_PATH / "06236926002285.png"),
        "prompts": ["Convert chart to OTSL.", "What trends can you see?"],
        "image": str(SAMPLES_PATH / "06236926002285.png"),
        "name": "📈 Data Chart",
        "description": "Visual chart with data points and trends",
        "pad": False,
        "category": "chart",
        "difficulty": "Intermediate"
    },
    {
        "preview_image": str(SAMPLES_PATH / "ar_page_0.png"),
        "prompts": ["Convert this page to docling.", "What language is this?"],
        "image": str(SAMPLES_PATH / "ar_page_0.png"),
        "name": "🌍 Arabic Document",
        "description": "Arabic text document with RTL layout",
        "pad": False,
        "category": "document",
        "difficulty": "Advanced"
    },
    {
        "preview_image": str(SAMPLES_PATH / "japanse_4_ibm.png"),
        "prompts": ["Convert this page to docling.", "Translate to English."],
        "image": str(SAMPLES_PATH / "japanse_4_ibm.png"),
        "name": "🇯🇵 Japanese Document",
        "description": "Japanese document with complex characters",
        "pad": False,
        "category": "document",
        "difficulty": "Advanced"
    }
]

# Initialize device and model
device = get_device()
logger.info(f"Using device: {device}")

class PhelomiaApp:
    """Main Phelomia application class"""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.model_loaded = False
        self.current_theme = settings.theme
        
        # Initialize components
        self.analytics = analytics
        self.ui = modern_ui
        
        # Chat history for each session
        self.chat_histories = {}
        
        logger.info("Phelomia application initialized")
    
    def load_model(self):
        """Load the AI model with error handling"""
        try:
            if self.model_loaded:
                return True
                
            logger.info(f"Loading model: {settings.model_name}")
            
            # Load processor
            self.processor = AutoProcessor.from_pretrained(
                settings.model_name,
                trust_remote_code=True
            )
            
            # Load model
            self.model = Idefics3ForConditionalGeneration.from_pretrained(
                settings.model_name,
                torch_dtype=torch.bfloat16 if device != "cpu" else torch.float32,
                device_map=device if device != "cpu" else None,
                trust_remote_code=True
            )
            
            if device == "cpu":
                self.model = self.model.to(device)
            
            self.model_loaded = True
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def create_interface(self) -> gr.Blocks:
        """Create the main Gradio interface"""
        
        # Select theme based on configuration
        selected_theme = carbon_theme if self.current_theme == "carbon" else mono_theme
        
        with gr.Blocks(
            title=TITLE,
            theme=selected_theme,
            css=self.get_custom_css()
        ) as app:
            
            # Header
            gr.HTML(DESCRIPTION)
            
            # Main application tabs
            with gr.Tabs() as main_tabs:
                
                # Landing/Quick Start Tab
                with gr.Tab("🏠 Home", id="home") as home_tab:
                    upload_btn, gallery_btn, chat_btn = self.ui.create_landing_page()
                
                # Upload and Analysis Tab
                with gr.Tab("📁 Upload & Analyze", id="upload") as upload_tab:
                    upload_components = self.ui.create_upload_interface()
                    (file_input, process_btn, preview_image, detection_results, 
                     recommendations, auto_detect, advanced_mode, advanced_options,
                     max_length, batch_size, enable_padding, enhance_image, 
                     progress_html) = upload_components
                
                # Gallery Tab
                with gr.Tab("🖼️ Sample Gallery", id="gallery") as gallery_tab:
                    self.create_gallery_interface()
                
                # Chat Tab
                with gr.Tab("💬 Interactive Chat", id="chat") as chat_tab:
                    self.create_chat_interface()
                
                # Batch Processing Tab
                with gr.Tab("⚡ Batch Processing", id="batch") as batch_tab:
                    self.create_batch_interface()
                
                # Analytics Tab (Admin)
                with gr.Tab("📊 Analytics", id="analytics") as analytics_tab:
                    self.create_analytics_interface()
            
            # Global state management
            session_state = gr.State({
                "current_image": None,
                "last_analysis": None,
                "chat_history": [],
                "session_id": None
            })
            
            # Event handlers
            self.setup_event_handlers(
                upload_btn, gallery_btn, chat_btn, file_input, process_btn,
                main_tabs, session_state
            )
        
        return app
    
    def create_gallery_interface(self):
        """Create enhanced gallery interface"""
        
        gr.Markdown("### 🖼️ Sample Document Gallery")
        gr.Markdown("Explore our curated collection of sample documents to see Phelomia's capabilities.")
        
        # Filter controls
        with gr.Row():
            category_filter = gr.Dropdown(
                choices=["All", "document", "table", "code", "image", "formula", "chart"],
                value="All",
                label="📂 Category Filter"
            )
            
            difficulty_filter = gr.Dropdown(
                choices=["All", "Easy", "Intermediate", "Advanced"],
                value="All",
                label="🎯 Difficulty Level"
            )
        
        # Gallery display
        with gr.Row():
            gallery_items = []
            
            for i, sample in enumerate(sample_data):
                with gr.Column(scale=1):
                    with gr.Group():
                        # Sample image
                        sample_image = gr.Image(
                            value=sample["preview_image"],
                            label=sample["name"],
                            interactive=False,
                            height=200
                        )
                        
                        # Sample info
                        gr.Markdown(f"""
                        **{sample['name']}**
                        
                        {sample['description']}
                        
                        📂 *{sample['category'].title()}* • 🎯 *{sample['difficulty']}*
                        """)
                        
                        # Try button
                        try_btn = gr.Button(
                            f"Try {sample['name']}", 
                            variant="primary",
                            size="sm"
                        )
                        
                        gallery_items.append((sample_image, try_btn, sample))
        
        return gallery_items
    
    def create_chat_interface(self):
        """Create interactive chat interface"""
        
        gr.Markdown("### 💬 Chat with Your Documents")
        gr.Markdown("Upload a document and ask questions about its content using natural language.")
        
        with gr.Row():
            with gr.Column(scale=2):
                # Chat history
                chatbot = gr.Chatbot(
                    label="Document Chat",
                    height=400,
                    show_label=True
                )
                
                # Chat input
                with gr.Row():
                    chat_input = gr.Textbox(
                        placeholder="Ask a question about your document...",
                        label="Your Question",
                        scale=4
                    )
                    
                    send_btn = gr.Button("Send", variant="primary", scale=1)
                    clear_btn = gr.Button("Clear", variant="secondary", scale=1)
                
                # Quick suggestions
                with gr.Row():
                    gr.Markdown("**💡 Quick Suggestions:**")
                
                with gr.Row():
                    suggestion_btns = [
                        gr.Button("What's in this document?", size="sm"),
                        gr.Button("Extract all tables", size="sm"),
                        gr.Button("Summarize the content", size="sm"),
                        gr.Button("Find key points", size="sm")
                    ]
            
            with gr.Column(scale=1):
                # Current document
                chat_document = gr.Image(
                    label="Current Document",
                    height=300,
                    interactive=False
                )
                
                # Upload for chat
                chat_upload = gr.File(
                    label="Upload Document for Chat",
                    file_types=["image"]
                )
                
                # Chat statistics
                gr.HTML("""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px;">
                    <h5>📊 Chat Statistics</h5>
                    <p><strong>Questions Asked:</strong> <span id="questions-count">0</span></p>
                    <p><strong>Avg Response Time:</strong> <span id="avg-response-time">-</span></p>
                    <p><strong>Satisfaction:</strong> <span id="satisfaction-rating">-</span></p>
                </div>
                """)
        
        return chatbot, chat_input, send_btn, clear_btn, chat_document, chat_upload
    
    def create_batch_interface(self):
        """Create batch processing interface"""
        
        gr.Markdown("### ⚡ Batch Document Processing")
        gr.Markdown("Process multiple documents simultaneously with advanced job management.")
        
        with gr.Row():
            with gr.Column(scale=2):
                # File upload for batch
                batch_files = gr.File(
                    label="📁 Upload Multiple Documents",
                    file_count="multiple",
                    file_types=["image"]
                )
                
                # Analysis options
                batch_analysis = gr.CheckboxGroup(
                    choices=[
                        ("📊 Table Recognition", "table"),
                        ("🧮 Formula Conversion", "formula"),
                        ("💻 Code Recognition", "code"),
                        ("📈 Chart Analysis", "chart"),
                        ("📄 Document Conversion", "document")
                    ],
                    label="Analysis Types",
                    value=["document"]
                )
                
                # Custom prompt for batch
                batch_prompt = gr.Textbox(
                    label="Custom Prompt (Optional)",
                    placeholder="Custom analysis instructions...",
                    lines=3
                )
                
                # Start batch button
                start_batch_btn = gr.Button(
                    "🚀 Start Batch Processing",
                    variant="primary",
                    size="lg"
                )
            
            with gr.Column(scale=1):
                # Job status
                job_status = gr.HTML("""
                <div style="background: #e9ecef; padding: 15px; border-radius: 8px;">
                    <h5>📋 Job Status</h5>
                    <p>No active jobs</p>
                </div>
                """)
                
                # Progress bar
                progress_bar = gr.HTML("""
                <div style="margin: 15px 0;">
                    <div style="background: #e9ecef; height: 20px; border-radius: 10px;">
                        <div style="background: #007bff; height: 100%; width: 0%; border-radius: 10px; transition: width 0.5s;" id="batch-progress"></div>
                    </div>
                    <p style="text-align: center; margin: 5px 0;">0% Complete</p>
                </div>
                """)
                
                # Active jobs list
                active_jobs = gr.Dataframe(
                    headers=["Job ID", "Status", "Progress", "Files"],
                    datatype=["str", "str", "number", "number"],
                    label="Active Jobs",
                    interactive=False
                )
        
        # Results section
        with gr.Row():
            batch_results = gr.HTML("""
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px;">
                <h5>📊 Batch Results</h5>
                <p>Results will appear here after processing completes.</p>
            </div>
            """)
        
        return (batch_files, batch_analysis, batch_prompt, start_batch_btn,
                job_status, progress_bar, active_jobs, batch_results)
    
    def create_analytics_interface(self):
        """Create analytics and monitoring interface"""
        
        gr.Markdown("### 📊 System Analytics & Monitoring")
        
        # Real-time metrics
        with gr.Row():
            total_docs_metric = gr.Number(
                label="📄 Documents Processed",
                value=0,
                interactive=False
            )
            
            success_rate_metric = gr.Number(
                label="✅ Success Rate (%)",
                value=0,
                interactive=False
            )
            
            avg_time_metric = gr.Number(
                label="⏱️ Avg Processing Time (s)",
                value=0,
                interactive=False
            )
            
            uptime_metric = gr.Number(
                label="🚀 Uptime (hours)",
                value=0,
                interactive=False
            )
        
        # Charts and visualizations
        with gr.Row():
            with gr.Column():
                usage_plot = gr.Plot(label="📈 Daily Usage Trend")
            
            with gr.Column():
                feature_plot = gr.Plot(label="🔥 Feature Popularity")
        
        # System information
        with gr.Row():
            system_info = gr.HTML("""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                <h5>🖥️ System Information</h5>
                <p><strong>Device:</strong> Auto-detected</p>
                <p><strong>Model:</strong> Granite Docling 258M</p>
                <p><strong>Memory Usage:</strong> Monitoring...</p>
                <p><strong>GPU Utilization:</strong> N/A</p>
            </div>
            """)
        
        # Controls
        with gr.Row():
            refresh_analytics_btn = gr.Button(
                "🔄 Refresh Data",
                variant="primary"
            )
            
            export_report_btn = gr.Button(
                "📊 Export Report",
                variant="secondary"
            )
            
            clear_cache_btn = gr.Button(
                "🗑️ Clear Cache",
                variant="secondary"
            )
        
        analytics_status = gr.HTML()
        
        return (total_docs_metric, success_rate_metric, avg_time_metric, uptime_metric,
                usage_plot, feature_plot, system_info, refresh_analytics_btn,
                export_report_btn, clear_cache_btn, analytics_status)
    
    def setup_event_handlers(self, upload_btn, gallery_btn, chat_btn, 
                           file_input, process_btn, main_tabs, session_state):
        """Setup event handlers for the interface"""
        
        # Navigation handlers
        upload_btn.click(
            lambda: gr.update(selected="upload"),
            outputs=[main_tabs]
        )
        
        gallery_btn.click(
            lambda: gr.update(selected="gallery"),
            outputs=[main_tabs]
        )
        
        chat_btn.click(
            lambda: gr.update(selected="chat"),
            outputs=[main_tabs]
        )
        
        # File processing handler
        process_btn.click(
            self.process_document,
            inputs=[file_input, session_state],
            outputs=[session_state]
        )
    
    def process_document(self, file, session_state):
        """Process uploaded document"""
        if not file:
            return session_state
        
        try:
            # Load model if not already loaded
            if not self.load_model():
                raise Exception("Failed to load model")
            
            # Track processing start
            start_time = time.time()
            request_id = self.analytics.track_request_start("document_processing")
            
            # Analyze document type
            analysis = analyze_document_type(file)
            
            # Process with model (simplified for demo)
            # In real implementation, this would use the actual model
            result = {
                "analysis": analysis,
                "processed_at": time.time(),
                "file_path": file
            }
            
            # Track completion
            processing_time = time.time() - start_time
            self.analytics.track_document_processed(
                analysis['suggested_analysis'][0] if analysis['suggested_analysis'] else 'unknown',
                processing_time,
                True
            )
            
            # Update session state
            session_state["last_analysis"] = result
            session_state["current_image"] = file
            
            logger.info(f"Document processed successfully in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            self.analytics.track_document_processed("unknown", 0, False, str(e))
        
        return session_state
    
    def get_custom_css(self) -> str:
        """Get custom CSS for the interface"""
        return """
        /* Custom Phelomia Styles */
        .gradio-container {
            max-width: 1200px !important;
            margin: 0 auto;
        }
        
        .gr-button-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            transition: all 0.3s ease !important;
        }
        
        .gr-button-primary:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
        }
        
        .gr-button-secondary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
            border: none !important;
            color: white !important;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 20px 0;
        }
        
        .feature {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            color: white;
            font-weight: bold;
        }
        
        .progress-indicator {
            margin: 20px 0;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 12px;
            color: white;
            text-align: center;
            margin: 10px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .status-online { background-color: #28a745; }
        .status-processing { background-color: #ffc107; }
        .status-error { background-color: #dc3545; }
        """


def main():
    """Main application entry point"""
    logger.info("Starting Phelomia application...")
    
    try:
        # Create application instance
        app_instance = PhelomiaApp()
        
        # Create interface
        app = app_instance.create_interface()
        
        # Launch configuration
        launch_kwargs = {
            "server_name": "0.0.0.0",
            "server_port": int(os.getenv("PORT", 7860)),
            "share": False,
            "debug": settings.debug,
            "show_api": True,
            "allowed_paths": [str(SAMPLES_PATH)]
        }
        
        if settings.debug:
            launch_kwargs["reload"] = True
        
        logger.info(f"Launching Phelomia on port {launch_kwargs['server_port']}")
        logger.info(f"Visit: http://localhost:{launch_kwargs['server_port']}")
        
        # Launch the application
        app.launch(**launch_kwargs)
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise


if __name__ == "__main__":
    main()