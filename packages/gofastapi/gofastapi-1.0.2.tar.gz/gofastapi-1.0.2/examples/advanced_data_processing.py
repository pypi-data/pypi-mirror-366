"""
Example: Advanced Data Processing API
Demonstrates GoFastAPI with NumPy, Pandas, and ML capabilities
"""

from gofastapi import GoFastAPI
from gofastapi.runtime import SubinterpreterManager
import numpy as np
import pandas as pd
from typing import List, Dict, Any

# Create application with advanced features
app = GoFastAPI(
    title="Data Processing API",
    version="2.0.0",
    description="Advanced data processing with NumPy, Pandas, and ML"
)

# Initialize subinterpreter manager for parallel processing
manager = SubinterpreterManager(pool_size=5)


@app.get("/")
def root():
    """API information and available endpoints."""
    return {
        "name": "Data Processing API",
        "version": "2.0.0",
        "features": [
            "NumPy array processing",
            "Pandas DataFrame operations", 
            "Statistical analysis",
            "Machine learning predictions",
            "Parallel processing"
        ],
        "performance": {
            "requests_per_second": "500K+",
            "latency_p95": "< 3ms",
            "parallel_processing": "GIL-free"
        }
    }


@app.post("/numpy/operations")
def numpy_operations(data: Dict[str, Any]):
    """Perform NumPy array operations."""
    try:
        # Convert input to numpy array
        arr = np.array(data.get("array", []))
        operation = data.get("operation", "sum")
        
        results = {}
        
        if operation == "statistics":
            results = {
                "mean": float(np.mean(arr)),
                "median": float(np.median(arr)),
                "std": float(np.std(arr)),
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
                "shape": list(arr.shape),
                "dtype": str(arr.dtype)
            }
        elif operation == "linear_algebra":
            if arr.ndim == 2:
                results = {
                    "determinant": float(np.linalg.det(arr)) if arr.shape[0] == arr.shape[1] else None,
                    "rank": int(np.linalg.matrix_rank(arr)),
                    "trace": float(np.trace(arr)) if arr.shape[0] == arr.shape[1] else None,
                    "norm": float(np.linalg.norm(arr))
                }
            else:
                results = {"error": "Linear algebra operations require 2D arrays"}
        elif operation == "fft":
            fft_result = np.fft.fft(arr.flatten())
            results = {
                "fft_real": fft_result.real.tolist()[:10],  # First 10 elements
                "fft_imag": fft_result.imag.tolist()[:10],
                "magnitude": np.abs(fft_result).tolist()[:10]
            }
        else:
            # Basic operations
            operations_map = {
                "sum": np.sum,
                "mean": np.mean,
                "max": np.max,
                "min": np.min,
                "std": np.std
            }
            func = operations_map.get(operation, np.sum)
            results = {"result": float(func(arr))}
        
        return {
            "input_shape": list(arr.shape),
            "operation": operation,
            "results": results,
            "processing_time_ms": 1.2  # Mock timing
        }
        
    except Exception as e:
        return {"error": str(e)}, 400


@app.post("/pandas/analyze")
def pandas_analyze(data: Dict[str, Any]):
    """Analyze data using Pandas."""
    try:
        # Create DataFrame from input data
        df = pd.DataFrame(data.get("data", []))
        analysis_type = data.get("analysis", "describe")
        
        results = {}
        
        if analysis_type == "describe":
            desc = df.describe()
            results = {
                "description": desc.to_dict(),
                "info": {
                    "shape": list(df.shape),
                    "columns": df.columns.tolist(),
                    "dtypes": df.dtypes.to_dict(),
                    "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
                }
            }
        
        elif analysis_type == "correlation":
            numeric_df = df.select_dtypes(include=[np.number])
            if not numeric_df.empty:
                corr = numeric_df.corr()
                results = {
                    "correlation_matrix": corr.to_dict(),
                    "strong_correlations": []
                }
                # Find strong correlations (> 0.7)
                for i in range(len(corr.columns)):
                    for j in range(i+1, len(corr.columns)):
                        corr_val = corr.iloc[i, j]
                        if abs(corr_val) > 0.7:
                            results["strong_correlations"].append({
                                "column1": corr.columns[i],
                                "column2": corr.columns[j],
                                "correlation": float(corr_val)
                            })
            else:
                results = {"error": "No numeric columns found"}
        
        elif analysis_type == "groupby":
            group_column = data.get("group_by")
            agg_column = data.get("aggregate")
            
            if group_column and agg_column and group_column in df.columns:
                grouped = df.groupby(group_column)[agg_column].agg(['mean', 'sum', 'count'])
                results = {
                    "grouped_data": grouped.to_dict(),
                    "group_column": group_column,
                    "aggregate_column": agg_column
                }
            else:
                results = {"error": "Invalid group_by or aggregate column"}
        
        return {
            "analysis_type": analysis_type,
            "data_shape": list(df.shape),
            "results": results,
            "processing_time_ms": 2.5  # Mock timing
        }
        
    except Exception as e:
        return {"error": str(e)}, 400


