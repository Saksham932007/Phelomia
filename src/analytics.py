"""
Performance Monitoring and Analytics System
Track usage, performance metrics, and provide insights for Phelomia
"""

import time
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """Track performance metrics and usage analytics"""
    
    def __init__(self, log_file: str = "logs/performance.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage for real-time metrics
        self.stats = defaultdict(int)
        self.processing_times = deque(maxlen=1000)  # Keep last 1000 processing times
        self.daily_stats = defaultdict(lambda: defaultdict(int))
        self.error_counts = defaultdict(int)
        self.user_feedback = []
        
        # Performance metrics
        self.start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Load existing data
        self._load_historical_data()
    
    def track_request_start(self, request_type: str, user_id: str = "anonymous") -> str:
        """Track the start of a request and return request ID"""
        request_id = f"{int(time.time() * 1000)}_{request_type}"
        
        with self.lock:
            self.total_requests += 1
            self.stats[f"requests_started_{request_type}"] += 1
            self.stats[f"daily_{datetime.now().strftime('%Y-%m-%d')}_{request_type}"] += 1
        
        return request_id
    
    def track_request_end(self, request_id: str, success: bool = True, 
                         execution_time: Optional[float] = None, 
                         error: Optional[str] = None):
        """Track the end of a request"""
        with self.lock:
            if success:
                self.successful_requests += 1
                self.stats["successful_requests"] += 1
            else:
                self.failed_requests += 1
                self.stats["failed_requests"] += 1
                if error:
                    self.error_counts[error] += 1
            
            if execution_time:
                self.processing_times.append(execution_time)
                self.stats["total_processing_time"] += execution_time
    
    def track_feature_usage(self, feature: str):
        """Track usage of specific features"""
        with self.lock:
            self.stats[f"feature_{feature}"] += 1
            today = datetime.now().strftime('%Y-%m-%d')
            self.daily_stats[today][feature] += 1
    
    def track_document_type(self, doc_type: str):
        """Track processed document types"""
        with self.lock:
            self.stats[f"document_type_{doc_type}"] += 1
    
    def track_user_feedback(self, rating: str, feedback_text: str, 
                           result_id: str = "", feature: str = ""):
        """Track user feedback"""
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "rating": rating,
            "feedback": feedback_text,
            "result_id": result_id,
            "feature": feature
        }
        
        with self.lock:
            self.user_feedback.append(feedback_entry)
            self.stats[f"feedback_{rating}"] += 1
        
        # Save feedback to file
        self._save_feedback(feedback_entry)
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get comprehensive dashboard metrics"""
        with self.lock:
            uptime_hours = (time.time() - self.start_time) / 3600
            
            # Calculate averages
            avg_processing_time = (
                sum(self.processing_times) / len(self.processing_times) 
                if self.processing_times else 0
            )
            
            success_rate = (
                (self.successful_requests / self.total_requests * 100) 
                if self.total_requests > 0 else 0
            )
            
            # Get most popular features
            feature_stats = {
                k.replace("feature_", ""): v 
                for k, v in self.stats.items() 
                if k.startswith("feature_")
            }
            
            most_popular_feature = (
                max(feature_stats.items(), key=lambda x: x[1])[0] 
                if feature_stats else "None"
            )
            
            # Get document type distribution
            doc_type_stats = {
                k.replace("document_type_", ""): v 
                for k, v in self.stats.items() 
                if k.startswith("document_type_")
            }
            
            return {
                "system_metrics": {
                    "uptime_hours": round(uptime_hours, 2),
                    "total_requests": self.total_requests,
                    "successful_requests": self.successful_requests,
                    "failed_requests": self.failed_requests,
                    "success_rate": round(success_rate, 2)
                },
                "performance_metrics": {
                    "average_processing_time": round(avg_processing_time, 3),
                    "total_processing_time": round(self.stats.get("total_processing_time", 0), 2),
                    "requests_per_hour": round(self.total_requests / max(uptime_hours, 1), 2)
                },
                "usage_metrics": {
                    "most_popular_feature": most_popular_feature,
                    "feature_usage": feature_stats,
                    "document_types": doc_type_stats
                },
                "feedback_metrics": {
                    "total_feedback": len(self.user_feedback),
                    "positive_feedback": self.stats.get("feedback_👍 Great", 0),
                    "neutral_feedback": self.stats.get("feedback_👌 Good", 0),
                    "negative_feedback": self.stats.get("feedback_👎 Needs work", 0)
                },
                "error_metrics": {
                    "error_distribution": dict(self.error_counts),
                    "total_errors": sum(self.error_counts.values())
                }
            }
    
    def get_daily_usage_trend(self, days: int = 7) -> Dict[str, List]:
        """Get daily usage trend for the last N days"""
        with self.lock:
            end_date = datetime.now()
            dates = []
            usage_data = []
            
            for i in range(days):
                date = (end_date - timedelta(days=i)).strftime('%Y-%m-%d')
                dates.append(date)
                
                daily_total = sum(self.daily_stats.get(date, {}).values())
                usage_data.append(daily_total)
            
            return {
                "dates": list(reversed(dates)),
                "usage": list(reversed(usage_data))
            }
    
    def get_feature_popularity_chart(self) -> Dict[str, Any]:
        """Get data for feature popularity chart"""
        with self.lock:
            feature_stats = {
                k.replace("feature_", ""): v 
                for k, v in self.stats.items() 
                if k.startswith("feature_")
            }
            
            # Sort by usage
            sorted_features = sorted(feature_stats.items(), key=lambda x: x[1], reverse=True)
            
            return {
                "labels": [item[0] for item in sorted_features],
                "values": [item[1] for item in sorted_features]
            }
    
    def export_analytics_report(self) -> str:
        """Export comprehensive analytics report"""
        metrics = self.get_dashboard_metrics()
        trend_data = self.get_daily_usage_trend(30)
        
        report = {
            "report_date": datetime.now().isoformat(),
            "summary": metrics,
            "trends": trend_data,
            "recent_feedback": self.user_feedback[-10:] if self.user_feedback else []
        }
        
        # Save to file
        report_file = self.log_file.parent / f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(report_file)
    
    def _load_historical_data(self):
        """Load historical performance data"""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load stats
                    self.stats.update(data.get("stats", {}))
                    self.daily_stats.update(data.get("daily_stats", {}))
                    self.error_counts.update(data.get("error_counts", {}))
                    
                    # Load processing times (limited to last 1000)
                    processing_times = data.get("processing_times", [])
                    self.processing_times.extend(processing_times[-1000:])
                    
                    # Load counters
                    self.total_requests = data.get("total_requests", 0)
                    self.successful_requests = data.get("successful_requests", 0)
                    self.failed_requests = data.get("failed_requests", 0)
                    
        except Exception as e:
            logger.error(f"Error loading historical data: {str(e)}")
    
    def _save_feedback(self, feedback_entry: Dict):
        """Save individual feedback entry"""
        try:
            feedback_file = self.log_file.parent / "user_feedback.jsonl"
            with open(feedback_file, 'a') as f:
                f.write(json.dumps(feedback_entry) + '\n')
        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
    
    def save_performance_data(self):
        """Save current performance data to file"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "stats": dict(self.stats),
                "daily_stats": dict(self.daily_stats),
                "error_counts": dict(self.error_counts),
                "processing_times": list(self.processing_times),
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests
            }
            
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving performance data: {str(e)}")


