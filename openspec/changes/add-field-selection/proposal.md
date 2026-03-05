# Proposal: Add Field Selection Feature

## Intent
Add the ability for users to selectively choose which fields to fetch and save from scraped data. Currently, the scraper fetches all available fields (id, name, price, shop_name, description, image_url, valid_from, valid_to, etc.) but users often only need a subset of these fields for their specific use cases. This feature will reduce data transfer, storage usage, and processing time by allowing users to specify exactly which fields they want to include in the output.

## Scope

**In scope:**
- Add `--fields` CLI option to accept comma-separated list of field names
- Support field filtering for all entity types (shops, leaflets, offers)
- Validate field names against available fields for each entity type
- Apply field filtering before saving to JSON (reduce file size)
- Apply field filtering to terminal output (cleaner display)
- Maintain backward compatibility (all fields included by default)
- Provide helpful error messages for invalid field names

**Out of scope:**
- Field renaming or aliasing
- Nested field selection (e.g., shop.name)
- Field transformations or formatting
- Filtering based on field values (different feature)
- Wildcard patterns for field selection

## Approach
Implement field selection at the data export layer by filtering entity dictionaries before serialization. Add a `--fields` argument to all CLI commands that produce output, accepting a comma-separated list. Validate field names against a defined schema for each entity type. The filtering will be applied consistently across both terminal display and file export to ensure predictable behavior.
