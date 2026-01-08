# Lakeflow CatAPI Community Connector

This documentation describes how to configure and use the **CatAPI** Lakeflow community connector to ingest data from The Cat API into Databricks.

## Prerequisites

- **The Cat API account**: You need to sign up for a free account at https://thecatapi.com/ to obtain an API key.
- **API Key**: 
  - Must be created at https://thecatapi.com/ and supplied to the connector as the `api_key` option.
  - Free tier accounts are available with basic rate limits.
- **Network access**: The environment running the connector must be able to reach `https://api.thecatapi.com`.
- **Lakeflow / Databricks environment**: A workspace where you can register a Lakeflow community connector and run ingestion pipelines.

## Setup

### Required Connection Parameters

Provide the following **connection-level** options when configuring the connector:

| Name      | Type   | Required | Description                                                                                 | Example                            |
|-----------|--------|----------|---------------------------------------------------------------------------------------------|------------------------------------|
| `api_key` | string | yes      | The Cat API key used for authentication.                                                    | `live_abc123...`                   |
| `base_url`| string | no       | Base URL for The Cat API. Override if needed; otherwise defaults to `https://api.thecatapi.com/v1`. | `https://api.thecatapi.com/v1`     |
| `externalOptionsAllowList` | string | no | Comma-separated list of table-specific option names that are allowed to be passed through to the connector. This connector supports optional table-specific options, so this parameter is optional. | `limit,breed_id,category_ids,size,mime_types,has_breeds,order,sub_id` |

The full list of supported table-specific options for `externalOptionsAllowList` is:
`limit,breed_id,category_ids,size,mime_types,has_breeds,order,sub_id`

> **Note**: Table-specific options such as `limit`, `breed_id`, or `sub_id` are **not** connection parameters. They are provided per-table via table options in the pipeline specification. These option names must be included in `externalOptionsAllowList` for the connection to allow them.

### Obtaining the Required Parameters

- **The Cat API Key**:
  1. Sign up for a free account at https://thecatapi.com/
  2. Navigate to your account dashboard
  3. Generate an API key
  4. Copy the generated API key and store it securely. Use this as the `api_key` connection option.

### Create a Unity Catalog Connection

A Unity Catalog connection for this connector can be created in two ways via the UI:

1. Follow the **Lakeflow Community Connector** UI flow from the **Add Data** page.
2. Select any existing Lakeflow Community Connector connection for this source or create a new one.
3. Optionally set `externalOptionsAllowList` to `limit,breed_id,category_ids,size,mime_types,has_breeds,order,sub_id` if you want to use table-specific filtering options.

The connection can also be created using the standard Unity Catalog API.

## Supported Objects

The CatAPI connector exposes a **static list** of tables:

- `images`
- `breeds`
- `categories`
- `votes`
- `favourites`

### Object summary, primary keys, and ingestion mode

The connector defines the ingestion mode and primary key for each table:

| Table           | Description                                           | Ingestion Type | Primary Key                                           | Incremental Cursor (if any) |
|-----------------|-------------------------------------------------------|----------------|-------------------------------------------------------|------------------------------|
| `images`        | Cat images with metadata (breeds, categories)         | `snapshot`     | `id` (string)                                        | n/a                          |
| `breeds`        | Cat breed information (reference data)                | `snapshot`     | `id` (string)                                        | n/a                          |
| `categories`    | Image categories (reference data)                     | `snapshot`     | `id` (64-bit integer)                                 | n/a                          |
| `votes`         | User votes on images (requires authentication)       | `append`       | `id` (64-bit integer)                                | `created_at`                 |
| `favourites`    | User favourite images (requires authentication)       | `cdc`          | `id` (64-bit integer)                                 | `created_at`                 |

### Required and optional table options

Table-specific options are passed via the pipeline spec under `table` in `objects`. The available options per table are:

- **`images`**:
  - `limit` (integer, optional): Number of results per page (default: 100, max: 100).
  - `breed_id` (string, optional): Filter images by breed ID.
  - `category_ids` (string, optional): Comma-separated category IDs to filter by.
  - `size` (string, optional): Image size: `thumb`, `small`, `med`, `full` (default: `full`).
  - `mime_types` (string, optional): Comma-separated MIME types: `jpg`, `png`, `gif`.
  - `has_breeds` (integer, optional): Filter images with breed data: `0` (no breeds), `1` (has breeds) (default: `0`).
  - `order` (string, optional): Sort order: `RANDOM`, `ASC`, `DESC` (default: `ASC`).

- **`votes`**:
  - `limit` (integer, optional): Number of results per page (default: 100, max: 100).
  - `sub_id` (string, optional): Filter by user-submitted identifier.

- **`favourites`**:
  - `limit` (integer, optional): Number of results per page (default: 100, max: 100).
  - `sub_id` (string, optional): Filter by user-submitted identifier.

- **`breeds`** and **`categories`**: No table-specific options are required.

### Schema highlights

Full schemas are defined by the connector and align with The Cat API documentation:

- **`images`**:
  - Uses `id` as the primary key (string).
  - Includes nested `breeds` array (each breed contains nested `weight` struct).
  - Includes nested `categories` array.
  - Fields: `id`, `url`, `width`, `height`, `breeds`, `categories`, `sub_id`.

- **`breeds`**:
  - Uses `id` as the primary key (string).
  - Includes nested `weight` struct with `imperial` and `metric` fields.
  - Contains comprehensive breed information including temperament, life span, origin, and various trait scores (1-5 scale).

- **`categories`**:
  - Uses `id` as the primary key (64-bit integer).
  - Simple structure with `id` and `name` fields.

