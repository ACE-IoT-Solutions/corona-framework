# OT Performance Metrics ("Corona") Standard - Draft

[![Python Tests](https://github.com/ACE-IoT-Solutions/corona-framework/actions/workflows/python-test.yml/badge.svg)](https://github.com/ACE-IoT-Solutions/corona-framework/actions/workflows/python-test.yml)

**(Working Title Note: The name "Corona" is used here as per initial discussion, but a different name might be preferable for a formal standard due to potential external associations.)**

## Introduction

This repository contains draft specifications for "Corona", a proposed standard for defining Operational Technology (OT) network and application performance metrics in a protocol-agnostic manner. The goal is to provide clear, reusable semantic definitions for common performance indicators found in industrial control systems and building automation.

This standard aims to:

*   Define metrics like traffic counters, latency, error rates, and utilization using semantic web technologies (RDFS).
*   Provide validation rules and constraints for data conforming to these metric definitions using SHACL.
*   Facilitate interoperability and consistent interpretation of performance data across different OT protocols and platforms.
*   Demonstrate seamless integration with existing standards, specifically the BACnet RDF representation proposed in ASHRAE Standard 135-2024 Addendum ct[cite: 1].
*   Integrate with network topology models for contextualizing metrics.

## Related Projects

This standard is designed to work in conjunction with other related efforts:

*   **[corona-network-standard](../corona-network-standard/README.md):** Defines the RDFS/SHACL model for representing network topology (Nodes, Interfaces, Links, Subnets, VLANs). `corona-standard` metrics use the `observedFrom` property to link to specific `net:HWNetEntity` instances (like `net:Node` or `net:Iface`) defined in this network model, providing context for where the metrics were observed.
*   **[corona-pcap-processor](../corona-pcap-processor/README.md):** An example implementation that processes PCAP network capture files (specifically focusing on BACnet traffic), extracts relevant performance data, and generates RDF metrics conforming to the `corona-standard` definitions and Pydantic models.

## Contents

This repository (conceptually) contains the following components:

1.  **`data/corona-ontology.ttl`**:
    *   RDFS definitions for Corona metric classes (e.g., `NetworkInterfaceMetric`, `ApplicationMetric`) and properties (e.g., `bytesReceived`, `readCommandLatency`, `requestSuccessPercentage`).
    *   Provides the core semantic meaning for each metric.
    *   References classes from `corona-network-standard` (e.g., `net:HWNetEntity` as the range for `corona:observedFrom`).

2.  **`data/corona-shapes.ttl`**:
    *   SHACL Node Shapes (e.g., `NetworkInterfaceShape`, `ApplicationMetricShape`) defining constraints for RDF data graphs reporting Corona metrics.
    *   Specifies rules like data types (`xsd:unsignedLong`, `xsd:float`), cardinality (min/max count), and value ranges.
    *   Validates links to network entities (e.g., ensuring `corona:observedFrom` points to a valid `net:HWNetEntity`).

3.  **`src/models.py`**:
    *   Pydantic models mirroring the RDFS/SHACL definitions, providing a Pythonic way to create and validate metric data.
    *   Includes methods (`to_ttl`, `to_prometheus`, `to_haystack_json`) for serializing metric instances into various output formats.

4.  **`examples/`**:
    *   Illustrative RDF examples demonstrating how systems (e.g., BACnet) can report metrics using the Corona standard definitions.

5.  **`README.md`**: 
    *   This file.

## Properties and Metrics

### General Metric Properties

1. **`observedFrom`**:
   * **Description:** Specifies the observer node in the network where these metrics were collected or calculated. This is the monitoring point (capture device, analyzer, or network tap) rather than the device about which the metrics were observed.
   * **Domain:** `PerformanceMetric`
   * **Range:** `rdfs:Resource`

2. **`description`**:
   * **Description:** Provides a detailed description of this metric instance, including context about how it was collected or calculated.
   * **Domain:** `PerformanceMetric`
   * **Range:** `xsd:string`

3. **`metric-identifier`**:
   * **Description:** A unique identifier for this specific metric instance to distinguish it from other similar metric instances in the same system.
   * **Domain:** `PerformanceMetric`
   * **Range:** `xsd:string`

4. **`metric-name`**:
   * **Description:** A human-readable name for this metric instance that can be used for display purposes.
   * **Domain:** `PerformanceMetric`
   * **Range:** `xsd:string`

### BACnet-Specific Application Metrics

1. **`readPropertyRequests`**:
   * **Description:** Total number of `ReadProperty` requests sent.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

2. **`readPropertyResponses`**:
   * **Description:** Total number of `ReadProperty` responses received.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

3. **`totalProperties`**:
   * **Description:** Total number of properties available in the BACnet object.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

4. **`whoIsRequestsSent`**:
   * **Description:** Total number of `Who-Is` requests sent.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

5. **`globalWhoIsRequestsSent`**:
   * **Description:** Number of global `Who-Is` requests sent.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

6. **`directedWhoIsRequestsSent`**:
   * **Description:** Number of directed `Who-Is` requests sent.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

7. **`globalWhoHasRequestsSent`**:
   * **Description:** Number of global `WhoHas` requests sent.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

8. **`directedWhoHasRequestsSent`**:
   * **Description:** Number of directed `WhoHas` requests sent.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

9. **`iAmResponsesSent`**:
   * **Description:** Total number of `I-am` responses sent.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

10. **`iAmResponsesReceived`**:
    * **Description:** Total number of `I-am` responses received.
    * **Domain:** `ApplicationMetric`
    * **Range:** `xsd:unsignedLong`

11. **`globalBroadcastMessageCount`**:
    * **Description:** Total number of global broadcast messages sent or received.
    * **Domain:** `ApplicationMetric`
    * **Range:** `xsd:unsignedLong`

12. **`totalBacnetMessagesSent`**:
    * **Description:** Total number of BACnet messages sent by this device.
    * **Domain:** `ApplicationMetric`
    * **Range:** `xsd:unsignedLong`

13. **`totalBroadcastsSent`**:
    * **Description:** Total number of broadcast messages (any type) sent by this device.
    * **Domain:** `ApplicationMetric`
    * **Range:** `xsd:unsignedLong`

### COV Notification Metrics

1. **`unconfirmedCOVNotificationsSent`**:
   * **Description:** Total number of unconfirmed COV notifications sent.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

2. **`confirmedCOVNotificationsSent`**:
   * **Description:** Total number of confirmed COV notifications sent.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

3. **`unconfirmedCOVNotificationsReceived`**:
   * **Description:** Total number of unconfirmed COV notifications received.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

4. **`confirmedCOVNotificationsReceived`**:
   * **Description:** Total number of confirmed COV notifications received.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

### Router and BBMD Metrics

1. **`messagesRouted`**:
   * **Description:** Total number of messages routed by this device acting as a router.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

2. **`messagesForwarded`**:
   * **Description:** Total number of messages forwarded by this device acting as a BBMD.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

3. **`routedMessagesSent`**:
   * **Description:** Total number of messages routed and sent to other networks.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

4. **`routedMessagesReceived`**:
   * **Description:** Total number of messages received that were routed from other networks.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

5. **`routedVia`**:
   * **Description:** Identifies the router or gateway device through which this message was routed.
   * **Domain:** `ApplicationMetric`
   * **Range:** `rdfs:Resource`

6. **`routedDevicesSeen`**:
   * **Description:** Number of unique devices on other networks that have been seen through routing.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

## Usage & Integration

* **Defining Metrics:** Use the URIs defined in `corona-ontology.ttl` (e.g., `corona:bytesReceived`) as stable identifiers when referring to these specific metrics in documentation, APIs, or data models.
* **Validating Data:** Use the SHACL shapes in `corona-shapes.ttl` with a SHACL-compliant validation tool to check if RDF data correctly represents Corona metrics according to the defined constraints.
* **BACnet Integration:** The examples show how RDF data generated from BACnet systems (following Addendum ct [cite: 1]) can incorporate Corona metric reporting. Systems can either:
    * Directly use `corona:` properties for metrics.
    * Map existing or vendor-specific BACnet properties to `corona:` properties using `rdfs:subPropertyOf` or `owl:sameAs` (if OWL is used).
    * Ensure generated RDF instances are declared with appropriate `corona:` classes (e.g., `corona:NetworkInterfaceMetric`) to be targeted by the SHACL shapes.

## Output Formats

The Corona standard supports multiple output formats to facilitate integration with different systems and tools:

### 1. TTL (Turtle) Format

The primary representation format using RDF semantic web technologies:
- Uses subject-predicate-object triples
- Organizes metrics with namespaces: `corona:` and `bacnet:`
- Links devices and interfaces with relationship predicates
- Example: `ex:addr_10.21.52.5 corona:globalWhoIsRequestsSent "8"^^xsd:unsignedLong`

### 2. Project Haystack Formats

#### JSON Format
- Row-based representation with metadata in header
- Column-based representation with type information
- One row per (entity, metric) combination
- Example: `{"metric":"globalWhoIsRequestsSent", "val":8, "entity":"@addr_10.21.52.5"}`

#### Zinc Format
- Compact representation of the JSON format
- Brief headers and row-based data
- Uses `@id` refs and marker syntax
- Example: `@addr_10.21.52.5 ... metric:"globalWhoIsRequestsSent" val:8`

### 3. Prometheus Exposition Format

Text-based format following OpenTelemetry conventions:
- Metric name + labels pattern
- Type and help metadata as comments
- Counter metrics with `_total` suffix
- Example: `bacnet_global_whois_requests_total{device_id="",address="10.21.52.5"} 8`

### Format Mapping

Metrics maintain consistent semantic meaning across formats with format-specific naming conventions:

| TTL (Corona) | Prometheus | Haystack (JSON/Zinc) |
|--------------|------------|----------------------|
| corona:globalWhoIsRequestsSent | bacnet_global_whois_requests_total | metric:"globalWhoIsRequestsSent" |
| corona:packetsReceived | bacnet_packets_total | metric:"packetsReceived" |
| corona:totalBacnetMessagesSent | bacnet_messages_sent_total | metric:"totalBacnetMessagesSent" |
| corona:messagesRouted | bacnet_messages_routed_total | metric:"messagesRouted" |

### Format Conversion Principles

When translating between formats, the following principles are maintained:
1. **Semantic equivalence**: Same metrics with different syntax
2. **Namespace mapping**: Corona/bacnet → bacnet_ prefix (Prometheus)
3. **Structure transformation**: Resource-centric (TTL) to row-based (Haystack) 
4. **Data type alignment**: XSD types (TTL) → native JSON types → text (Prometheus)

## Status

**DRAFT / PROPOSAL:** The specifications contained herein are conceptual drafts and do not represent an official standard. They are intended for discussion, experimentation, and refinement.

## Contributing & Feedback

This is currently a conceptual exploration. Feedback, suggestions for improvement, additional metric definitions, and use cases are welcome. Please open an issue in the repository tracker (if applicable) for discussion.