class UsageAnalytics:
    """High-level analytics interface"""
    
    def __init__(self):
        self.tracker = PerformanceTracker()
    
    def track_document_processed(self, doc_type: str, processing_time: float, 
                                success: bool = True, error: Optional[str] = None):
        """Track a document processing event"""
        request_id = self.tracker.track_request_start("document_processing")
        self.tracker.track_feature_usage("document_processing")
        self.tracker.track_document_type(doc_type)
        self.tracker.track_request_end(request_id, success, processing_time, error)
    
    def track_chat_interaction(self, processing_time: float, success: bool = True):
        """Track a chat interaction"""
        request_id = self.tracker.track_request_start("chat")
        self.tracker.track_feature_usage("chat")
        self.tracker.track_request_end(request_id, success, processing_time)
    
    def track_file_upload(self, file_size: int, file_type: str):
        """Track file upload event"""
        self.tracker.track_feature_usage("file_upload")
        self.tracker.stats[f"upload_size_total"] += file_size
        self.tracker.stats[f"upload_type_{file_type}"] += 1
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data"""
        return self.tracker.get_dashboard_metrics()
    
    def add_user_feedback(self, rating: str, feedback: str, feature: str = ""):
        """Add user feedback"""
        self.tracker.track_user_feedback(rating, feedback, "", feature)
    
    def generate_report(self) -> str:
        """Generate analytics report"""
        return self.tracker.export_analytics_report()


# Global analytics instance
analytics = UsageAnalytics()