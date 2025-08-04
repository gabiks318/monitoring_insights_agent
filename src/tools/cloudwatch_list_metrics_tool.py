class CloudWatchListMetricsTool:
    name = "list_metrics"
    description = "List available CloudWatch metrics in a given namespace"
    inputs = {
        "namespace": {
            "type": "string",
            "description": "Namespace to list metrics from (e.g., AWS/EC2 or Custom)"
        },
        "metric_name": {
            "type": "string",
            "description": "Filter by metric name (optional)"
        },
        "dimensions": {
            "type": "array",
            "description": "Filter by dimensions (optional)",
            "items": {
                "type": "object",
                "properties": {
                    "Name": {"type": "string"},
                    "Value": {"type": "string"}
                }
            }
        },
        "region": {
            "type": "string",
            "description": "AWS region to query (default: ap-south-1)"
        }
    }
    output_type = "any"

    def __call__(
        self,
        namespace: str,
        metric_name: str = "",
        dimensions: list = [],
        region: str = "ap-south-1"
    ) -> list:
        import boto3

        cloudwatch = boto3.client("cloudwatch", region_name=region)

        kwargs = {"Namespace": namespace}
        if metric_name:
            kwargs["MetricName"] = metric_name
        if dimensions:
            kwargs["Dimensions"] = dimensions

        response = cloudwatch.list_metrics(**kwargs)
        return response.get("Metrics", [])

