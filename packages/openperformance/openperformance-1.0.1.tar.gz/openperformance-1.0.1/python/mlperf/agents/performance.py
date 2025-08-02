"""Performance analysis agent for detailed performance insights."""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats

from mlperf.agents.base import Agent, AgentContext, AgentResponse, AgentTask
from mlperf.utils.logging import get_logger

logger = get_logger(__name__)


class PerformanceAnalysisAgent(Agent):
    """Agent specialized in analyzing performance data and generating insights."""
    
    def __init__(self):
        super().__init__(
            name="PerformanceAnalysisAgent",
            description="ML performance analysis and insights generation",
            model="gpt-4",
            instructions="""You are an expert in ML performance analysis and optimization.
            
Your responsibilities include:
1. Analyzing performance metrics across different dimensions
2. Identifying trends, patterns, and anomalies in performance data
3. Providing root cause analysis for performance issues
4. Generating actionable insights and recommendations
5. Creating performance reports and visualizations
6. Comparing performance across different configurations and time periods

When analyzing performance, consider:
- Statistical significance of performance changes
- Hardware resource utilization patterns
- Framework and library bottlenecks
- Workload characteristics and scaling behavior
- Cost-performance trade-offs
- Long-term performance trends
""",
            temperature=0.3,  # Lower temperature for analytical consistency
        )
    
    async def process(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Process performance analysis tasks."""
        start_time = datetime.utcnow()
        
        try:
            # Validate task
            if not await self.validate_task(task):
                return AgentResponse(
                    task_id=task.task_id,
                    status="failed",
                    result={"error": "Invalid task for PerformanceAnalysisAgent"},
                    reasoning="Task type not supported by this agent",
                    confidence=0.0,
                    execution_time=0.0,
                )
            
            # Route to appropriate handler
            if task.task_type == "analyze_metrics":
                response = await self._analyze_metrics(task, context)
            elif task.task_type == "detect_anomalies":
                response = await self._detect_anomalies(task, context)
            elif task.task_type == "root_cause_analysis":
                response = await self._root_cause_analysis(task, context)
            elif task.task_type == "performance_report":
                response = await self._generate_performance_report(task, context)
            elif task.task_type == "trend_analysis":
                response = await self._analyze_trends(task, context)
            elif task.task_type == "compare_configurations":
                response = await self._compare_configurations(task, context)
            else:
                response = await self._general_analysis_task(task, context)
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            response.execution_time = execution_time
            
            # Update context
            self.update_context(context, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in PerformanceAnalysisAgent: {e}")
            return AgentResponse(
                task_id=task.task_id,
                status="failed",
                result={"error": str(e)},
                reasoning=f"Error during performance analysis: {e}",
                confidence=0.0,
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
            )
    
    async def validate_task(self, task: AgentTask) -> bool:
        """Validate if this agent can handle the task."""
        valid_types = [
            "analyze_metrics",
            "detect_anomalies",
            "root_cause_analysis",
            "performance_report",
            "trend_analysis",
            "compare_configurations",
            "performance_analysis",
            "profiling_analysis",
        ]
        return task.task_type in valid_types
    
    async def _analyze_metrics(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Analyze performance metrics in detail."""
        params = task.parameters
        metrics = params.get("metrics", {})
        time_range = params.get("time_range", "last_hour")
        dimensions = params.get("dimensions", ["hardware", "workload", "framework"])
        
        analysis = {
            "summary": {},
            "insights": [],
            "metrics_breakdown": {},
            "correlations": {},
            "recommendations": []
        }
        
        # Summary statistics
        for metric_name, values in metrics.items():
            if isinstance(values, list) and values:
                analysis["summary"][metric_name] = {
                    "mean": np.mean(values),
                    "median": np.median(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "p95": np.percentile(values, 95),
                    "p99": np.percentile(values, 99),
                    "cv": np.std(values) / np.mean(values) if np.mean(values) != 0 else 0,  # Coefficient of variation
                }
                
                # Identify issues
                if analysis["summary"][metric_name]["cv"] > 0.3:
                    analysis["insights"].append({
                        "type": "high_variability",
                        "metric": metric_name,
                        "severity": "medium",
                        "description": f"{metric_name} shows high variability (CV={analysis['summary'][metric_name]['cv']:.2f})",
                        "impact": "Inconsistent performance may affect user experience"
                    })
        
        # Dimensional analysis
        if "dimensional_metrics" in params:
            for dimension in dimensions:
                if dimension in params["dimensional_metrics"]:
                    analysis["metrics_breakdown"][dimension] = self._analyze_dimension(
                        params["dimensional_metrics"][dimension]
                    )
        
        # Correlation analysis
        metric_names = list(metrics.keys())
        if len(metric_names) >= 2:
            correlation_matrix = self._calculate_correlations(metrics)
            analysis["correlations"] = correlation_matrix
            
            # Find strong correlations
            for i, metric1 in enumerate(metric_names):
                for j, metric2 in enumerate(metric_names[i+1:], i+1):
                    corr = correlation_matrix.get(f"{metric1}_vs_{metric2}", 0)
                    if abs(corr) > 0.7:
                        analysis["insights"].append({
                            "type": "strong_correlation",
                            "metrics": [metric1, metric2],
                            "correlation": corr,
                            "description": f"Strong {'positive' if corr > 0 else 'negative'} correlation between {metric1} and {metric2}",
                            "recommendation": "Consider these metrics together when optimizing"
                        })
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_metric_recommendations(analysis)
        
        reasoning = f"Analyzed {len(metrics)} metrics across {len(dimensions)} dimensions"
        reasoning += f" with {len(analysis['insights'])} insights generated"
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result=analysis,
            reasoning=reasoning,
            confidence=0.85,
            suggestions=[
                "Monitor high-variability metrics more closely",
                "Use dimensional breakdowns to identify optimization opportunities",
                "Consider correlated metrics when making changes",
            ],
            next_steps=[
                "Run anomaly detection on high-variability metrics",
                "Perform root cause analysis on identified issues",
                "Set up alerts for metric thresholds",
            ],
        )
    
    async def _detect_anomalies(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Detect anomalies in performance data."""
        params = task.parameters
        metrics = params.get("metrics", {})
        sensitivity = params.get("sensitivity", "medium")
        methods = params.get("methods", ["statistical", "isolation_forest"])
        
        anomalies = {
            "detected_anomalies": [],
            "anomaly_scores": {},
            "time_periods": [],
            "affected_metrics": set(),
        }
        
        # Statistical anomaly detection
        if "statistical" in methods:
            for metric_name, values in metrics.items():
                if isinstance(values, list) and len(values) > 10:
                    # Z-score based detection
                    z_scores = np.abs(stats.zscore(values))
                    threshold = {
                        "low": 3.5,
                        "medium": 3.0,
                        "high": 2.5
                    }.get(sensitivity, 3.0)
                    
                    anomaly_indices = np.where(z_scores > threshold)[0]
                    
                    for idx in anomaly_indices:
                        anomalies["detected_anomalies"].append({
                            "metric": metric_name,
                            "index": int(idx),
                            "value": values[idx],
                            "z_score": float(z_scores[idx]),
                            "type": "statistical_outlier",
                            "severity": self._classify_anomaly_severity(z_scores[idx]),
                        })
                        anomalies["affected_metrics"].add(metric_name)
        
        # Pattern-based anomaly detection
        if "pattern" in methods:
            for metric_name, values in metrics.items():
                if isinstance(values, list) and len(values) > 20:
                    # Detect sudden spikes/drops
                    changes = np.diff(values)
                    change_threshold = np.std(changes) * 2.5
                    
                    spike_indices = np.where(np.abs(changes) > change_threshold)[0]
                    
                    for idx in spike_indices:
                        anomalies["detected_anomalies"].append({
                            "metric": metric_name,
                            "index": int(idx + 1),  # +1 because diff reduces length by 1
                            "value": values[idx + 1],
                            "change": float(changes[idx]),
                            "type": "sudden_change",
                            "severity": "high" if abs(changes[idx]) > change_threshold * 2 else "medium",
                        })
                        anomalies["affected_metrics"].add(metric_name)
        
        # Aggregate anomalies by time period
        if "timestamps" in params:
            anomalies["time_periods"] = self._aggregate_anomalies_by_time(
                anomalies["detected_anomalies"],
                params["timestamps"]
            )
        
        # Convert set to list for JSON serialization
        anomalies["affected_metrics"] = list(anomalies["affected_metrics"])
        
        reasoning = f"Detected {len(anomalies['detected_anomalies'])} anomalies"
        reasoning += f" across {len(anomalies['affected_metrics'])} metrics"
        reasoning += f" using {len(methods)} detection methods"
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result=anomalies,
            reasoning=reasoning,
            confidence=0.8,
            suggestions=[
                "Investigate high-severity anomalies first",
                "Check system logs around anomaly timestamps",
                "Correlate anomalies with deployment or configuration changes",
            ],
            next_steps=[
                "Perform root cause analysis on detected anomalies",
                "Set up real-time anomaly detection alerts",
                "Review and adjust sensitivity thresholds",
            ],
        )
    
    async def _root_cause_analysis(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Perform root cause analysis for performance issues."""
        params = task.parameters
        issue = params.get("issue", {})
        metrics = params.get("metrics", {})
        system_info = params.get("system_info", {})
        timeline = params.get("timeline", [])
        
        root_cause_analysis = {
            "probable_causes": [],
            "contributing_factors": [],
            "evidence": [],
            "remediation_steps": [],
            "prevention_measures": [],
        }
        
        # Analyze the issue
        issue_type = issue.get("type", "performance_degradation")
        affected_metrics = issue.get("affected_metrics", [])
        
        # Check for common root causes
        # 1. Resource exhaustion
        if any(metric in affected_metrics for metric in ["memory_usage", "gpu_memory"]):
            if metrics.get("memory_usage", {}).get("max", 0) > 0.9:
                root_cause_analysis["probable_causes"].append({
                    "cause": "Memory exhaustion",
                    "confidence": 0.9,
                    "evidence": ["Memory usage exceeded 90%"],
                    "impact": "System performance degradation, potential OOM errors",
                })
                root_cause_analysis["remediation_steps"].extend([
                    "Reduce batch size",
                    "Enable gradient checkpointing",
                    "Optimize memory allocations",
                ])
        
        # 2. Thermal throttling
        if system_info.get("temperature", {}).get("gpu", 0) > 80:
            root_cause_analysis["probable_causes"].append({
                "cause": "Thermal throttling",
                "confidence": 0.85,
                "evidence": [f"GPU temperature: {system_info['temperature']['gpu']}°C"],
                "impact": "Reduced clock speeds, inconsistent performance",
            })
            root_cause_analysis["remediation_steps"].extend([
                "Improve cooling solution",
                "Reduce power limit",
                "Optimize workload scheduling",
            ])
        
        # 3. I/O bottleneck
        if "data_loading_time" in affected_metrics:
            data_loading_ratio = metrics.get("data_loading_time", {}).get("mean", 0) / metrics.get("compute_time", {}).get("mean", 1)
            if data_loading_ratio > 0.3:
                root_cause_analysis["probable_causes"].append({
                    "cause": "I/O bottleneck",
                    "confidence": 0.8,
                    "evidence": [f"Data loading takes {data_loading_ratio*100:.1f}% of compute time"],
                    "impact": "GPU underutilization, reduced throughput",
                })
                root_cause_analysis["remediation_steps"].extend([
                    "Increase number of data loader workers",
                    "Enable data prefetching",
                    "Use faster storage (NVMe SSD)",
                ])
        
        # 4. Configuration issues
        if timeline:
            # Look for configuration changes that correlate with issue start
            for event in timeline:
                if event.get("type") == "configuration_change":
                    root_cause_analysis["contributing_factors"].append({
                        "factor": f"Configuration change: {event.get('description', 'Unknown')}",
                        "timestamp": event.get("timestamp"),
                        "correlation": "temporal",
                    })
        
        # Generate prevention measures
        root_cause_analysis["prevention_measures"] = [
            "Implement comprehensive monitoring and alerting",
            "Establish performance baselines and track deviations",
            "Create automated performance regression tests",
            "Document optimal configuration settings",
            "Regular system maintenance and updates",
        ]
        
        reasoning = f"Analyzed {issue_type} affecting {len(affected_metrics)} metrics"
        reasoning += f", identified {len(root_cause_analysis['probable_causes'])} probable causes"
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result=root_cause_analysis,
            reasoning=reasoning,
            confidence=0.75,
            suggestions=[
                "Address high-confidence root causes first",
                "Implement monitoring for identified factors",
                "Test remediation steps in a controlled environment",
            ],
            next_steps=[
                "Apply remediation steps in order of impact",
                "Monitor metrics after each change",
                "Document findings for future reference",
            ],
        )
    
    async def _generate_performance_report(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Generate comprehensive performance report."""
        params = task.parameters
        time_range = params.get("time_range", "last_24_hours")
        metrics = params.get("metrics", {})
        benchmarks = params.get("benchmarks", [])
        comparisons = params.get("comparisons", {})
        
        report = {
            "executive_summary": {},
            "performance_overview": {},
            "key_findings": [],
            "detailed_analysis": {},
            "recommendations": [],
            "appendix": {},
        }
        
        # Executive summary
        report["executive_summary"] = {
            "report_period": time_range,
            "overall_performance": self._calculate_overall_performance(metrics),
            "key_metrics": self._extract_key_metrics(metrics),
            "performance_trend": self._determine_trend(metrics),
            "critical_issues": [],
            "highlights": [],
        }
        
        # Performance overview
        report["performance_overview"] = {
            "throughput": {
                "current": metrics.get("throughput", {}).get("mean", 0),
                "change": self._calculate_change(metrics.get("throughput", {}), comparisons.get("baseline", {})),
                "trend": "improving" if self._calculate_change(metrics.get("throughput", {}), comparisons.get("baseline", {})) > 0 else "degrading",
            },
            "latency": {
                "p50": metrics.get("latency", {}).get("p50", 0),
                "p95": metrics.get("latency", {}).get("p95", 0),
                "p99": metrics.get("latency", {}).get("p99", 0),
                "trend": self._determine_latency_trend(metrics.get("latency", {})),
            },
            "resource_utilization": {
                "gpu": metrics.get("gpu_utilization", {}).get("mean", 0),
                "memory": metrics.get("memory_usage", {}).get("mean", 0),
                "efficiency": self._calculate_efficiency(metrics),
            },
        }
        
        # Key findings
        findings = []
        
        # Check for performance improvements
        if report["performance_overview"]["throughput"]["change"] > 10:
            findings.append({
                "type": "improvement",
                "title": "Significant throughput improvement",
                "description": f"Throughput increased by {report['performance_overview']['throughput']['change']:.1f}%",
                "impact": "positive",
                "priority": "info",
            })
        
        # Check for issues
        if report["performance_overview"]["resource_utilization"]["gpu"] < 70:
            findings.append({
                "type": "issue",
                "title": "Low GPU utilization",
                "description": f"GPU utilization is only {report['performance_overview']['resource_utilization']['gpu']:.1f}%",
                "impact": "negative",
                "priority": "high",
            })
            report["executive_summary"]["critical_issues"].append("Low GPU utilization")
        
        report["key_findings"] = findings
        
        # Detailed analysis
        report["detailed_analysis"] = {
            "performance_breakdown": self._create_performance_breakdown(metrics, benchmarks),
            "bottleneck_analysis": self._analyze_bottlenecks(metrics),
            "scaling_analysis": self._analyze_scaling(metrics, params.get("scaling_data", {})),
            "cost_analysis": self._calculate_cost_metrics(metrics, params.get("cost_data", {})),
        }
        
        # Recommendations
        report["recommendations"] = self._generate_report_recommendations(report)
        
        # Appendix
        report["appendix"] = {
            "methodology": "Statistical analysis using mean, percentiles, and trend detection",
            "data_sources": params.get("data_sources", ["benchmark_results", "system_metrics"]),
            "glossary": {
                "throughput": "Number of operations completed per second",
                "latency": "Time taken to complete a single operation",
                "efficiency": "Ratio of useful work to total resources consumed",
            },
        }
        
        reasoning = f"Generated comprehensive performance report for {time_range}"
        reasoning += f" with {len(findings)} key findings and {len(report['recommendations'])} recommendations"
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result=report,
            reasoning=reasoning,
            confidence=0.9,
            suggestions=[
                "Share report with stakeholders",
                "Create action items from recommendations",
                "Schedule follow-up analysis",
            ],
            next_steps=[
                "Implement high-priority recommendations",
                "Set up automated report generation",
                "Track progress on identified issues",
            ],
        )
    
    async def _analyze_trends(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Analyze performance trends over time."""
        params = task.parameters
        time_series_data = params.get("time_series_data", {})
        metrics_to_analyze = params.get("metrics", [])
        time_window = params.get("time_window", "7_days")
        
        trend_analysis = {
            "trends": {},
            "seasonality": {},
            "change_points": [],
            "forecasts": {},
            "alerts": [],
        }
        
        for metric in metrics_to_analyze:
            if metric in time_series_data:
                data = time_series_data[metric]
                if isinstance(data, list) and len(data) > 10:
                    # Calculate trend
                    trend = self._calculate_trend(data)
                    trend_analysis["trends"][metric] = {
                        "direction": trend["direction"],
                        "strength": trend["strength"],
                        "slope": trend["slope"],
                        "r_squared": trend["r_squared"],
                    }
                    
                    # Detect seasonality
                    if len(data) > 48:  # Need enough data for seasonality
                        seasonality = self._detect_seasonality(data)
                        if seasonality["is_seasonal"]:
                            trend_analysis["seasonality"][metric] = seasonality
                    
                    # Detect change points
                    change_points = self._detect_change_points(data)
                    for cp in change_points:
                        trend_analysis["change_points"].append({
                            "metric": metric,
                            "index": cp["index"],
                            "magnitude": cp["magnitude"],
                            "type": cp["type"],
                        })
                    
                    # Simple forecast (linear extrapolation)
                    forecast = self._simple_forecast(data, horizon=24)
                    trend_analysis["forecasts"][metric] = {
                        "values": forecast,
                        "confidence_interval": self._calculate_forecast_ci(data, forecast),
                    }
                    
                    # Generate alerts
                    if trend["direction"] == "decreasing" and metric in ["throughput", "performance"]:
                        trend_analysis["alerts"].append({
                            "metric": metric,
                            "type": "performance_degradation",
                            "severity": "high" if trend["strength"] > 0.5 else "medium",
                            "message": f"{metric} showing {trend['strength']*100:.1f}% decline",
                        })
        
        reasoning = f"Analyzed trends for {len(metrics_to_analyze)} metrics over {time_window}"
        reasoning += f", detected {len(trend_analysis['change_points'])} change points"
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result=trend_analysis,
            reasoning=reasoning,
            confidence=0.85,
            suggestions=[
                "Monitor metrics with negative trends closely",
                "Investigate change points for root causes",
                "Use forecasts for capacity planning",
            ],
            next_steps=[
                "Set up alerts for trend reversals",
                "Create automated trend reports",
                "Implement predictive maintenance based on forecasts",
            ],
        )
    
    async def _compare_configurations(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Compare performance across different configurations."""
        params = task.parameters
        configurations = params.get("configurations", [])
        metrics = params.get("metrics", ["throughput", "latency", "efficiency"])
        comparison_type = params.get("comparison_type", "relative")
        
        comparison = {
            "configuration_summary": {},
            "metric_comparisons": {},
            "best_configuration": {},
            "trade_offs": [],
            "statistical_significance": {},
            "recommendations": [],
        }
        
        # Summarize each configuration
        for config in configurations:
            config_id = config.get("id", "unknown")
            comparison["configuration_summary"][config_id] = {
                "description": config.get("description", ""),
                "parameters": config.get("parameters", {}),
                "hardware": config.get("hardware", {}),
                "software": config.get("software", {}),
            }
        
        # Compare metrics across configurations
        for metric in metrics:
            metric_values = {}
            for config in configurations:
                config_id = config.get("id")
                if metric in config.get("results", {}):
                    metric_values[config_id] = config["results"][metric]
            
            if len(metric_values) >= 2:
                comparison["metric_comparisons"][metric] = self._compare_metric_values(
                    metric_values,
                    comparison_type
                )
                
                # Statistical significance testing
                if len(metric_values) >= 2 and all(isinstance(v, list) for v in metric_values.values()):
                    comparison["statistical_significance"][metric] = self._test_significance(
                        metric_values
                    )
        
        # Identify best configuration
        scores = {}
        for config_id in comparison["configuration_summary"]:
            score = 0
            for metric in metrics:
                if metric in comparison["metric_comparisons"]:
                    ranking = comparison["metric_comparisons"][metric].get("ranking", {})
                    if config_id in ranking:
                        # Higher rank = better (1st place gets highest score)
                        score += len(ranking) - ranking[config_id] + 1
            scores[config_id] = score
        
        best_config_id = max(scores, key=scores.get) if scores else None
        if best_config_id:
            comparison["best_configuration"] = {
                "id": best_config_id,
                "score": scores[best_config_id],
                "wins": [m for m, comp in comparison["metric_comparisons"].items() 
                        if comp.get("best") == best_config_id],
            }
        
        # Identify trade-offs
        for metric1 in metrics:
            for metric2 in metrics:
                if metric1 != metric2:
                    trade_off = self._identify_trade_off(
                        comparison["metric_comparisons"].get(metric1, {}),
                        comparison["metric_comparisons"].get(metric2, {})
                    )
                    if trade_off:
                        comparison["trade_offs"].append(trade_off)
        
        # Generate recommendations
        comparison["recommendations"] = self._generate_comparison_recommendations(comparison)
        
        reasoning = f"Compared {len(configurations)} configurations across {len(metrics)} metrics"
        if best_config_id:
            reasoning += f", identified {best_config_id} as best overall"
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result=comparison,
            reasoning=reasoning,
            confidence=0.85,
            suggestions=[
                f"Deploy configuration '{best_config_id}' for best overall performance" if best_config_id else "Gather more data for conclusive comparison",
                "Consider trade-offs based on your priorities",
                "Validate results with longer benchmark runs",
            ],
            next_steps=[
                "Run statistical validation on best configuration",
                "Test edge cases and failure scenarios",
                "Document configuration decision rationale",
            ],
        )
    
    async def _general_analysis_task(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Handle general performance analysis tasks."""
        # Fallback for general analysis questions
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result={
                "response": "General performance analysis completed",
                "task_type": task.task_type,
                "parameters": task.parameters,
            },
            reasoning="Processed general performance analysis task",
            confidence=0.7,
            suggestions=[
                "Use specific analysis types for more detailed insights",
                "Provide more context for better analysis",
                "Consider running comprehensive performance report",
            ],
            next_steps=[
                "Define specific analysis objectives",
                "Gather relevant performance data",
                "Select appropriate analysis methods",
            ],
        )
    
    def _analyze_dimension(self, dimensional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze metrics across a specific dimension."""
        analysis = {
            "distribution": {},
            "outliers": [],
            "top_performers": [],
            "bottom_performers": [],
        }
        
        # Sort by performance
        sorted_items = sorted(
            dimensional_data.items(),
            key=lambda x: x[1].get("value", 0),
            reverse=True
        )
        
        # Top and bottom performers
        if len(sorted_items) >= 3:
            analysis["top_performers"] = [
                {"name": k, "value": v.get("value", 0)} 
                for k, v in sorted_items[:3]
            ]
            analysis["bottom_performers"] = [
                {"name": k, "value": v.get("value", 0)} 
                for k, v in sorted_items[-3:]
            ]
        
        return analysis
    
    def _calculate_correlations(self, metrics: Dict[str, List[float]]) -> Dict[str, float]:
        """Calculate correlations between metrics."""
        correlations = {}
        
        metric_names = list(metrics.keys())
        for i, metric1 in enumerate(metric_names):
            for j, metric2 in enumerate(metric_names[i+1:], i+1):
                if isinstance(metrics[metric1], list) and isinstance(metrics[metric2], list):
                    # Ensure same length
                    min_len = min(len(metrics[metric1]), len(metrics[metric2]))
                    if min_len > 2:
                        corr = np.corrcoef(
                            metrics[metric1][:min_len],
                            metrics[metric2][:min_len]
                        )[0, 1]
                        correlations[f"{metric1}_vs_{metric2}"] = float(corr)
        
        return correlations
    
    def _generate_metric_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on metric analysis."""
        recommendations = []
        
        # Check for high variability
        for metric, stats in analysis.get("summary", {}).items():
            if stats.get("cv", 0) > 0.3:
                recommendations.append({
                    "type": "stability",
                    "priority": "high",
                    "title": f"Stabilize {metric}",
                    "description": f"Reduce variability in {metric} (current CV={stats['cv']:.2f})",
                    "actions": [
                        "Identify sources of variability",
                        "Implement performance isolation",
                        "Use performance governors",
                    ],
                })
        
        # Check for optimization opportunities
        if "correlations" in analysis:
            for correlation, value in analysis["correlations"].items():
                if abs(value) > 0.8:
                    metrics = correlation.split("_vs_")
                    recommendations.append({
                        "type": "optimization",
                        "priority": "medium",
                        "title": f"Co-optimize {metrics[0]} and {metrics[1]}",
                        "description": f"Strong correlation ({value:.2f}) suggests joint optimization opportunity",
                        "actions": [
                            "Profile both metrics together",
                            "Find common bottlenecks",
                            "Optimize shared resources",
                        ],
                    })
        
        return recommendations
    
    def _classify_anomaly_severity(self, z_score: float) -> str:
        """Classify anomaly severity based on z-score."""
        if abs(z_score) > 4:
            return "critical"
        elif abs(z_score) > 3.5:
            return "high"
        elif abs(z_score) > 3:
            return "medium"
        else:
            return "low"
    
    def _aggregate_anomalies_by_time(self, anomalies: List[Dict], timestamps: List[str]) -> List[Dict]:
        """Aggregate anomalies by time period."""
        # Simple hourly aggregation
        time_buckets = {}
        
        for anomaly in anomalies:
            if anomaly["index"] < len(timestamps):
                # Extract hour from timestamp
                ts = timestamps[anomaly["index"]]
                hour = ts[:13]  # Assuming ISO format
                
                if hour not in time_buckets:
                    time_buckets[hour] = {
                        "period": hour,
                        "count": 0,
                        "metrics_affected": set(),
                        "severities": [],
                    }
                
                time_buckets[hour]["count"] += 1
                time_buckets[hour]["metrics_affected"].add(anomaly["metric"])
                time_buckets[hour]["severities"].append(anomaly.get("severity", "unknown"))
        
        # Convert to list and clean up sets
        result = []
        for period, data in sorted(time_buckets.items()):
            data["metrics_affected"] = list(data["metrics_affected"])
            data["dominant_severity"] = max(set(data["severities"]), key=data["severities"].count)
            result.append(data)
        
        return result
    
    def _calculate_overall_performance(self, metrics: Dict[str, Any]) -> str:
        """Calculate overall performance rating."""
        score = 0
        factors = 0
        
        # Throughput contribution
        if "throughput" in metrics:
            throughput_score = min(metrics["throughput"].get("mean", 0) / 1000, 1.0)  # Normalize
            score += throughput_score
            factors += 1
        
        # Latency contribution (inverse)
        if "latency" in metrics:
            latency_score = max(0, 1 - metrics["latency"].get("p95", 100) / 100)  # Lower is better
            score += latency_score
            factors += 1
        
        # Efficiency contribution
        if "gpu_utilization" in metrics:
            efficiency_score = metrics["gpu_utilization"].get("mean", 0) / 100
            score += efficiency_score
            factors += 1
        
        if factors == 0:
            return "unknown"
        
        overall_score = score / factors
        
        if overall_score >= 0.9:
            return "excellent"
        elif overall_score >= 0.7:
            return "good"
        elif overall_score >= 0.5:
            return "fair"
        else:
            return "poor"
    
    def _extract_key_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics for summary."""
        key_metrics = {}
        
        # Priority metrics
        priority_metrics = ["throughput", "latency", "gpu_utilization", "memory_usage"]
        
        for metric in priority_metrics:
            if metric in metrics:
                if isinstance(metrics[metric], dict):
                    if "mean" in metrics[metric]:
                        key_metrics[metric] = metrics[metric]["mean"]
                    elif "value" in metrics[metric]:
                        key_metrics[metric] = metrics[metric]["value"]
                else:
                    key_metrics[metric] = metrics[metric]
        
        return key_metrics
    
    def _determine_trend(self, metrics: Dict[str, Any]) -> str:
        """Determine overall performance trend."""
        # Simplified trend detection
        # In practice, would use time series analysis
        return "stable"  # Placeholder
    
    def _calculate_change(self, current: Dict[str, Any], baseline: Dict[str, Any]) -> float:
        """Calculate percentage change from baseline."""
        current_val = current.get("mean", current.get("value", 0))
        baseline_val = baseline.get("mean", baseline.get("value", 0))
        
        if baseline_val == 0:
            return 0.0
        
        return ((current_val - baseline_val) / baseline_val) * 100
    
    def _determine_latency_trend(self, latency_data: Dict[str, Any]) -> str:
        """Determine latency trend."""
        # Placeholder - would analyze time series
        return "stable"
    
    def _calculate_efficiency(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall efficiency score."""
        gpu_util = metrics.get("gpu_utilization", {}).get("mean", 0)
        memory_eff = 1 - metrics.get("memory_waste", {}).get("mean", 0)
        
        return (gpu_util + memory_eff) / 2
    
    def _create_performance_breakdown(self, metrics: Dict, benchmarks: List) -> Dict:
        """Create detailed performance breakdown."""
        breakdown = {
            "by_operation": {},
            "by_hardware": {},
            "by_configuration": {},
        }
        
        # Analyze benchmarks
        for benchmark in benchmarks:
            op_type = benchmark.get("operation", "unknown")
            if op_type not in breakdown["by_operation"]:
                breakdown["by_operation"][op_type] = {
                    "count": 0,
                    "avg_throughput": 0,
                    "avg_latency": 0,
                }
            
            breakdown["by_operation"][op_type]["count"] += 1
            # Add more detailed breakdown logic
        
        return breakdown
    
    def _analyze_bottlenecks(self, metrics: Dict) -> Dict:
        """Analyze performance bottlenecks."""
        bottlenecks = {
            "identified": [],
            "severity": {},
            "impact": {},
        }
        
        # GPU underutilization
        gpu_util = metrics.get("gpu_utilization", {}).get("mean", 100)
        if gpu_util < 70:
            bottlenecks["identified"].append("gpu_underutilization")
            bottlenecks["severity"]["gpu_underutilization"] = "high" if gpu_util < 50 else "medium"
            bottlenecks["impact"]["gpu_underutilization"] = f"{100-gpu_util:.1f}% wasted GPU capacity"
        
        # Memory bandwidth
        mem_bandwidth_util = metrics.get("memory_bandwidth_utilization", {}).get("mean", 0)
        if mem_bandwidth_util > 85:
            bottlenecks["identified"].append("memory_bandwidth")
            bottlenecks["severity"]["memory_bandwidth"] = "high"
            bottlenecks["impact"]["memory_bandwidth"] = "Performance limited by memory transfer"
        
        return bottlenecks
    
    def _analyze_scaling(self, metrics: Dict, scaling_data: Dict) -> Dict:
        """Analyze scaling characteristics."""
        return {
            "scaling_efficiency": scaling_data.get("efficiency", "unknown"),
            "optimal_scale": scaling_data.get("optimal_scale", "unknown"),
            "scaling_bottlenecks": scaling_data.get("bottlenecks", []),
        }
    
    def _calculate_cost_metrics(self, metrics: Dict, cost_data: Dict) -> Dict:
        """Calculate cost-related metrics."""
        throughput = metrics.get("throughput", {}).get("mean", 1)
        hourly_cost = cost_data.get("hourly_cost", 1.0)
        
        return {
            "cost_per_sample": hourly_cost / (throughput * 3600) if throughput > 0 else float('inf'),
            "samples_per_dollar": (throughput * 3600) / hourly_cost if hourly_cost > 0 else 0,
            "monthly_cost": hourly_cost * 24 * 30,
        }
    
    def _generate_report_recommendations(self, report: Dict) -> List[Dict]:
        """Generate recommendations for performance report."""
        recommendations = []
        
        # Based on findings
        for finding in report.get("key_findings", []):
            if finding["type"] == "issue" and finding["priority"] == "high":
                recommendations.append({
                    "priority": "high",
                    "title": f"Address {finding['title']}",
                    "description": finding["description"],
                    "expected_impact": "10-30% performance improvement",
                    "effort": "medium",
                })
        
        # Based on bottlenecks
        bottlenecks = report.get("detailed_analysis", {}).get("bottleneck_analysis", {}).get("identified", [])
        for bottleneck in bottlenecks[:3]:  # Top 3 bottlenecks
            recommendations.append({
                "priority": "medium",
                "title": f"Optimize {bottleneck.replace('_', ' ')}",
                "description": f"Address {bottleneck} to improve performance",
                "expected_impact": "5-15% improvement",
                "effort": "medium",
            })
        
        return recommendations
    
    def _calculate_trend(self, data: List[float]) -> Dict[str, Any]:
        """Calculate trend from time series data."""
        if len(data) < 2:
            return {"direction": "insufficient_data", "strength": 0, "slope": 0, "r_squared": 0}
        
        # Simple linear regression
        x = np.arange(len(data))
        y = np.array(data)
        
        # Calculate slope and r-squared
        slope, intercept = np.polyfit(x, y, 1)
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine direction and strength
        if abs(slope) < 0.01:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"
        
        # Strength based on r-squared and slope magnitude
        strength = abs(r_squared) * min(abs(slope) / np.mean(y) if np.mean(y) != 0 else 0, 1.0)
        
        return {
            "direction": direction,
            "strength": float(strength),
            "slope": float(slope),
            "r_squared": float(r_squared),
        }
    
    def _detect_seasonality(self, data: List[float]) -> Dict[str, Any]:
        """Detect seasonality in time series data."""
        # Simplified seasonality detection
        # In practice, would use FFT or decomposition methods
        
        # Check for daily pattern (24 hours)
        if len(data) >= 48:
            daily_pattern = []
            for i in range(24):
                hour_values = [data[j] for j in range(i, len(data), 24)]
                if hour_values:
                    daily_pattern.append(np.mean(hour_values))
            
            # Check if pattern variance is significant
            pattern_variance = np.var(daily_pattern)
            data_variance = np.var(data)
            
            if pattern_variance > data_variance * 0.1:
                return {
                    "is_seasonal": True,
                    "period": 24,
                    "pattern": daily_pattern,
                    "strength": float(pattern_variance / data_variance),
                }
        
        return {"is_seasonal": False}
    
    def _detect_change_points(self, data: List[float]) -> List[Dict[str, Any]]:
        """Detect significant change points in time series."""
        change_points = []
        
        if len(data) < 10:
            return change_points
        
        # Simple change point detection using rolling statistics
        window_size = max(5, len(data) // 20)
        
        for i in range(window_size, len(data) - window_size):
            before = data[i-window_size:i]
            after = data[i:i+window_size]
            
            # Test for significant mean change
            mean_before = np.mean(before)
            mean_after = np.mean(after)
            std_before = np.std(before)
            
            if std_before > 0:
                z_score = abs(mean_after - mean_before) / std_before
                
                if z_score > 3:
                    change_points.append({
                        "index": i,
                        "magnitude": float(mean_after - mean_before),
                        "type": "mean_shift",
                        "z_score": float(z_score),
                    })
        
        return change_points
    
    def _simple_forecast(self, data: List[float], horizon: int) -> List[float]:
        """Simple linear forecast."""
        if len(data) < 2:
            return [data[-1] if data else 0] * horizon
        
        # Linear extrapolation
        x = np.arange(len(data))
        y = np.array(data)
        slope, intercept = np.polyfit(x, y, 1)
        
        # Generate forecast
        forecast = []
        for i in range(horizon):
            forecast_value = slope * (len(data) + i) + intercept
            forecast.append(float(max(0, forecast_value)))  # Ensure non-negative
        
        return forecast
    
    def _calculate_forecast_ci(self, historical: List[float], forecast: List[float]) -> Dict[str, List[float]]:
        """Calculate confidence interval for forecast."""
        # Simple CI based on historical variance
        std = np.std(historical) if len(historical) > 1 else 0
        
        return {
            "lower": [max(0, f - 2*std) for f in forecast],
            "upper": [f + 2*std for f in forecast],
        }
    
    def _compare_metric_values(self, values: Dict[str, Any], comparison_type: str) -> Dict[str, Any]:
        """Compare metric values across configurations."""
        comparison = {
            "best": None,
            "worst": None,
            "ranking": {},
            "differences": {},
        }
        
        # Convert to comparable format
        comparable_values = {}
        for config_id, value in values.items():
            if isinstance(value, list):
                comparable_values[config_id] = np.mean(value)
            elif isinstance(value, dict):
                comparable_values[config_id] = value.get("mean", value.get("value", 0))
            else:
                comparable_values[config_id] = float(value)
        
        # Rank configurations
        sorted_configs = sorted(comparable_values.items(), key=lambda x: x[1], reverse=True)
        
        comparison["best"] = sorted_configs[0][0] if sorted_configs else None
        comparison["worst"] = sorted_configs[-1][0] if sorted_configs else None
        
        for rank, (config_id, value) in enumerate(sorted_configs):
            comparison["ranking"][config_id] = rank + 1
        
        # Calculate differences
        if comparison_type == "relative" and comparison["worst"]:
            worst_value = comparable_values[comparison["worst"]]
            for config_id, value in comparable_values.items():
                if worst_value != 0:
                    comparison["differences"][config_id] = ((value - worst_value) / worst_value) * 100
                else:
                    comparison["differences"][config_id] = 0
        
        return comparison
    
    def _test_significance(self, metric_values: Dict[str, List[float]]) -> Dict[str, Any]:
        """Test statistical significance of differences."""
        significance_results = {
            "method": "t-test",
            "pairs": {},
        }
        
        config_ids = list(metric_values.keys())
        
        for i, config1 in enumerate(config_ids):
            for config2 in config_ids[i+1:]:
                values1 = metric_values[config1]
                values2 = metric_values[config2]
                
                if len(values1) >= 5 and len(values2) >= 5:
                    # Perform t-test
                    t_stat, p_value = stats.ttest_ind(values1, values2)
                    
                    pair_key = f"{config1}_vs_{config2}"
                    significance_results["pairs"][pair_key] = {
                        "t_statistic": float(t_stat),
                        "p_value": float(p_value),
                        "significant": p_value < 0.05,
                        "confidence": 1 - p_value,
                    }
        
        return significance_results
    
    def _identify_trade_off(self, metric1_comparison: Dict, metric2_comparison: Dict) -> Optional[Dict]:
        """Identify trade-offs between metrics."""
        if not metric1_comparison.get("ranking") or not metric2_comparison.get("ranking"):
            return None
        
        # Check if rankings are inversely correlated
        configs = set(metric1_comparison["ranking"].keys()) & set(metric2_comparison["ranking"].keys())
        
        if len(configs) < 2:
            return None
        
        # Calculate rank correlation
        ranks1 = [metric1_comparison["ranking"][c] for c in configs]
        ranks2 = [metric2_comparison["ranking"][c] for c in configs]
        
        if len(set(ranks1)) > 1 and len(set(ranks2)) > 1:
            correlation = np.corrcoef(ranks1, ranks2)[0, 1]
            
            if correlation < -0.5:  # Negative correlation indicates trade-off
                return {
                    "type": "inverse_relationship",
                    "metrics": ["metric1", "metric2"],  # Would use actual metric names
                    "correlation": float(correlation),
                    "description": "Improving one metric tends to worsen the other",
                }
        
        return None
    
    def _generate_comparison_recommendations(self, comparison: Dict) -> List[Dict]:
        """Generate recommendations based on configuration comparison."""
        recommendations = []
        
        # Best configuration recommendation
        if comparison.get("best_configuration"):
            recommendations.append({
                "priority": "high",
                "title": "Deploy optimal configuration",
                "description": f"Configuration '{comparison['best_configuration']['id']}' shows best overall performance",
                "actions": [
                    "Validate in production-like environment",
                    "Create rollback plan",
                    "Monitor performance metrics closely",
                ],
            })
        
        # Trade-off recommendations
        for trade_off in comparison.get("trade_offs", []):
            recommendations.append({
                "priority": "medium",
                "title": "Consider trade-off implications",
                "description": trade_off["description"],
                "actions": [
                    "Define priority between conflicting metrics",
                    "Set acceptable thresholds for each metric",
                    "Consider workload-specific configurations",
                ],
            })
        
        return recommendations