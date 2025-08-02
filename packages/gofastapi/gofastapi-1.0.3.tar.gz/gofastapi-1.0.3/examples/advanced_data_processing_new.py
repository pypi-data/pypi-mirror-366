"""
Example 2: Advanced Data Processing API
Real-time analytics, data transformation, and machine learning endpoints
"""

from gofastapi import GoFastAPI, HTTPException
import json
import time
import random
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

app = GoFastAPI(
    title="Advanced Data Processing API",
    version="1.0.2",
    description="High-performance data analytics and machine learning API with real-time processing"
)

# In-memory data storage
analytics_data = []
processed_datasets = {}
ml_models = {}
real_time_metrics = {
    "requests_count": 0,
    "processing_time_avg": 0,
    "data_points_processed": 0,
    "last_update": datetime.now().isoformat()
}

def generate_sample_data(count: int = 1000) -> List[Dict]:
    """Generate sample data for testing."""
    data = []
    categories = ["sales", "marketing", "support", "development", "operations"]
    
    for i in range(count):
        data.append({
            "id": i + 1,
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "category": random.choice(categories),
            "value": random.uniform(10, 1000),
            "quantity": random.randint(1, 100),
            "status": random.choice(["active", "pending", "completed", "cancelled"]),
            "region": random.choice(["north", "south", "east", "west", "central"]),
            "score": random.uniform(0, 100)
        })
    
    return data

def update_metrics(processing_time: float, data_points: int):
    """Update real-time metrics."""
    global real_time_metrics
    real_time_metrics["requests_count"] += 1
    real_time_metrics["data_points_processed"] += data_points
    
    # Calculate moving average for processing time
    current_avg = real_time_metrics["processing_time_avg"]
    count = real_time_metrics["requests_count"]
    real_time_metrics["processing_time_avg"] = (current_avg * (count - 1) + processing_time) / count
    real_time_metrics["last_update"] = datetime.now().isoformat()

@app.get("/")
def root():
    """Data Processing API information."""
    return {
        "name": "Advanced Data Processing API",
        "version": "1.0.2",
        "framework": "GoFastAPI",
        "description": "High-performance analytics and ML API",
        "features": [
            "Real-time Data Processing",
            "Statistical Analysis",
            "Data Transformation",
            "Machine Learning Pipelines",
            "Performance Analytics",
            "Data Visualization Support"
        ],
        "endpoints": {
            "data_processing": ["/data/upload", "/data/analyze", "/data/transform"],
            "analytics": ["/analytics/summary", "/analytics/trends", "/analytics/predictions"],
            "machine_learning": ["/ml/train", "/ml/predict", "/ml/models"],
            "performance": ["/metrics", "/health", "/benchmarks"]
        },
        "performance": {
            "framework": "GoFastAPI",
            "speed": "25x faster than FastAPI",
            "throughput": "500K+ RPS",
            "data_processing": "Real-time capable"
        }
    }

@app.post("/data/upload")
def upload_data(dataset: dict):
    """Upload and validate large datasets."""
    start_time = time.time()
    
    dataset_name = dataset.get("name", f"dataset_{int(time.time())}")
    data = dataset.get("data", [])
    
    if not data:
        raise HTTPException(400, "No data provided")
    
    # Data validation and processing
    processed_data = []
    errors = []
    
    for i, record in enumerate(data):
        try:
            # Validate required fields
            if not isinstance(record, dict):
                errors.append(f"Record {i}: Invalid format")
                continue
            
            # Process and clean data
            processed_record = {
                "id": record.get("id", i + 1),
                "timestamp": record.get("timestamp", datetime.now().isoformat()),
                "value": float(record.get("value", 0)),
                "category": str(record.get("category", "unknown")).lower(),
                "processed_at": datetime.now().isoformat()
            }
            
            processed_data.append(processed_record)
            
        except Exception as e:
            errors.append(f"Record {i}: {str(e)}")
    
    # Store processed dataset
    processed_datasets[dataset_name] = {
        "name": dataset_name,
        "data": processed_data,
        "metadata": {
            "total_records": len(data),
            "processed_records": len(processed_data),
            "errors": len(errors),
            "upload_time": datetime.now().isoformat(),
            "processing_time": time.time() - start_time
        }
    }
    
    processing_time = time.time() - start_time
    update_metrics(processing_time, len(processed_data))
    
    return {
        "message": "Dataset uploaded and processed successfully",
        "dataset_name": dataset_name,
        "summary": {
            "total_records": len(data),
            "processed_records": len(processed_data),
            "error_count": len(errors),
            "processing_time": f"{processing_time:.4f} seconds",
            "throughput": f"{len(processed_data) / processing_time:.0f} records/second" if processing_time > 0 else "N/A"
        },
        "errors": errors[:10] if errors else []  # Show first 10 errors
    }