- **`votes`**:
  - Uses `id` as the primary key (64-bit integer).
  - Fields: `id`, `image_id`, `sub_id`, `created_at`, `value`, `country_code`.
  - `created_at` is used as the cursor field for incremental ingestion.

- **`favourites`**:
  - Uses `id` as the primary key (64-bit integer).
  - Includes nested `image` struct (full image object with breeds and categories).
  - Fields: `id`, `user_id`, `image_id`, `sub_id`, `created_at`, `image`.
  - `created_at` is used as the cursor field for incremental ingestion.

You usually do not need to customize the schema; it is static and driven by the connector implementation.

## Data Type Mapping

The Cat API JSON fields are mapped to logical types as follows (and then to Spark types in the implementation):

| Cat API JSON Type            | Example Fields                                | Connector Logical Type                  | Notes |
|-----------------------------|-----------------------------------------------|-----------------------------------------|-------|
| integer (64-bit)         | `id`, `width`, `height`, scores, flags           | 64-bit integer (`LongType`)             | All numeric fields are stored as `LongType` to avoid overflow. |
| string                      | `id`, `url`, `name`, `temperament`, `origin` | string (`StringType`)                 | Text fields, URLs, IDs. |
| ISO 8601 datetime (string)  | `created_at`      | string (`StringType`) | Stored as UTC strings; downstream processing can cast to timestamp. |
| object                      | `weight`, `breed`, `image` | struct (`StructType`) | Nested objects are preserved instead of flattened. |
| array                       | `breeds`, `categories`              | array of struct types      | Arrays are preserved as nested collections. |
| nullable fields             | `alt_names`, `wikipedia_url`, `breeds`, `categories` | same as base type + `null`             | Missing nested objects are surfaced as `null`, not `{}`. |

The connector is designed to:

- Prefer `LongType` for all numeric fields (IDs, dimensions, scores, flags).
- Preserve nested JSON structures instead of flattening them into separate tables.
- Treat absent nested fields as `None`/`null` to conform to Lakeflow's expectations.

## How to Run

### Step 1: Clone/Copy the Source Connector Code

Use the Lakeflow Community Connector UI to copy or reference the CatAPI connector source in your workspace. This will typically place the connector code (for example, `catapi.py`) under a project path that Lakeflow can load.

### Step 2: Configure Your Pipeline

In your pipeline code (e.g. `ingestion_pipeline.py` or a similar entrypoint), you will configure a `pipeline_spec` that references:

- A **Unity Catalog connection** that uses this CatAPI connector.
- One or more **tables** to ingest, each with optional `table_options`.

Example `pipeline_spec` snippet:

```json
{
  "pipeline_spec": {
    "connection_name": "catapi_connection",
    "object": [
      {
        "table": {
          "source_table": "images",
          "limit": 100,
          "has_breeds": 1,
          "size": "med",
          "mime_types": "jpg"
        }
      },
      {
        "table": {
          "source_table": "breeds"
        }
      },
      {
        "table": {
          "source_table": "categories"
        }
      },
      {
        "table": {
          "source_table": "votes",
          "limit": 100
        }
      },
      {
        "table": {
          "source_table": "favourites",
          "limit": 100
        }
      }
    ]
  }
}
```

- `connection_name` must point to the UC connection configured with your CatAPI `api_key` (and optional `base_url`).
- For each `table`:
  - `source_table` must be one of the supported table names listed above.
  - Table options such as `limit`, `breed_id`, `category_ids`, `size`, `mime_types`, `has_breeds`, `order`, and `sub_id` are passed directly to the connector and used to control how data is read.

### Step 3: Run and Schedule the Pipeline

Run the pipeline using your standard Lakeflow / Databricks orchestration (e.g., a scheduled job or workflow). For incremental tables (`votes` and `favourites`):

- On the **first run**, the connector will start from the beginning of available data.
- On **subsequent runs**, the connector uses the stored `cursor` (based on `created_at` for `cdc`/`append` tables) to pick up new records incrementally.

#### Best Practices

- **Start small**:
  - Begin with reference data tables (`breeds`, `categories`) to validate configuration and data shape.
  - Then move to `images` with appropriate filters to limit data volume.
- **Use appropriate filters**:
  - For `images`, use `has_breeds=1` if you only need images with breed information.
  - Use `size` parameter to control image URL sizes (smaller sizes reduce data transfer).
  - Use `mime_types` to filter specific image formats.
- **Respect rate limits**:
  - The Cat API enforces rate limits per API key; consider staggering syncs if you encounter rate limiting.
  - Free tier accounts typically have lower rate limits than paid accounts.
- **Handle pagination**:
  - The connector automatically handles pagination for `images`, `votes`, and `favourites`.
  - Use `limit` parameter to control page size (max 100 per request).

#### Troubleshooting

Common issues and how to address them:

- **Authentication failures (`401` / `403`)**:
  - Verify that the `api_key` is correct and not expired.
  - Ensure the API key is properly included in the connection configuration.
- **Rate limiting**:
  - Reduce request frequency or upgrade to a paid account tier.
  - Implement retry logic with exponential backoff if needed.
- **Empty results for `votes` or `favourites`**:
  - These tables require authentication and return data specific to the authenticated user's account.
  - Ensure you have created votes or favourites in your account if testing these tables.
- **Schema mismatches downstream**:
  - The connector uses nested structs extensively (e.g., `breeds` array, `weight` struct); ensure downstream tables are defined to accept nested types, or explicitly cast/flatten as needed in your transformations.

## References

- Connector implementation: `sources/catapi/catapi.py`
- Connector API documentation and schemas: `sources/catapi/catapi_api_doc.md`
- Official The Cat API documentation:
  - `https://docs.thecatapi.com/`
  - `https://thecatapi.com/`
  - `https://account.thecatapi.com/`

