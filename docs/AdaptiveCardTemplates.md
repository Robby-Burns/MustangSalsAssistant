# Microsoft Teams Adaptive Card Templates
*Version 1.0 - Generated per AgentSpec MVP*

| Template Name | Trigger | Target Input Schema | Note |
|---|---|---|---|
| **Quote Draft Card** | The Merchant pushes `QuoteDraft` | `{ "project_name": "str", "address": "str", "compliance": "list", "gross_margin": "float", "travel_sku": "str", "line_items": "list" }` | Unified view presented after an end-to-end execution pipeline. Includes human approval button. |
| **Edit Scope Interface** | User clicks `Edit Scope` | `{ "project_name": "str" }` | Modal card allowing quick-chips or free-form updates to the QuoteDraft scope. |
| **3-Day Nudge Card** | `Last_Activity_Date > 72h` | `{ "project_name": "str", "draft_preview": "str" }` | Proactive notification offering a drafted email from the CommTemplateEngine. |
| **Email Draft Card** | User requests comms | `{ "email_type": "str", "recipient": "str", "subject": "str", "body_preview": "str" }` | Previews outgoing intent messaging. Needs to be manually copied to clipboard! |
| **Address Block Card** | `GeoLockGuard` fails. | `{ "current_address": "str" }` | Displays required action required explicitly halting Auditor execution. |
| **No Recipe Alert** | `S3VectorFactory` returns 0 | `{ "project_type": "str" }` | Flags that the query is custom and needs manual baseline labor estimates. |
| **Margin Alert Card** | `QuoteDraft.Margin_Alert == True` | `{ "gross_margin": "float", "line_items": "list" }` | Shows the `⚠️` symbol indicating floor breach (<35%). Rep must sign to continue. |
| **API Fallback Card** | `ShopvoxFactory` hits 500 error | `{ "sandbox_cache_date": "str", "quote_data": "list" }` | Watermarks the entire document as `ESTIMATE ONLY` instructing manual pricing validation. |