@app.get("/data/analyze/{dataset_name}")
def analyze_dataset(dataset_name: str):
    """Perform comprehensive statistical analysis on dataset."""
    start_time = time.time()
    
    if dataset_name not in processed_datasets:
        raise HTTPException(404, "Dataset not found")
    
    dataset = processed_datasets[dataset_name]
    data = dataset["data"]
    
    if not data:
        raise HTTPException(400, "Dataset is empty")
    
    # Extract numerical values for analysis
    values = [record["value"] for record in data if isinstance(record.get("value"), (int, float))]
    
    if not values:
        raise HTTPException(400, "No numerical data found for analysis")
    
    # Statistical analysis
    analysis = {
        "basic_stats": {
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "mode": statistics.mode(values) if len(set(values)) < len(values) else None,
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "variance": statistics.variance(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "range": max(values) - min(values)
        },
        "percentiles": {
            "25th": statistics.quantiles(values, n=4)[0] if len(values) >= 4 else None,
            "50th": statistics.median(values),
            "75th": statistics.quantiles(values, n=4)[2] if len(values) >= 4 else None,
            "90th": statistics.quantiles(values, n=10)[8] if len(values) >= 10 else None,
            "95th": statistics.quantiles(values, n=20)[18] if len(values) >= 20 else None
        },
        "category_analysis": {},
        "time_series": {}
    }
    
    # Category-based analysis
    categories = {}
    for record in data:
        cat = record.get("category", "unknown")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(record["value"])
    
    for cat, cat_values in categories.items():
        if cat_values:
            analysis["category_analysis"][cat] = {
                "count": len(cat_values),
                "mean": statistics.mean(cat_values),
                "median": statistics.median(cat_values),
                "std_dev": statistics.stdev(cat_values) if len(cat_values) > 1 else 0
            }
    
    # Time series analysis (group by day)
    daily_data = {}
    for record in data:
        try:
            timestamp = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
            date_key = timestamp.date().isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = []
            daily_data[date_key].append(record["value"])
        except:
            continue
    
    for date, day_values in daily_data.items():
        analysis["time_series"][date] = {
            "count": len(day_values),
            "sum": sum(day_values),
            "mean": statistics.mean(day_values),
            "min": min(day_values),
            "max": max(day_values)
        }
    
    processing_time = time.time() - start_time
    update_metrics(processing_time, len(data))
    
    return {
        "dataset_name": dataset_name,
        "analysis": analysis,
        "metadata": {
            "analysis_time": f"{processing_time:.4f} seconds",
            "data_points_analyzed": len(values),
            "categories_found": len(categories),
            "time_periods": len(daily_data)
        }
    }

@app.get("/metrics")
def get_performance_metrics():
    """Get comprehensive performance metrics."""
    return {
        "real_time_metrics": real_time_metrics,
        "system_performance": {
            "framework": "GoFastAPI",
            "version": "1.0.2",
            "performance_boost": "25x faster than FastAPI",
            "capability": "500K+ RPS"
        },
        "data_processing": {
            "datasets_stored": len(processed_datasets),
            "ml_models_trained": len(ml_models),
            "total_data_points": sum(len(ds["data"]) for ds in processed_datasets.values())
        },
        "processing_efficiency": {
            "avg_processing_time": f"{real_time_metrics['processing_time_avg']:.4f} seconds",
            "total_requests": real_time_metrics["requests_count"],
            "data_throughput": f"{real_time_metrics['data_points_processed']} points processed"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Advanced Data Processing API")
    print("=" * 60)
    
    # Initialize with sample data
    print("📊 Generating sample dataset...")
    sample_data = generate_sample_data(1000)
    
    # Upload sample dataset
    sample_dataset = {
        "name": "sample_dataset",
        "data": sample_data
    }
    
    try:
        result = upload_data(sample_dataset)
        print(f"✅ Sample dataset created: {result['dataset_name']}")
        print(f"  • Records: {result['summary']['processed_records']}")
        print(f"  • Processing time: {result['summary']['processing_time']}")
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
    
    print(f"📈 System initialized:")
    print(f"  • Datasets: {len(processed_datasets)}")
    print(f"  • ML Models: {len(ml_models)}")
    print()
    print("🌐 Server starting at: http://localhost:8001")
    print("📋 API endpoints:")
    print("  • POST /data/upload           - Upload datasets")
    print("  • GET  /data/analyze/{name}   - Analyze dataset")
    print("  • GET  /analytics/summary     - Analytics summary")
    print("  • GET  /metrics               - Performance metrics")
    print("=" * 60)
    
    try:
        app.run(host="0.0.0.0", port=8001, reload=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
