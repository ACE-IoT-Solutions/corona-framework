# Agentic Sessions

## 2024-05-02: Multi-Format Output Support

Added documentation and implementation for multiple output formats to enable integration with various systems:

1. **TTL (Turtle) Format**
   - Primary semantic representation following the Corona ontology
   - Uses subject-predicate-object triples with RDF semantics
   - Maintains full relationship context between metrics and devices

2. **Project Haystack Formats**
   - Added JSON format support with row-based representation
   - Added Zinc format as a compact alternative to JSON
   - Implemented consistent naming conventions between Corona and Haystack

3. **Prometheus Exposition Format**
   - Added support for OpenTelemetry-compatible text format
   - Implemented counter metrics with `_total` suffix
   - Added type and help metadata as comments

4. **Format Translation**
   - Created consistent mapping between all formats:
     - TTL → Prometheus (e.g., `corona:globalWhoIsRequestsSent` → `bacnet_global_whois_requests_total`)
     - TTL → Haystack (e.g., `corona:globalWhoIsRequestsSent` → `metric:"globalWhoIsRequestsSent"`)
   - Maintained semantic equivalence across formats
   - Implemented data type transformations (XSD → JSON → text)

5. **Sample Outputs**
   - Added sample files demonstrating all formats
   - Created documentation with format comparison
   - Added examples showing the same metrics in different formats

## 2024-04-29: Enhanced BACnet Metrics Framework

Added new metrics to the Corona framework:

1. **Global Broadcast Metrics**
   - Added `globalBroadcastMessageCount` to track all global broadcast messages
   - Added `totalBacnetMessagesSent` to track total BACnet messages
   - Added `totalBroadcastsSent` to track all broadcast messages

2. **Enhanced WhoIs/WhoHas Services**
   - Maintained existing division of WhoIs into global and directed
   - Added new WhoHas metrics (both global and directed variants)

3. **COV Notification Tracking**
   - Added metrics for unconfirmed COV notifications (sent/received)
   - Added metrics for confirmed COV notifications (sent/received)

4. **Router and BBMD Metrics**
   - Added `messagesRouted` for tracking router activity
   - Added `messagesForwarded` for tracking BBMD activity

5. **Validator Improvements**
   - Enhanced validator with specialized analysis functions:
     - `list_broadcast_metrics()`
     - `list_cov_metrics()`
     - `list_who_metrics()`
     - `list_message_count_metrics()`
     - `list_bbmd_metrics()`
   - Updated ontology analysis to report on all new metric types

All changes maintain backward compatibility with existing implementations while providing more granular tracking of BACnet protocol activities.

6. **Clarified `observedFrom` Property**
   - Enhanced documentation to clarify that `observedFrom` specifies the observer node (monitoring point) where metrics were collected or calculated
   - Updated SHACL shape descriptions to reflect this clarification
   - Made explicit that this is the device collecting the metrics, not necessarily the device being observed

7. **Added General Metric Properties**
   - Added `corona:description` for detailed metric instance descriptions
   - Added `corona:metric-identifier` for unique identification of specific metric instances
   - Added `corona:metric-name` for human-readable names for display purposes
   - Added validation rules with appropriate constraints
   - Enhanced validator with `list_general_metric_properties()` function
   - Updated example to demonstrate usage of these properties