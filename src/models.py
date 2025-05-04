import re
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
import json
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from constants import CORONA, BACNET


def to_camel_case(snake_str: str) -> str:
    """Converts snake_case to camelCase."""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def format_rdflib_literal(value: Any) -> Literal:
    """Formats a Python value as an RDFLib Literal with appropriate datatype."""
    if isinstance(value, bool):
        return Literal(value, datatype=XSD.boolean)
    elif isinstance(value, int):
        return Literal(value, datatype=XSD.integer)
    elif isinstance(value, float):
        return Literal(value, datatype=XSD.float)
    elif isinstance(value, datetime):
        return Literal(value.isoformat(timespec='seconds'), datatype=XSD.dateTime)
    elif isinstance(value, str):
        if value.startswith("http://") or value.startswith("https://") or ":" in value.split("://")[0]:
            try:
                return URIRef(value)
            except Exception:
                return Literal(value, datatype=XSD.string)
        else:
            return Literal(value, datatype=XSD.string)
    else:
        return Literal(str(value), datatype=XSD.string)

def to_prometheus_metric_name(metric_name: str, prefix: str = "bacnet") -> str:
    """Converts a camelCase or snake_case metric name to Prometheus snake_case format."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', metric_name)
    snake_case_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    # Add prefix and handle potential counter suffix
    if "requests" in snake_case_name or "responses" in snake_case_name or "count" in snake_case_name or "sent" in snake_case_name or "received" in snake_case_name or "total" in snake_case_name or "number" in snake_case_name:
         suffix = "_total"
    else:
         suffix = "" # Or determine gauge/other types if needed
    return f"{prefix}_{snake_case_name}{suffix}"

class BaseMetric(BaseModel):
    """Base model for all performance metrics."""
    metric_instance_uri: str = Field(..., description="Unique URI for this specific metric reading instance.")
    observed_from: Optional[str] = Field(None, description="Observer node (URI or identifier) where metrics were collected.")
    description: Optional[str] = Field(None, description="Detailed description of this metric instance.")
    metric_identifier: Optional[str] = Field(None, description="Unique identifier for this metric instance within the system.")
    metric_name: Optional[str] = Field(None, description="Human-readable name for this metric instance.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the metric observation.")
    # Common labels/tags that might apply to all metrics
    source_entity_uri: Optional[str] = Field(None, description="The URI of the entity (device, interface, application) the metric is about.")
    source_entity_address: Optional[str] = Field(None, description="Network address or other identifier for the source entity.")

    def _get_metric_fields(self) -> Dict[str, Any]:
        """Helper to get fields that represent actual metric values, excluding metadata."""
        exclude_fields = {'metric_instance_uri', 'observed_from', 'description', 'metric_identifier', 'metric_name', 'timestamp', 'source_entity_uri', 'source_entity_address'}
        return {k: v for k, v in self.model_dump(exclude_none=True).items() if k not in exclude_fields}

    def to_ttl(self) -> str:
        """Serializes the metric instance to Turtle (TTL) format using RDFLib."""
        g = Graph()
        # Bind namespaces for cleaner output
        g.bind("corona", CORONA)
        g.bind("bacnet", BACNET)
        g.bind("xsd", XSD)
        g.bind("rdf", RDF)
        g.bind("rdfs", RDFS)

        # Use the provided metric_instance_uri directly
        try:
            instance_uri = URIRef(self.metric_instance_uri)
        except Exception as e:
            raise ValueError(f"Invalid metric_instance_uri: {self.metric_instance_uri} - {e}")

        # Add type triple - Use the actual class name
        g.add((instance_uri, RDF.type, CORONA[self.__class__.__name__]))

        # Add common fields as triples
        if self.observed_from:
            observed_from_term = format_rdflib_literal(self.observed_from)
            g.add((instance_uri, CORONA.observedFrom, observed_from_term))
        if self.description:
            g.add((instance_uri, RDFS.comment, Literal(self.description)))
        if self.metric_identifier:
            g.add((instance_uri, CORONA['metric-identifier'], Literal(self.metric_identifier, datatype=XSD.string)))
        if self.metric_name:
            g.add((instance_uri, RDFS.label, Literal(self.metric_name)))
        if self.timestamp:
            g.add((instance_uri, CORONA.observedAt, format_rdflib_literal(self.timestamp)))
        if self.source_entity_uri:
            try:
                source_uri = URIRef(self.source_entity_uri)
                g.add((instance_uri, CORONA.metricSource, source_uri))
            except Exception as e:
                print(f"Warning: Could not create URIRef from source_entity_uri '{self.source_entity_uri}': {e}")
        elif self.source_entity_address:
            g.add((instance_uri, CORONA.sourceAddress, Literal(self.source_entity_address)))

        # Add specific metric value fields
        metric_fields = self._get_metric_fields()
        for field_name, value in metric_fields.items():
            if value is None:
                continue

            pydantic_field = self.model_fields.get(field_name)
            prop_name_camel = pydantic_field.alias if pydantic_field and pydantic_field.alias else to_camel_case(field_name)

            namespace = BACNET if "bacnet" in field_name.lower() or any(term in prop_name_camel.lower() for term in ["who", "cov", "bbmd", "readproperty", "iam", "ihave", "routed", "forwarded"]) else CORONA

            prop_uri = namespace[prop_name_camel]
            g.add((instance_uri, prop_uri, format_rdflib_literal(value)))

        ttl_output = g.serialize(format='turtle')
        return ttl_output

    def to_haystack_json(self) -> List[Dict[str, Any]]:
        """Serializes the metric to Project Haystack JSON format (simplified row)."""
        entity_ref = f"@{self.source_entity_uri}" if self.source_entity_uri else f"@addr_{self.source_entity_address}" if self.source_entity_address else "@unknown"
        metrics = []
        metric_fields = self._get_metric_fields()
        for field_name, value in metric_fields.items():
             pydantic_field = self.model_fields.get(field_name)
             metric_key = pydantic_field.alias if pydantic_field and pydantic_field.alias else to_camel_case(field_name)
             metrics.append({
                 "entity": entity_ref,
                 "metric": metric_key,
                 "val": value,
                 "ts": self.timestamp.isoformat(),
                 "observer": self.observed_from,
                 "metricId": self.metric_identifier,
             })
        return metrics

    def to_prometheus(self, prefix: str = "bacnet") -> List[str]:
        """Serializes the metric to Prometheus exposition format."""
        lines = []
        metric_fields = self._get_metric_fields()

        labels = {}
        if self.source_entity_uri:
            safe_uri = re.sub(r'[^a-zA-Z0-9_]', '_', self.source_entity_uri)
            labels["entity_uri"] = safe_uri
        if self.source_entity_address:
            labels["address"] = self.source_entity_address
        if self.observed_from:
            safe_observer = re.sub(r'[^a-zA-Z0-9_]', '_', self.observed_from)
            labels["observer"] = safe_observer
        if self.metric_identifier:
             labels["metric_id"] = self.metric_identifier

        label_str = ",".join([f'{k}="{v}"' for k, v in labels.items() if v])
        if label_str:
            label_str = f"{{{label_str}}}"
        else:
            label_str = ""

        for field_name, value in metric_fields.items():
            pydantic_field = self.model_fields.get(field_name)
            original_name = pydantic_field.alias if pydantic_field and pydantic_field.alias else to_camel_case(field_name)
            prom_metric_name = to_prometheus_metric_name(original_name, prefix)

            metric_type = "counter" if prom_metric_name.endswith("_total") else "gauge"
            field_description = pydantic_field.description if pydantic_field and pydantic_field.description else (self.description or original_name)
            sanitized_description = field_description.replace('\n', ' ').replace('\"', '\\"')
            lines.append(f"# HELP {prom_metric_name} {sanitized_description}")
            lines.append(f"# TYPE {prom_metric_name} {metric_type}")

            try:
                prom_value = float(value)
            except (ValueError, TypeError):
                prom_value = 0.0
                print(f"Warning: Could not convert value '{value}' for metric '{prom_metric_name}' to float. Setting to 0.")

            timestamp_ms = int(self.timestamp.timestamp() * 1000)
            lines.append(f"{prom_metric_name}{label_str} {prom_value} {timestamp_ms}")
            lines.append("")

        return lines

class BacnetApplicationMetric(BaseMetric):
    """Metrics related to BACnet application layer activity."""
    read_property_requests: Optional[int] = Field(None, alias="readPropertyRequests", description="Total number of ReadProperty requests sent.")
    read_property_responses: Optional[int] = Field(None, alias="readPropertyResponses", description="Total number of ReadProperty responses received.")
    who_is_requests_sent: Optional[int] = Field(None, alias="whoIsRequestsSent", description="Total number of Who-Is requests sent.")
    global_who_is_requests_sent: Optional[int] = Field(None, alias="globalWhoIsRequestsSent", description="Number of global Who-Is requests sent.")
    directed_who_is_requests_sent: Optional[int] = Field(None, alias="directedWhoIsRequestsSent", description="Number of directed Who-Is requests sent.")
    who_has_requests_sent: Optional[int] = Field(None, alias="whoHasRequestsSent", description="Total number of Who-Has requests sent.")
    global_who_has_requests_sent: Optional[int] = Field(None, alias="globalWhoHasRequestsSent", description="Number of global WhoHas requests sent.")
    directed_who_has_requests_sent: Optional[int] = Field(None, alias="directedWhoHasRequestsSent", description="Number of directed WhoHas requests sent.")
    i_am_responses_sent: Optional[int] = Field(None, alias="iAmResponsesSent", description="Total number of I-am responses sent.")
    i_am_responses_received: Optional[int] = Field(None, alias="iAmResponsesReceived", description="Total number of I-am responses received.")
    i_have_responses_sent: Optional[int] = Field(None, alias="iHaveResponsesSent", description="Total number of I-Have responses sent.")
    i_have_responses_received: Optional[int] = Field(None, alias="iHaveResponsesReceived", description="Total number of I-Have responses received.")
    total_bacnet_messages_sent: Optional[int] = Field(None, alias="totalBACnetMessagesSent", description="Total number of BACnet messages sent by this device.")
    total_bacnet_messages_received: Optional[int] = Field(None, alias="totalBACnetMessagesReceived", description="Total number of BACnet messages received by this device.")
    total_broadcasts_sent: Optional[int] = Field(None, alias="totalBroadcastsSent", description="Total number of broadcast messages (any type) sent by this device.")
    total_broadcasts_received: Optional[int] = Field(None, alias="totalBroadcastsReceived", description="Total number of broadcast messages (any type) received by this device.")

class COVNotificationMetric(BaseMetric):
    """Metrics related to BACnet COV Notifications."""
    unconfirmed_cov_notifications_sent: Optional[int] = Field(None, alias="unconfirmedCOVNotificationsSent", description="Total number of unconfirmed COV notifications sent.")
    confirmed_cov_notifications_sent: Optional[int] = Field(None, alias="confirmedCOVNotificationsSent", description="Total number of confirmed COV notifications sent.")
    unconfirmed_cov_notifications_received: Optional[int] = Field(None, alias="unconfirmedCOVNotificationsReceived", description="Total number of unconfirmed COV notifications received.")
    confirmed_cov_notifications_received: Optional[int] = Field(None, alias="confirmedCOVNotificationsReceived", description="Total number of confirmed COV notifications received.")

class RouterBBMDMetric(BaseMetric):
    """Metrics related to BACnet Router and BBMD functions."""
    messages_routed: Optional[int] = Field(None, alias="messagesRouted", description="Total number of messages routed by this device acting as a router.")
    messages_forwarded: Optional[int] = Field(None, alias="messagesForwarded", description="Total number of messages forwarded by this device acting as a BBMD.")
    routed_messages_sent: Optional[int] = Field(None, alias="routedMessagesSent", description="Total number of messages routed and sent to other networks.")
    routed_messages_received: Optional[int] = Field(None, alias="routedMessagesReceived", description="Total number of messages received that were routed from other networks.")
    routed_via: Optional[str] = Field(None, description="Identifier (URI) of the router/gateway device.")
    routed_devices_seen: Optional[int] = Field(None, alias="routedDevicesSeen", description="Number of unique devices on other networks seen through routing.")
    bbmd_entries_count: Optional[int] = Field(None, alias="bbmdEntriesCount", description="Number of entries in the BBMD table.")
    foreign_device_registrations: Optional[int] = Field(None, alias="foreignDeviceRegistrations", description="Number of currently registered foreign devices.")

if __name__ == '__main__':
    metric_instance = BacnetApplicationMetric(
        metric_instance_uri="http://example.com/metricInstance/bacnetApp/dev1/1714758900",
        source_entity_uri="http://example.com/device/bacnetDevice1",
        source_entity_address="192.168.1.100",
        observed_from="http://example.com/observer/captureAgent1",
        description="BACnet application metrics for Device 1",
        metric_identifier="bacnet_app_dev1",
        metric_name="BACnet App Stats (Dev1)",
        timestamp=datetime.now(),
        readPropertyRequests=150,
        readPropertyResponses=148,
        who_is_requests_sent=10,
        global_who_is_requests_sent=8,
        directed_who_is_requests_sent=2,
        i_am_responses_received=5,
        total_bacnet_messages_sent=200,
        total_broadcasts_received=15
    )

    print("--- TTL Output (RDFLib) ---")
    print(metric_instance.to_ttl())
    print("\n--- Haystack JSON Output ---")
    print(json.dumps(metric_instance.to_haystack_json(), indent=2))
    print("\n--- Prometheus Output ---")
    print("\n".join(metric_instance.to_prometheus()))

    cov_metric = COVNotificationMetric(
         metric_instance_uri="http://example.com/metricInstance/cov/dev2/1714759900",
         source_entity_uri="http://example.com/device/bacnetDevice2",
         source_entity_address="192.168.1.101",
         timestamp=datetime.now(),
         unconfirmed_cov_notifications_sent=500,
         confirmed_cov_notifications_received=20
    )
    print("\n--- COV Metric (Prometheus) ---")
    print("\n".join(cov_metric.to_prometheus(prefix="bacnet_cov")))

    router_metric = RouterBBMDMetric(
        metric_instance_uri="http://example.com/metricInstance/router/gw1/1714760000",
        source_entity_uri="http://example.com/device/gateway1",
        source_entity_address="10.0.0.1",
        timestamp=datetime.now(),
        messages_routed=10000,
        messages_forwarded=500,
        routed_devices_seen=25,
        bbmd_entries_count=10
    )
    print("\n--- Router/BBMD Metric (TTL with RDFLib) ---")
    print(router_metric.to_ttl())
