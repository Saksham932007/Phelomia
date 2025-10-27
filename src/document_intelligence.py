"""
Document Type Detection System
AI-powered document analysis to automatically detect document types and suggest optimal processing
"""

import cv2
import numpy as np
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class DocumentTypeDetector:
    """Intelligent document type detection system"""
    
    def __init__(self):
        self.detection_patterns = {
            'table': {
                'keywords': ['table', 'row', 'column', 'cell', 'data'],
                'visual_features': ['grid_lines', 'structured_layout'],
                'confidence_threshold': 0.7
            },
            'formula': {
                'keywords': ['equation', 'formula', 'math', 'integral', 'sum'],
                'visual_features': ['mathematical_symbols', 'subscripts'],
                'confidence_threshold': 0.6
            },
            'code': {
                'keywords': ['function', 'class', 'import', 'def', 'var'],
                'visual_features': ['monospace_font', 'indentation'],
                'confidence_threshold': 0.8
            },
            'chart': {
                'keywords': ['chart', 'graph', 'plot', 'axis', 'legend'],
                'visual_features': ['axes', 'data_points', 'bars'],
                'confidence_threshold': 0.7
            },
            'document': {
                'keywords': ['paragraph', 'text', 'section', 'title'],
                'visual_features': ['text_blocks', 'headers'],
                'confidence_threshold': 0.5
            }
        }
    
    def analyze_document(self, image_path: str) -> Dict:
        """
        Analyze document and detect type with confidence scores
        
        Args:
            image_path: Path to the document image
            
        Returns:
            Dictionary with analysis results
        """
        try:
            image = Image.open(image_path).convert('RGB')
            
            # Perform various detection methods
            visual_analysis = self._analyze_visual_features(image)
            text_analysis = self._analyze_text_content(image)
            layout_analysis = self._analyze_layout(image)
            
            # Combine analyses
            confidence_scores = self._calculate_confidence_scores(
                visual_analysis, text_analysis, layout_analysis
            )
            
            # Generate suggestions and recommendations
            suggestions = self._generate_suggestions(confidence_scores)
            recommendations = self._generate_recommendations(confidence_scores, image_path)
            
            return {
                'suggested_analysis': suggestions,
                'confidence_scores': confidence_scores,
                'recommendations': recommendations,
                'auto_settings': self._get_optimal_settings(confidence_scores),
                'processing_hints': self._get_processing_hints(confidence_scores)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing document {image_path}: {str(e)}")
            return self._get_fallback_analysis()
    
    def _analyze_visual_features(self, image: Image.Image) -> Dict:
        """Analyze visual features of the image"""
        try:
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            features = {}
            
            # Detect lines (indicating tables or structured content)
            features['horizontal_lines'] = self._detect_horizontal_lines(gray)
            features['vertical_lines'] = self._detect_vertical_lines(gray)
            features['grid_structure'] = features['horizontal_lines'] * features['vertical_lines']
            
            # Detect text regions
            features['text_density'] = self._calculate_text_density(gray)
            features['white_space_ratio'] = self._calculate_whitespace_ratio(gray)
            
            # Detect mathematical symbols
            features['mathematical_symbols'] = self._detect_mathematical_symbols(gray)
            
            # Detect chart-like features
            features['chart_elements'] = self._detect_chart_elements(gray)
            
            return features
            
        except Exception as e:
            logger.error(f"Error in visual analysis: {str(e)}")
            return {}
    
    def _detect_horizontal_lines(self, gray_image: np.ndarray) -> float:
        """Detect horizontal lines in the image"""
        try:
            edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                horizontal_count = 0
                for rho, theta in lines[:, 0]:
                    # Check if line is roughly horizontal (theta close to 0 or pi)
                    if abs(theta) < 0.2 or abs(theta - np.pi) < 0.2:
                        horizontal_count += 1
                
                return min(horizontal_count / 10.0, 1.0)  # Normalize to 0-1
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _detect_vertical_lines(self, gray_image: np.ndarray) -> float:
        """Detect vertical lines in the image"""
        try:
            edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                vertical_count = 0
                for rho, theta in lines[:, 0]:
                    # Check if line is roughly vertical (theta close to pi/2)
                    if abs(theta - np.pi/2) < 0.2:
                        vertical_count += 1
                
                return min(vertical_count / 10.0, 1.0)  # Normalize to 0-1
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_text_density(self, gray_image: np.ndarray) -> float:
        """Calculate text density in the image"""
        try:
            # Use adaptive thresholding to find text regions
            binary = cv2.adaptiveThreshold(
                gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Count non-white pixels as potential text
            text_pixels = np.sum(binary == 0)
            total_pixels = binary.size
            
            return text_pixels / total_pixels
            
        except Exception:
            return 0.5  # Default moderate text density
    
    def _calculate_whitespace_ratio(self, gray_image: np.ndarray) -> float:
        """Calculate the ratio of whitespace in the image"""
        try:
            # Threshold to find white areas
            _, binary = cv2.threshold(gray_image, 240, 255, cv2.THRESH_BINARY)
            white_pixels = np.sum(binary == 255)
            total_pixels = binary.size
            
            return white_pixels / total_pixels
            
        except Exception:
            return 0.5
    
    def _detect_mathematical_symbols(self, gray_image: np.ndarray) -> float:
        """Detect mathematical symbols and formulas"""
        try:
            # Look for mathematical symbol patterns
            # This is a simplified approach - in production, you'd use more sophisticated methods
            
            # Detect complex shapes that might be mathematical symbols
            contours, _ = cv2.findContours(
                cv2.Canny(gray_image, 50, 150), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            complex_shapes = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    # Mathematical symbols often have complex shapes
                    if 0.1 < circularity < 0.7 and area > 50:
                        complex_shapes += 1
            
            return min(complex_shapes / 20.0, 1.0)
            
        except Exception:
            return 0.0
    
    def _detect_chart_elements(self, gray_image: np.ndarray) -> float:
        """Detect chart and graph elements"""
        try:
            # Look for chart-like patterns
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Detect circles (pie charts, data points)
            circles = cv2.HoughCircles(
                gray_image, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=5, maxRadius=50
            )
            
            circle_score = 0.0
            if circles is not None:
                circle_score = min(len(circles[0]) / 10.0, 1.0)
            
            # Detect rectangular regions (bars, legend boxes)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            rectangular_shapes = 0
            for contour in contours:
                approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
                if len(approx) == 4:  # Rectangle
                    rectangular_shapes += 1
            
            rect_score = min(rectangular_shapes / 20.0, 1.0)
            
            return (circle_score + rect_score) / 2
            
        except Exception:
            return 0.0
    
    def _analyze_text_content(self, image: Image.Image) -> Dict:
        """Analyze text content using OCR-like methods (simplified)"""
        # In a real implementation, you'd use OCR here
        # For now, return default values
        return {
            'code_keywords': 0.0,
            'math_keywords': 0.0,
            'table_keywords': 0.0,
            'chart_keywords': 0.0
        }
    
    def _analyze_layout(self, image: Image.Image) -> Dict:
        """Analyze document layout structure"""
        width, height = image.size
        aspect_ratio = width / height
        
        return {
            'aspect_ratio': aspect_ratio,
            'is_landscape': aspect_ratio > 1.2,
            'is_portrait': aspect_ratio < 0.8,
            'is_square': 0.8 <= aspect_ratio <= 1.2
        }
    
    def _calculate_confidence_scores(self, visual: Dict, text: Dict, layout: Dict) -> Dict:
        """Calculate confidence scores for each document type"""
        scores = {}
        
        # Table detection
        scores['table'] = (
            visual.get('grid_structure', 0) * 0.4 +
            text.get('table_keywords', 0) * 0.3 +
            (1 - visual.get('white_space_ratio', 0.5)) * 0.3
        )
        
        # Formula detection
        scores['formula'] = (
            visual.get('mathematical_symbols', 0) * 0.5 +
            text.get('math_keywords', 0) * 0.3 +
            visual.get('white_space_ratio', 0.5) * 0.2
        )
        
        # Code detection
        scores['code'] = (
            text.get('code_keywords', 0) * 0.4 +
            visual.get('text_density', 0.5) * 0.3 +
            (1 - visual.get('white_space_ratio', 0.5)) * 0.3
        )
        
        # Chart detection
        scores['chart'] = (
            visual.get('chart_elements', 0) * 0.5 +
            text.get('chart_keywords', 0) * 0.2 +
            layout.get('aspect_ratio', 1.0) * 0.3
        )
        
        # Document detection (default for text documents)
        scores['document'] = max(0.3, 1.0 - max(scores.values()))
        
        return scores
    
    def _generate_suggestions(self, scores: Dict) -> List[str]:
        """Generate processing suggestions based on confidence scores"""
        suggestions = []
        
        for doc_type, score in scores.items():
            threshold = self.detection_patterns[doc_type]['confidence_threshold']
            if score > threshold:
                suggestions.append(doc_type)
        
        # If no strong suggestions, default to document conversion
        if not suggestions:
            suggestions = ['document']
        
        return sorted(suggestions, key=lambda x: scores[x], reverse=True)
    
    def _generate_recommendations(self, scores: Dict, image_path: str) -> List[str]:
        """Generate user-friendly recommendations"""
        recommendations = []
        
        if scores.get('table', 0) > 0.7:
            recommendations.append("🔍 This looks like a table - try Table Recognition for best results!")
        
        if scores.get('formula', 0) > 0.6:
            recommendations.append("🧮 Mathematical content detected - use Formula Recognition to convert to LaTeX!")
        
        if scores.get('code', 0) > 0.8:
            recommendations.append("💻 Code snippet detected - try Code Recognition!")
        
        if scores.get('chart', 0) > 0.7:
            recommendations.append("📊 Chart or graph detected - use Chart Extraction!")
        
        if not recommendations:
            recommendations.append("📄 Try Document Conversion for general text extraction!")
        
        return recommendations
    
    def _get_optimal_settings(self, scores: Dict) -> Dict:
        """Get optimal processing settings based on document type"""
        top_type = max(scores.items(), key=lambda x: x[1])[0]
        
        settings = {
            'table': {'pad': True, 'enhance_contrast': True},
            'formula': {'pad': True, 'high_resolution': True},
            'code': {'pad': True, 'preserve_formatting': True},
            'chart': {'pad': False, 'color_analysis': True},
            'document': {'pad': False, 'text_enhancement': True}
        }
        
        return settings.get(top_type, {'pad': False})
    
    def _get_processing_hints(self, scores: Dict) -> List[str]:
        """Get processing hints for better results"""
        hints = []
        
        if scores.get('table', 0) > 0.5:
            hints.append("For tables: Ensure clear grid lines and good contrast")
        
        if scores.get('formula', 0) > 0.5:
            hints.append("For formulas: High resolution images work better")
        
        if scores.get('code', 0) > 0.5:
            hints.append("For code: Monospace fonts improve recognition")
        
        return hints
    
    def _get_fallback_analysis(self) -> Dict:
        """Return fallback analysis when detection fails"""
        return {
            'suggested_analysis': ['document'],
            'confidence_scores': {'document': 1.0},
            'recommendations': ["📄 Try Document Conversion for general text extraction!"],
            'auto_settings': {'pad': False},
            'processing_hints': ["Upload a clear, high-resolution image for best results"]
        }


# Global detector instance
document_detector = DocumentTypeDetector()


def analyze_document_type(image_path: str) -> Dict:
    """
    Convenience function to analyze document type
    
    Args:
        image_path: Path to the document image
        
    Returns:
        Analysis results dictionary
    """
    return document_detector.analyze_document(image_path)