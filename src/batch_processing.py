"""
Batch Processing System for Phelomia
Handle multiple documents and background processing
"""

import asyncio
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from dataclasses import dataclass, asdict
from enum import Enum

from .analytics import analytics

logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchJob:
    """Batch processing job data structure"""
    job_id: str
    file_paths: List[str]
    analysis_types: List[str]
    custom_prompt: Optional[str] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    progress: float = 0.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    results: List[Dict] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.results is None:
            self.results = []
        if self.errors is None:
            self.errors = []


class BatchProcessor:
    """Batch processing system for handling multiple documents"""
    
    def __init__(self, max_concurrent_jobs: int = 3, max_workers: int = 4):
        self.max_concurrent = max_concurrent_jobs
        self.max_workers = max_workers
        self.active_jobs: Dict[str, BatchJob] = {}
        self.job_history: List[BatchJob] = []
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Processing callbacks
        self.progress_callbacks: Dict[str, Callable] = {}
        self.completion_callbacks: Dict[str, Callable] = {}
        
        # Results storage
        self.results_dir = Path("results/batch_processing")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    async def submit_batch_job(
        self, 
        file_paths: List[str], 
        analysis_types: List[str],
        custom_prompt: Optional[str] = None,
        priority: int = 1
    ) -> str:
        """
        Submit a batch processing job
        
        Args:
            file_paths: List of file paths to process
            analysis_types: Types of analysis to perform
            custom_prompt: Optional custom prompt
            priority: Job priority (higher = more important)
            
        Returns:
            Job ID for tracking
        """
        job_id = f"batch_{int(time.time() * 1000)}"
        
        # Create batch job
        job = BatchJob(
            job_id=job_id,
            file_paths=file_paths,
            analysis_types=analysis_types,
            custom_prompt=custom_prompt
        )
        
        # Add to active jobs
        self.active_jobs[job_id] = job
        
        # Start processing
        asyncio.create_task(self._process_batch_job(job))
        
        logger.info(f"Submitted batch job {job_id} with {len(file_paths)} files")
        analytics.track_feature_usage("batch_processing")
        
        return job_id
    
    async def _process_batch_job(self, job: BatchJob):
        """Process a batch job asynchronously"""
        try:
            job.status = ProcessingStatus.PROCESSING
            job.start_time = time.time()
            
            logger.info(f"Starting batch job {job.job_id}")
            
            # Process files with progress tracking
            await self._process_files_with_progress(job)
            
            # Job completed successfully
            job.status = ProcessingStatus.COMPLETED
            job.end_time = time.time()
            job.progress = 100.0
            
            # Save results
            await self._save_job_results(job)
            
            # Move to history
            self.job_history.append(job)
            del self.active_jobs[job.job_id]
            
            # Trigger completion callback
            if job.job_id in self.completion_callbacks:
                self.completion_callbacks[job.job_id](job)
            
            processing_time = job.end_time - job.start_time
            analytics.track_document_processed("batch", processing_time, True)
            
            logger.info(f"Completed batch job {job.job_id} in {processing_time:.2f}s")
            
        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.end_time = time.time()
            job.errors.append(str(e))
            
            logger.error(f"Batch job {job.job_id} failed: {str(e)}")
            analytics.track_document_processed("batch", 0, False, str(e))
            
            # Move to history even if failed
            self.job_history.append(job)
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
    
    async def _process_files_with_progress(self, job: BatchJob):
        """Process files with progress tracking"""
        total_files = len(job.file_paths)
        completed_files = 0
        
        # Process files in batches to manage memory
        batch_size = min(self.max_workers, 4)
        
        for i in range(0, total_files, batch_size):
            batch_files = job.file_paths[i:i + batch_size]
            
            # Submit batch to thread pool
            futures = []
            for file_path in batch_files:
                future = self.executor.submit(
                    self._process_single_file,
                    file_path,
                    job.analysis_types,
                    job.custom_prompt
                )
                futures.append((future, file_path))
            
            # Wait for completion and collect results
            for future, file_path in futures:
                try:
                    result = future.result(timeout=300)  # 5 minute timeout per file
                    job.results.append({
                        "file_path": file_path,
                        "result": result,
                        "status": "success"
                    })
                    
                except Exception as e:
                    job.errors.append(f"Error processing {file_path}: {str(e)}")
                    job.results.append({
                        "file_path": file_path,
                        "error": str(e),
                        "status": "error"
                    })
                
                completed_files += 1
                job.progress = (completed_files / total_files) * 100
                
                # Trigger progress callback
                if job.job_id in self.progress_callbacks:
                    self.progress_callbacks[job.job_id](job.progress, completed_files, total_files)
    
    def _process_single_file(
        self, 
        file_path: str, 
        analysis_types: List[str], 
        custom_prompt: Optional[str]
    ) -> Dict:
        """
        Process a single file (to be implemented with actual model)
        This is a placeholder for the actual processing logic
        """
        try:
            # Simulate processing time
            time.sleep(2)  # In real implementation, this would be model inference
            
            # Placeholder result
            result = {
                "file_path": file_path,
                "analysis_types": analysis_types,
                "extracted_text": f"Extracted content from {Path(file_path).name}",
                "confidence": 0.95,
                "processing_time": 2.0,
                "metadata": {
                    "file_size": Path(file_path).stat().st_size if Path(file_path).exists() else 0,
                    "timestamp": time.time()
                }
            }
            
            if custom_prompt:
                result["custom_analysis"] = f"Custom analysis for: {custom_prompt}"
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            raise
    
    async def _save_job_results(self, job: BatchJob):
        """Save job results to disk"""
        try:
            results_file = self.results_dir / f"job_{job.job_id}.json"
            
            # Prepare serializable job data
            job_data = {
                "job_id": job.job_id,
                "file_paths": job.file_paths,
                "analysis_types": job.analysis_types,
                "custom_prompt": job.custom_prompt,
                "status": job.status.value,
                "progress": job.progress,
                "start_time": job.start_time,
                "end_time": job.end_time,
                "processing_time": job.end_time - job.start_time if job.end_time and job.start_time else None,
                "results": job.results,
                "errors": job.errors,
                "summary": {
                    "total_files": len(job.file_paths),
                    "successful_files": len([r for r in job.results if r.get("status") == "success"]),
                    "failed_files": len([r for r in job.results if r.get("status") == "error"]),
                    "total_errors": len(job.errors)
                }
            }
            
            with open(results_file, 'w') as f:
                json.dump(job_data, f, indent=2)
            
            logger.info(f"Saved results for job {job.job_id} to {results_file}")
            
        except Exception as e:
            logger.error(f"Error saving results for job {job.job_id}: {str(e)}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get current status of a job"""
        # Check active jobs
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            return {
                "job_id": job.job_id,
                "status": job.status.value,
                "progress": job.progress,
                "files_total": len(job.file_paths),
                "files_completed": len(job.results),
                "errors": len(job.errors),
                "start_time": job.start_time,
                "estimated_completion": self._estimate_completion_time(job)
            }
        
        # Check job history
        for job in self.job_history:
            if job.job_id == job_id:
                return {
                    "job_id": job.job_id,
                    "status": job.status.value,
                    "progress": job.progress,
                    "files_total": len(job.file_paths),
                    "files_completed": len(job.results),
                    "errors": len(job.errors),
                    "start_time": job.start_time,
                    "end_time": job.end_time,
                    "processing_time": job.end_time - job.start_time if job.end_time and job.start_time else None
                }
        
        return None
    
    def _estimate_completion_time(self, job: BatchJob) -> Optional[float]:
        """Estimate job completion time based on progress"""
        if job.progress == 0 or not job.start_time:
            return None
        
        elapsed_time = time.time() - job.start_time
        estimated_total_time = elapsed_time / (job.progress / 100)
        estimated_remaining = estimated_total_time - elapsed_time
        
        return max(0, estimated_remaining)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel an active job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = ProcessingStatus.CANCELLED
            job.end_time = time.time()
            
            # Move to history
            self.job_history.append(job)
            del self.active_jobs[job_id]
            
            logger.info(f"Cancelled job {job_id}")
            return True
        
        return False
    
    def get_active_jobs(self) -> List[Dict]:
        """Get list of active jobs"""
        return [
            {
                "job_id": job.job_id,
                "status": job.status.value,
                "progress": job.progress,
                "files_total": len(job.file_paths),
                "start_time": job.start_time
            }
            for job in self.active_jobs.values()
        ]
    
    def get_job_history(self, limit: int = 50) -> List[Dict]:
        """Get job history"""
        return [
            {
                "job_id": job.job_id,
                "status": job.status.value,
                "files_total": len(job.file_paths),
                "start_time": job.start_time,
                "end_time": job.end_time,
                "processing_time": job.end_time - job.start_time if job.end_time and job.start_time else None
            }
            for job in self.job_history[-limit:]
        ]
    
    def register_progress_callback(self, job_id: str, callback: Callable):
        """Register progress callback for a job"""
        self.progress_callbacks[job_id] = callback
    
    def register_completion_callback(self, job_id: str, callback: Callable):
        """Register completion callback for a job"""
        self.completion_callbacks[job_id] = callback
    
    def cleanup_old_jobs(self, days_old: int = 30):
        """Cleanup old job data"""
        cutoff_time = time.time() - (days_old * 24 * 3600)
        
        # Clean job history
        self.job_history = [
            job for job in self.job_history 
            if job.end_time and job.end_time > cutoff_time
        ]
        
        # Clean result files
        for result_file in self.results_dir.glob("job_*.json"):
            if result_file.stat().st_mtime < cutoff_time:
                result_file.unlink()
                logger.info(f"Cleaned up old result file: {result_file}")


# Global batch processor instance
batch_processor = BatchProcessor()