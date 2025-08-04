class CloudWatchGetMetricsTool:
    name = "cloudwatch_query"
    description = "Query CloudWatch metrics using metric name, namespace, dimensions, time range, period, and statistic."
    inputs = {
        "metric_name": {"type": "string", "description": "Metric name to query"},
        "namespace": {"type": "string", "description": "CloudWatch namespace"},
        "dimensions": {"type": "list", "description": "List of dimensions", "default": []},
        "start_time": {"type": "string", "description": "Start time (ISO)", "default": "2024-01-01T00:00:00Z"},
        "end_time": {"type": "string", "description": "End time (ISO)", "default": "2024-01-01T01:00:00Z"},
        "period": {"type": "integer", "description": "Period in seconds", "default": 300},
        "statistic": {"type": "string", "description": "Statistic type", "default": "Average"},
        "region": {"type": "string", "description": "AWS region to query (default: ap-south-1)", "default": "ap-south-1"}
    }
    output_type = "any"

    def __call__(
        self,
        metric_name: str,
        namespace: str,
        dimensions: list = [],
        start_time: str = "2024-01-01T00:00:00Z",
        end_time: str = "2024-01-01T01:00:00Z",
        period: int = 300,
        statistic: str = "Average",
        region: str = "ap-south-1"
    ):
        import boto3
        cloudwatch = boto3.client("cloudwatch", region_name=region)
        try:
            response = cloudwatch.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=[statistic],
            )
            return response.get("Datapoints", [])
        except Exception as e:
            return f"Error querying CloudWatch: {str(e)}"
