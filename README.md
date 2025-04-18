# OT Performance Metrics ("Corona") Standard - Draft

**Current Date:** Friday, April 18, 2025


**(Working Title Note: The name "Corona" is used here as per initial discussion, but a different name might be preferable for a formal standard due to potential external associations.)**

## Introduction

This repository contains draft specifications for "Corona", a proposed standard for defining Operational Technology (OT) network and application performance metrics in a protocol-agnostic manner. The goal is to provide clear, reusable semantic definitions for common performance indicators found in industrial control systems and building automation.

This standard aims to:

* Define metrics like traffic counters, latency, error rates, and utilization using semantic web technologies (RDFS).
* Provide validation rules and constraints for data conforming to these metric definitions using SHACL.
* Facilitate interoperability and consistent interpretation of performance data across different OT protocols and platforms.
* Demonstrate seamless integration with existing standards, specifically the BACnet RDF representation proposed in ASHRAE Standard 135-2024 Addendum ct[cite: 1].

## Contents

This repository (conceptually) contains the following components:

1.  **`corona-ontology.ttl`**:
    * RDFS definitions for Corona metric classes (e.g., `NetworkInterfaceMetric`, `ApplicationMetric`) and properties (e.g., `bytesReceived`, `readCommandLatency`, `requestSuccessPercentage`).
    * Provides the core semantic meaning for each metric.

2.  **`corona-shapes.ttl`**:
    * SHACL Node Shapes (e.g., `NetworkInterfaceShape`, `ApplicationMetricShape`) defining constraints for RDF data graphs reporting Corona metrics.
    * Specifies rules like data types (`xsd:unsignedLong`, `xsd:float`), cardinality (min/max count), and value ranges.

3.  **`examples/bacnet-integration.ttl`**:
    * Illustrative RDF examples demonstrating how BACnet devices/objects, represented using the RDF syntax from Addendum ct[cite: 1], can report metrics using the Corona standard definitions.
    * Shows how Corona properties can be directly instantiated or mapped from BACnet-specific properties.
    * Includes example instances that can be validated against `corona-shapes.ttl`.

4.  **`README.md`**:
    * This file.

## New Metrics

The following new metrics have been added to the Corona standard to support BACnet-specific application performance monitoring:

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

5. **`iAmResponsesReceived`**:
   * **Description:** Total number of `I-am` responses received.
   * **Domain:** `ApplicationMetric`
   * **Range:** `xsd:unsignedLong`

## Usage & Integration

* **Defining Metrics:** Use the URIs defined in `corona-ontology.ttl` (e.g., `corona:bytesReceived`) as stable identifiers when referring to these specific metrics in documentation, APIs, or data models.
* **Validating Data:** Use the SHACL shapes in `corona-shapes.ttl` with a SHACL-compliant validation tool to check if RDF data correctly represents Corona metrics according to the defined constraints.
* **BACnet Integration:** The examples show how RDF data generated from BACnet systems (following Addendum ct [cite: 1]) can incorporate Corona metric reporting. Systems can either:
    * Directly use `corona:` properties for metrics.
    * Map existing or vendor-specific BACnet properties to `corona:` properties using `rdfs:subPropertyOf` or `owl:sameAs` (if OWL is used).
    * Ensure generated RDF instances are declared with appropriate `corona:` classes (e.g., `corona:NetworkInterfaceMetric`) to be targeted by the SHACL shapes.

## Status

**DRAFT / PROPOSAL:** The specifications contained herein are conceptual drafts and do not represent an official standard. They are intended for discussion, experimentation, and refinement.

## Contributing & Feedback

This is currently a conceptual exploration. Feedback, suggestions for improvement, additional metric definitions, and use cases are welcome. Please open an issue in the repository tracker (if applicable) for discussion.