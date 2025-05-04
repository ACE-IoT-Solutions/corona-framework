\
from datetime import datetime
from typing import List
from models import BaseMetric, BacnetApplicationMetric, COVNotificationMetric, RouterBBMDMetric

def generate_sample_bacnet_app_metric() -> BacnetApplicationMetric:
    """Generates a sample BacnetApplicationMetric instance."""
    return BacnetApplicationMetric(
        metric_instance_uri="http://example.com/metricInstance/bacnetApp/devDemo/1715000000",
        source_entity_uri="http://example.com/device/bacnetDeviceDemo",
        source_entity_address="192.168.1.200",
        observed_from="http://example.com/observer/demoAgent",
        description="Sample BACnet application metrics for Demo Device",
        metric_identifier="bacnet_app_demo",
        metric_name="BACnet App Stats (Demo)",
        timestamp=datetime.now(),
        readPropertyRequests=250,
        readPropertyResponses=245,
        who_is_requests_sent=15,
        global_who_is_requests_sent=10,
        directed_who_is_requests_sent=5,
        i_am_responses_received=8,
        total_bacnet_messages_sent=300,
        total_broadcasts_received=25
    )

def generate_sample_cov_metric() -> COVNotificationMetric:
    """Generates a sample COVNotificationMetric instance."""
    return COVNotificationMetric(
         metric_instance_uri="http://example.com/metricInstance/cov/devDemo/1715000100",
         source_entity_uri="http://example.com/device/bacnetDeviceDemo",
         source_entity_address="192.168.1.200",
         observed_from="http://example.com/observer/demoAgent",
         description="Sample COV metrics for Demo Device",
         metric_identifier="cov_demo",
         metric_name="COV Stats (Demo)",
         timestamp=datetime.now(),
         unconfirmed_cov_notifications_sent=600,
         confirmed_cov_notifications_received=30
    )

def generate_sample_router_metric() -> RouterBBMDMetric:
    """Generates a sample RouterBBMDMetric instance."""
    return RouterBBMDMetric(
        metric_instance_uri="http://example.com/metricInstance/router/gwDemo/1715000200",
        source_entity_uri="http://example.com/device/gatewayDemo",
        source_entity_address="10.0.0.2",
        observed_from="http://example.com/observer/demoAgent",
        description="Sample Router/BBMD metrics for Demo Gateway",
        metric_identifier="router_demo",
        metric_name="Router/BBMD Stats (Demo)",
        timestamp=datetime.now(),
        messages_routed=15000,
        messages_forwarded=750,
        routed_devices_seen=30,
        bbmd_entries_count=12
    )

def generate_all_sample_metrics() -> List[BaseMetric]:
    """Generates a list containing one of each sample metric type."""
    return [
        generate_sample_bacnet_app_metric(),
        generate_sample_cov_metric(),
        generate_sample_router_metric(),
    ]
