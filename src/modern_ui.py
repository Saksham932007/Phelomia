"""
Modern UI Components for Phelomia
Enhanced user interface with progressive disclosure and modern design
"""

import gradio as gr
from typing import Dict, List, Optional, Tuple, Any
import json
from pathlib import Path

from .analytics import analytics
from .document_intelligence import analyze_document_type
from .config import get_settings

settings = get_settings()


class ModernUI:
    """Modern UI component builder for Phelomia"""
    
    def __init__(self):
        self.current_step = 1
        self.max_steps = 4
        
    def create_landing_page(self) -> gr.Blocks:
        """Create modern landing page with quick actions"""
        
        with gr.Row(equal_height=True):
            with gr.Column(scale=2):
                gr.Markdown("""
                # 🚀 Welcome to Phelomia!
                
                **AI-Powered Document Analysis & Conversion Platform**
                
                Transform any document into structured data with cutting-edge AI technology.
                Upload your document and let our intelligent system automatically detect the best processing method.
                
                ### ✨ What Can Phelomia Do?
                """)
                
                with gr.Row():
                    with gr.Column():
                        gr.HTML("""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    padding: 20px; border-radius: 12px; color: white; text-align: center; margin: 10px;">
                            <h3>📊 Tables</h3>
                            <p>Extract and convert tables to structured formats</p>
                        </div>
                        """)
                    
                    with gr.Column():
                        gr.HTML("""
                        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                                    padding: 20px; border-radius: 12px; color: white; text-align: center; margin: 10px;">
                            <h3>🧮 Formulas</h3>
                            <p>Convert mathematical formulas to LaTeX</p>
                        </div>
                        """)
                
                with gr.Row():
                    with gr.Column():
                        gr.HTML("""
                        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                                    padding: 20px; border-radius: 12px; color: white; text-align: center; margin: 10px;">
                            <h3>💻 Code</h3>
                            <p>Extract and recognize code snippets</p>
                        </div>
                        """)
                    
                    with gr.Column():
                        gr.HTML("""
                        <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                                    padding: 20px; border-radius: 12px; color: white; text-align: center; margin: 10px;">
                            <h3>📈 Charts</h3>
                            <p>Analyze charts and extract data</p>
                        </div>
                        """)
                
                # Quick action buttons
                with gr.Row():
                    upload_btn = gr.Button(
                        "📁 Upload Document", 
                        variant="primary", 
                        size="lg",
                        scale=2
                    )
                    gallery_btn = gr.Button(
                        "🖼️ Try Examples", 
                        variant="secondary", 
                        size="lg",
                        scale=1
                    )
                    chat_btn = gr.Button(
                        "💬 Chat Mode", 
                        variant="secondary", 
                        size="lg",
                        scale=1
                    )
            
            with gr.Column(scale=1):
                gr.HTML("""
                <div style="background: #f8f9fa; padding: 30px; border-radius: 15px; height: 100%;">
                    <h3 style="color: #495057; margin-bottom: 20px;">🎯 Quick Stats</h3>
                    <div style="margin-bottom: 15px;">
                        <strong>Documents Processed Today:</strong><br>
                        <span style="font-size: 24px; color: #28a745;">1,247</span>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <strong>Success Rate:</strong><br>
                        <span style="font-size: 24px; color: #007bff;">98.5%</span>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <strong>Avg Processing Time:</strong><br>
                        <span style="font-size: 24px; color: #6f42c1;">2.3s</span>
                    </div>
                    <hr style="margin: 20px 0;">
                    <div style="text-align: center;">
                        <p style="margin: 0; color: #6c757d;">Powered by IBM Granite AI</p>
                    </div>
                </div>
                """)
        
        return upload_btn, gallery_btn, chat_btn
    
    def create_upload_interface(self) -> Tuple[gr.components.Component, ...]:
        """Create enhanced upload interface with auto-detection"""
        
        with gr.Row():
            with gr.Column(scale=2):
                # Progress indicator
                progress_html = gr.HTML("""
                <div style="margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-weight: bold; color: #007bff;">Step 1: Upload Document</span>
                        <span style="color: #6c757d;">1 of 4</span>
                    </div>
                    <div style="background: #e9ecef; height: 8px; border-radius: 4px;">
                        <div style="background: linear-gradient(90deg, #007bff, #0056b3); height: 100%; width: 25%; border-radius: 4px; transition: width 0.3s;"></div>
                    </div>
                </div>
                """)
                
                # Enhanced file upload
                file_input = gr.File(
                    label="📁 Drop your document here or click to browse",
                    file_types=["image"],
                    height=200,
                    interactive=True
                )
                
                # Auto-detection toggle
                with gr.Row():
                    auto_detect = gr.Checkbox(
                        label="🤖 Enable automatic document type detection", 
                        value=True,
                        info="Our AI will analyze your document and suggest the best processing method"
                    )
                    
                    advanced_mode = gr.Checkbox(
                        label="⚙️ Advanced options", 
                        value=False,
                        info="Show expert configuration options"
                    )
                
                # Advanced options (initially hidden)
                with gr.Column(visible=False) as advanced_options:
                    gr.Markdown("### 🔧 Advanced Configuration")
                    
                    with gr.Row():
                        max_length = gr.Slider(
                            minimum=256,
                            maximum=2048,
                            value=settings.max_length,
                            label="Max Processing Length",
                            info="Higher values for detailed analysis"
                        )
                        
                        batch_size = gr.Slider(
                            minimum=1,
                            maximum=8,
                            value=settings.batch_size,
                            step=1,
                            label="Batch Size",
                            info="Process multiple elements simultaneously"
                        )
                    
                    with gr.Row():
                        enable_padding = gr.Checkbox(
                            label="📐 Enable image padding",
                            value=True,
                            info="Add padding for better recognition"
                        )
                        
                        enhance_image = gr.Checkbox(
                            label="✨ Enhance image quality",
                            value=True,
                            info="Apply preprocessing for better results"
                        )
                
                # Process button
                process_btn = gr.Button(
                    "🔍 Analyze Document", 
                    variant="primary", 
                    size="lg",
                    interactive=False
                )
            
            with gr.Column(scale=1):
                # Preview and detection results
                preview_image = gr.Image(
                    label="📷 Preview", 
                    interactive=False,
                    height=300
                )
                
                # Auto-detection results
                detection_results = gr.HTML(visible=False)
                
                # Recommendations
                recommendations = gr.Markdown(visible=False)
        
        # Toggle advanced options visibility
        def toggle_advanced(show_advanced):
            return gr.update(visible=show_advanced)
        
        advanced_mode.change(
            toggle_advanced,
            inputs=[advanced_mode],
            outputs=[advanced_options]
        )
        
        # Auto-detection when file is uploaded
        def handle_file_upload(file, auto_detect_enabled):
            if file is None:
                return (
                    None,  # preview
                    gr.update(interactive=False),  # process button
                    gr.update(visible=False),  # detection results
                    gr.update(visible=False)   # recommendations
                )
            
            # Show preview
            preview = file
            
            if auto_detect_enabled:
                try:
                    # Analyze document type
                    analysis = analyze_document_type(file)
                    
                    # Create detection results HTML
                    confidence_html = "<h4>🎯 Detection Results</h4>"
                    for doc_type, confidence in analysis['confidence_scores'].items():
                        percentage = confidence * 100
                        color = "#28a745" if percentage > 70 else "#ffc107" if percentage > 40 else "#dc3545"
                        confidence_html += f"""
                        <div style="margin: 5px 0;">
                            <span style="font-weight: bold;">{doc_type.title()}:</span>
                            <div style="background: #e9ecef; height: 20px; border-radius: 10px; margin: 2px 0;">
                                <div style="background: {color}; height: 100%; width: {percentage}%; border-radius: 10px; line-height: 20px; text-align: center; color: white; font-size: 12px;">
                                    {percentage:.1f}%
                                </div>
                            </div>
                        </div>
                        """
                    
                    # Create recommendations
                    rec_text = "### 💡 Recommendations\n"
                    for rec in analysis['recommendations']:
                        rec_text += f"- {rec}\n"
                    
                    # Track file upload
                    analytics.track_file_upload(0, "image")  # Size would be calculated in real implementation
                    
                    return (
                        preview,
                        gr.update(interactive=True),
                        gr.update(value=confidence_html, visible=True),
                        gr.update(value=rec_text, visible=True)
                    )
                    
                except Exception as e:
                    return (
                        preview,
                        gr.update(interactive=True),
                        gr.update(value=f"<div style='color: red;'>Error during analysis: {str(e)}</div>", visible=True),
                        gr.update(visible=False)
                    )
            else:
                return (
                    preview,
                    gr.update(interactive=True),
                    gr.update(visible=False),
                    gr.update(visible=False)
                )
        
        file_input.change(
            handle_file_upload,
            inputs=[file_input, auto_detect],
            outputs=[preview_image, process_btn, detection_results, recommendations]
        )
        
        return (
            file_input, process_btn, preview_image, detection_results, 
            recommendations, auto_detect, advanced_mode, advanced_options,
            max_length, batch_size, enable_padding, enhance_image, progress_html
        )
    
    def create_analysis_selector(self) -> Tuple[gr.components.Component, ...]:
        """Create analysis type selector with smart suggestions"""
        
        progress_html = gr.HTML("""
        <div style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span style="font-weight: bold; color: #007bff;">Step 2: Choose Analysis Type</span>
                <span style="color: #6c757d;">2 of 4</span>
            </div>
            <div style="background: #e9ecef; height: 8px; border-radius: 4px;">
                <div style="background: linear-gradient(90deg, #007bff, #0056b3); height: 100%; width: 50%; border-radius: 4px; transition: width 0.3s;"></div>
            </div>
        </div>
        """)
        
        gr.Markdown("### 🎯 What would you like to extract from your document?")
        
        with gr.Row():
            with gr.Column():
                analysis_options = gr.CheckboxGroup(
                    choices=[
                        ("📊 Extract Tables", "table"),
                        ("🧮 Convert Formulas to LaTeX", "formula"), 
                        ("💻 Extract Code", "code"),
                        ("📈 Analyze Charts", "chart"),
                        ("📄 Convert to Docling Format", "document"),
                        ("💬 Enable Interactive Chat", "chat")
                    ],
                    label="Select Analysis Types",
                    value=["table"],
                    info="You can select multiple analysis types to run in parallel"
                )
                
                # Custom prompt option
                with gr.Accordion("✏️ Custom Analysis", open=False):
                    custom_prompt = gr.Textbox(
                        label="Custom Prompt",
                        placeholder="Enter your custom analysis request...",
                        lines=3,
                        info="Describe exactly what you want to extract or analyze"
                    )
            
            with gr.Column():
                # Smart suggestions based on detection
                suggested_analysis = gr.HTML("""
                <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 4px solid #2196f3;">
                    <h4 style="margin-top: 0; color: #1976d2;">🤖 AI Suggestions</h4>
                    <p style="margin: 0; color: #424242;">Upload a document first to see intelligent recommendations</p>
                </div>
                """)
                
                # Analysis preview
                analysis_preview = gr.HTML("""
                <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin-top: 15px;">
                    <h5 style="margin-top: 0;">📋 Selected Analysis Preview</h5>
                    <p style="margin: 0; color: #666;">Your analysis configuration will appear here</p>
                </div>
                """)
        
        # Process configuration button
        configure_btn = gr.Button(
            "⚙️ Configure Processing", 
            variant="primary", 
            size="lg"
        )
        
        # Update preview when selections change
        def update_analysis_preview(selected_options, custom_text):
            if not selected_options and not custom_text:
                return """
                <div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">
                    <h5 style="margin-top: 0;">📋 Selected Analysis Preview</h5>
                    <p style="margin: 0; color: #666;">No analysis types selected</p>
                </div>
                """
            
            preview_html = """
            <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50;">
                <h5 style="margin-top: 0; color: #2e7d32;">📋 Analysis Configuration</h5>
            """
            
            if selected_options:
                preview_html += "<strong>Selected analyses:</strong><ul>"
                for option in selected_options:
                    option_names = {
                        "table": "📊 Table Recognition",
                        "formula": "🧮 Formula to LaTeX Conversion",
                        "code": "💻 Code Recognition",
                        "chart": "📈 Chart Analysis", 
                        "document": "📄 Document Conversion",
                        "chat": "💬 Interactive Chat Mode"
                    }
                    preview_html += f"<li>{option_names.get(option, option)}</li>"
                preview_html += "</ul>"
            
            if custom_text:
                preview_html += f"<strong>Custom analysis:</strong><br><em>{custom_text}</em><br>"
            
            preview_html += "</div>"
            return preview_html
        
        analysis_options.change(
            update_analysis_preview,
            inputs=[analysis_options, custom_prompt],
            outputs=[analysis_preview]
        )
        
        custom_prompt.change(
            update_analysis_preview,
            inputs=[analysis_options, custom_prompt],
            outputs=[analysis_preview]
        )
        
        return (
            progress_html, analysis_options, custom_prompt, 
            suggested_analysis, analysis_preview, configure_btn
        )
    
    def create_results_interface(self) -> Tuple[gr.components.Component, ...]:
        """Create comprehensive results interface"""
        
        progress_html = gr.HTML("""
        <div style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span style="font-weight: bold; color: #28a745;">Step 4: Results</span>
                <span style="color: #6c757d;">4 of 4</span>
            </div>
            <div style="background: #e9ecef; height: 8px; border-radius: 4px;">
                <div style="background: linear-gradient(90deg, #28a745, #20c997); height: 100%; width: 100%; border-radius: 4px; transition: width 0.3s;"></div>
            </div>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # Results tabs
                with gr.Tabs():
                    with gr.Tab("📊 Analysis Results") as results_tab:
                        results_display = gr.HTML()
                        
                        # Bounding box visualization
                        annotated_image = gr.Image(
                            label="📍 Annotated Document", 
                            interactive=False
                        )
                    
                    with gr.Tab("💬 Interactive Chat") as chat_tab:
                        chatbot = gr.Chatbot(
                            label="Chat with your document",
                            height=400
                        )
                        
                        chat_input = gr.Textbox(
                            label="Ask questions about your document",
                            placeholder="e.g., What is the total in the table?",
                            interactive=True
                        )
                        
                        chat_submit = gr.Button("Send", variant="primary")
                    
                    with gr.Tab("📈 Performance") as performance_tab:
                        performance_metrics = gr.HTML()
                
                # Action buttons
                with gr.Row():
                    export_btn = gr.Button("📥 Export Results", variant="secondary")
                    share_btn = gr.Button("🔗 Share", variant="secondary")
                    improve_btn = gr.Button("✨ Improve Results", variant="secondary")
                    new_analysis_btn = gr.Button("🔄 New Analysis", variant="primary")
            
            with gr.Column(scale=1):
                # Processing status
                processing_status = gr.HTML("""
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <h5 style="margin-top: 0; color: #856404;">⏳ Processing Status</h5>
                    <p style="margin: 0;">Ready to process your document</p>
                </div>
                """)
                
                # Quality metrics
                quality_metrics = gr.HTML("""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px;">
                    <h5 style="margin-top: 0;">📊 Quality Metrics</h5>
                    <div style="margin: 10px 0;">
                        <strong>Confidence Score:</strong><br>
                        <div style="background: #e9ecef; height: 20px; border-radius: 10px; margin: 5px 0;">
                            <div style="background: #28a745; height: 100%; width: 0%; border-radius: 10px; transition: width 0.5s;" id="confidence-bar"></div>
                        </div>
                    </div>
                    <div style="margin: 10px 0;">
                        <strong>Processing Time:</strong> <span id="processing-time">-</span><br>
                        <strong>Elements Detected:</strong> <span id="elements-count">-</span><br>
                        <strong>Accuracy:</strong> <span id="accuracy-score">-</span>
                    </div>
                </div>
                """)
                
                # Feedback section
                feedback_section = self.create_feedback_interface()
        
        return (
            progress_html, results_display, annotated_image, chatbot, 
            chat_input, chat_submit, performance_metrics, processing_status,
            quality_metrics, export_btn, share_btn, improve_btn, 
            new_analysis_btn, feedback_section
        )
    
    def create_feedback_interface(self) -> gr.components.Component:
        """Create user feedback interface"""
        
        with gr.Accordion("💬 Feedback", open=False):
            gr.Markdown("### Help us improve Phelomia!")
            
            with gr.Row():
                rating = gr.Radio(
                    choices=["👍 Great", "👌 Good", "👎 Needs work"],
                    label="How was your experience?",
                    value=None
                )
            
            feedback_text = gr.Textbox(
                label="Tell us more (optional)",
                placeholder="What worked well? What could be improved?",
                lines=3
            )
            
            submit_feedback = gr.Button("Send Feedback", variant="secondary")
            
            feedback_status = gr.HTML(visible=False)
            
            def handle_feedback(rating_value, feedback_content):
                if rating_value:
                    # Track feedback
                    analytics.add_user_feedback(rating_value, feedback_content)
                    
                    return gr.update(
                        value="<div style='color: green; padding: 10px; background: #d4edda; border-radius: 5px;'>✅ Thank you for your feedback!</div>",
                        visible=True
                    )
                else:
                    return gr.update(
                        value="<div style='color: red; padding: 10px; background: #f8d7da; border-radius: 5px;'>Please select a rating first.</div>",
                        visible=True
                    )
            
            submit_feedback.click(
                handle_feedback,
                inputs=[rating, feedback_text],
                outputs=[feedback_status]
            )
        
        return submit_feedback
    
    def create_admin_dashboard(self) -> gr.Blocks:
        """Create admin dashboard for analytics"""
        
        with gr.Blocks(title="Phelomia Admin Dashboard") as dashboard:
            gr.Markdown("# 📊 Phelomia Analytics Dashboard")
            
            # Real-time metrics
            with gr.Row():
                total_docs = gr.Number(label="📄 Total Documents", interactive=False)
                success_rate = gr.Number(label="✅ Success Rate (%)", interactive=False)
                avg_time = gr.Number(label="⏱️ Avg Processing Time (s)", interactive=False)
                uptime = gr.Number(label="🚀 Uptime (hours)", interactive=False)
            
            # Charts
            with gr.Row():
                with gr.Column():
                    usage_chart = gr.Plot(label="📈 Daily Usage Trend")
                
                with gr.Column():
                    feature_chart = gr.Plot(label="🔥 Feature Popularity")
            
            # Controls
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh Data", variant="primary")
                export_report_btn = gr.Button("📊 Export Report", variant="secondary")
                
            report_status = gr.HTML()
            
            def update_dashboard():
                metrics = analytics.get_dashboard_data()
                
                system_metrics = metrics["system_metrics"]
                performance_metrics = metrics["performance_metrics"]
                
                return (
                    system_metrics["total_requests"],
                    system_metrics["success_rate"],
                    performance_metrics["average_processing_time"],
                    system_metrics["uptime_hours"]
                )
            
            def export_report():
                try:
                    report_path = analytics.generate_report()
                    return f"<div style='color: green;'>Report exported to: {report_path}</div>"
                except Exception as e:
                    return f"<div style='color: red;'>Error exporting report: {str(e)}</div>"
            
            refresh_btn.click(
                update_dashboard,
                outputs=[total_docs, success_rate, avg_time, uptime]
            )
            
            export_report_btn.click(
                export_report,
                outputs=[report_status]
            )
        
        return dashboard


# Global UI instance
modern_ui = ModernUI()