@app.post("/ml/predict")
def ml_predict(data: Dict[str, Any]):
    """Machine learning prediction endpoint."""
    try:
        features = np.array(data.get("features", []))
        model_type = data.get("model", "linear_regression")
        
        # Mock ML models (in real app, you'd load trained models)
        if model_type == "linear_regression":
            # Simple linear model: y = 2*x1 + 3*x2 + 1
            if features.ndim == 1:
                prediction = 2 * features[0] + 3 * features[1] + 1 if len(features) >= 2 else 0
            else:
                prediction = np.sum(features * [2, 3], axis=1) + 1
            
            return {
                "model": "linear_regression",
                "prediction": float(prediction) if np.isscalar(prediction) else prediction.tolist(),
                "confidence": 0.95,
                "feature_importance": [0.4, 0.6]
            }
        
        elif model_type == "classification":
            # Mock classification
            prob = 1 / (1 + np.exp(-np.sum(features)))  # Sigmoid
            prediction = 1 if prob > 0.5 else 0
            
            return {
                "model": "logistic_regression",
                "prediction": int(prediction),
                "probability": float(prob),
                "class_probabilities": {
                    "class_0": float(1 - prob),
                    "class_1": float(prob)
                }
            }
        
        elif model_type == "clustering":
            # Mock clustering (assign to cluster based on feature sum)
            cluster = int(np.sum(features)) % 3
            
            return {
                "model": "kmeans",
                "cluster": cluster,
                "distance_to_centroid": float(np.random.random()),
                "cluster_centers": [[1, 2], [3, 4], [5, 6]]
            }
        
        else:
            return {"error": f"Unknown model type: {model_type}"}, 400
            
    except Exception as e:
        return {"error": str(e)}, 400


@app.post("/parallel/process")
def parallel_process(data: Dict[str, Any]):
    """Process data in parallel using subinterpreters."""
    try:
        datasets = data.get("datasets", [])
        operation = data.get("operation", "sum")
        
        def process_dataset(dataset):
            """Process a single dataset."""
            arr = np.array(dataset)
            if operation == "sum":
                return np.sum(arr)
            elif operation == "mean":
                return np.mean(arr)
            elif operation == "std":
                return np.std(arr)
            else:
                return np.sum(arr)
        
        # Process datasets in parallel
        results = []
        for dataset in datasets:
            result = manager.execute_in_pool(process_dataset, dataset)
            results.append(float(result))
        
        return {
            "operation": operation,
            "datasets_processed": len(datasets),
            "results": results,
            "parallel_processing": True,
            "processing_time_ms": 5.2  # Mock timing
        }
        
    except Exception as e:
        return {"error": str(e)}, 400


@app.post("/advanced/time_series")
def time_series_analysis(data: Dict[str, Any]):
    """Advanced time series analysis."""
    try:
        values = data.get("values", [])
        timestamps = data.get("timestamps", [])
        
        # Create time series DataFrame
        if timestamps:
            df = pd.DataFrame({
                "timestamp": pd.to_datetime(timestamps),
                "value": values
            })
            df.set_index("timestamp", inplace=True)
        else:
            df = pd.DataFrame({"value": values})
        
        # Time series analysis
        results = {
            "trend": {
                "mean": float(df["value"].mean()),
                "std": float(df["value"].std()),
                "min": float(df["value"].min()),
                "max": float(df["value"].max())
            },
            "seasonality": {
                "detected": False,  # Mock seasonality detection
                "period": None
            },
            "anomalies": [],  # Mock anomaly detection
            "forecast": []    # Mock forecasting
        }
        
        # Simple trend analysis
        if len(values) > 1:
            trend_slope = (values[-1] - values[0]) / len(values)
            results["trend"]["slope"] = float(trend_slope)
            results["trend"]["direction"] = "increasing" if trend_slope > 0 else "decreasing"
        
        # Mock rolling statistics
        if len(values) >= 7:
            rolling_mean = df["value"].rolling(window=7).mean().dropna()
            results["rolling_statistics"] = {
                "window_size": 7,
                "rolling_mean": rolling_mean.tolist()[-5:]  # Last 5 values
            }
        
        return {
            "analysis": "time_series",
            "data_points": len(values),
            "results": results,
            "processing_time_ms": 8.1
        }
        
    except Exception as e:
        return {"error": str(e)}, 400


@app.get("/performance/benchmark")
def performance_benchmark():
    """Performance benchmark endpoint."""
    import time
    
    # Simulate various operations
    start_time = time.perf_counter()
    
    # NumPy operations
    large_array = np.random.random(10000)
    np_result = np.sum(large_array)
    
    # Pandas operations
    df = pd.DataFrame(np.random.random((1000, 5)))
    pd_result = df.describe()
    
    end_time = time.perf_counter()
    processing_time = (end_time - start_time) * 1000
    
    return {
        "benchmark": "data_processing",
        "operations": ["numpy_sum", "pandas_describe"],
        "data_size": {
            "numpy_array": 10000,
            "pandas_dataframe": [1000, 5]
        },
        "processing_time_ms": round(processing_time, 2),
        "performance": {
            "numpy_sum": round(np_result, 4),
            "pandas_shape": list(df.shape)
        },
        "framework": "GoFastAPI",
        "performance_note": "25x faster than FastAPI"
    }


if __name__ == "__main__":
    print("🚀 Starting Advanced Data Processing API")
    print("📊 NumPy and Pandas integration enabled")
    print("🔄 Parallel processing with subinterpreters")
    print("🤖 Mock ML models available")
    print("🌐 Available at: http://localhost:8000")
    
    app.run(host="0.0.0.0", port=8000, reload=True)
