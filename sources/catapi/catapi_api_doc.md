# **CatAPI API Documentation**

## **Authorization**

- **Chosen method**: API Key authentication via HTTP header.
- **Base URL**: `https://api.thecatapi.com/v1`
- **Auth placement**:
  - HTTP header: `x-api-key: <api_key>`
  - The API key is obtained by signing up at https://thecatapi.com/
  - API key is required for all requests (including public endpoints)
- **Other supported methods**: None. The Cat API only supports API key authentication.

Example authenticated request:

```bash
curl -X GET \
  -H "x-api-key: YOUR_API_KEY" \
  "https://api.thecatapi.com/v1/images/search?limit=1"
```

Notes:
- The `x-api-key` header must be included in all API requests.
- Rate limits vary based on account type (free tier typically has lower limits).
- Content-Type header is optional but can be set to `application/json` for consistency.

## **Object List**

The Cat API provides access to several types of objects. The object list is **static** (defined by the connector), not discovered dynamically from an API.

| Object Name | Description | Primary Endpoint | Ingestion Type |
|------------|-------------|------------------|----------------|
| `images` | Cat images with metadata | `GET /images/search` | `snapshot` |
| `breeds` | Cat breed information | `GET /breeds` | `snapshot` |
| `categories` | Image categories | `GET /categories` | `snapshot` |
| `votes` | User votes on images (requires auth) | `GET /votes` | `append` |
| `favourites` | User favourite images (requires auth) | `GET /favourites` | `cdc` |

**Connector scope for initial implementation**:
- Step 1 focuses on the `images` object and documents it in detail.
- Other objects are listed for future extension.

High-level notes on additional objects:
- **Breeds**: Static reference data about cat breeds. Can be retrieved once and refreshed periodically.
- **Categories**: Static list of image categories (e.g., "hats", "sunglasses", "boxes").
- **Votes**: User-submitted votes on images. Append-only stream of vote records.
- **Favourites**: User-saved favourite images. Supports create and delete operations, making it suitable for CDC-style ingestion.

## **Object Schema**

### General notes

- The Cat API returns JSON responses with consistent schemas.
- Nested JSON objects (e.g., `breeds` array within an image) are modeled as **nested structures** rather than being fully flattened.
- Schema information is derived from the API response structure and official documentation.

### `images` object (primary table)

**Source endpoint**:  
`GET /images/search`

**Key behavior**:
- Returns an array of image objects.
- Supports filtering via query parameters (breed_id, category_ids, size, mime_types, etc.).
- Supports pagination via `page` and `limit` parameters.
- Can return images with or without breed information based on `has_breeds` parameter.

**High-level schema (connector view)**:

Top-level fields (all from the Cat API unless marked as "connector-derived"):

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | string | Unique identifier for the image. Primary key. |
| `url` | string | URL to the image file. |
| `width` | integer (64-bit) | Image width in pixels. |
| `height` | integer (64-bit) | Image height in pixels. |
| `breeds` | array of struct | Array of breed objects associated with the image. Empty array if no breeds. |
| `categories` | array of struct | Array of category objects associated with the image. Empty array if no categories. |
| `sub_id` | string or null | User-submitted identifier (if provided when uploading). |

**Nested `breeds` struct schema** (within images):

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | string | Unique breed identifier. |
| `name` | string | Breed name. |
| `temperament` | string | Comma-separated list of temperament traits. |
| `life_span` | string | Typical life span range (e.g., "12 - 15"). |
| `alt_names` | string or null | Alternative names for the breed. |
| `wikipedia_url` | string or null | Wikipedia URL for the breed. |
| `origin` | string | Country/region of origin. |
| `weight` | struct | Weight range object with `imperial` and `metric` fields. |
| `cfa_url` | string or null | CFA (Cat Fanciers' Association) URL. |
| `vetstreet_url` | string or null | Vetstreet URL. |
| `vcahospitals_url` | string or null | VCA Hospitals URL. |
| `country_codes` | string | ISO country codes (e.g., "US,GB"). |
| `description` | string | Breed description. |
| `indoor` | integer or null | Indoor preference (0 or 1). |
| `lap` | integer or null | Lap cat preference (0 or 1). |
| `adaptability` | integer | Adaptability score (1-5). |
| `affection_level` | integer | Affection level score (1-5). |
| `child_friendly` | integer | Child-friendly score (1-5). |
| `dog_friendly` | integer | Dog-friendly score (1-5). |
| `energy_level` | integer | Energy level score (1-5). |
| `grooming` | integer | Grooming needs score (1-5). |
| `health_issues` | integer | Health issues score (1-5). |
| `intelligence` | integer | Intelligence score (1-5). |
| `shedding_level` | integer | Shedding level score (1-5). |
| `social_needs` | integer | Social needs score (1-5). |
| `stranger_friendly` | integer | Stranger-friendly score (1-5). |
| `vocalisation` | integer | Vocalisation score (1-5). |
| `experimental` | integer | Experimental breed flag (0 or 1). |
| `hairless` | integer | Hairless breed flag (0 or 1). |
| `natural` | integer | Natural breed flag (0 or 1). |
| `rare` | integer | Rare breed flag (0 or 1). |
| `rex` | integer | Rex breed flag (0 or 1). |
| `suppressed_tail` | integer | Suppressed tail flag (0 or 1). |
| `short_legs` | integer | Short legs flag (0 or 1). |
| `hypoallergenic` | integer | Hypoallergenic flag (0 or 1). |

**Nested `categories` struct schema** (within images):

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique category identifier. |
| `name` | string | Category name (e.g., "hats", "boxes"). |

**Nested `weight` struct schema** (within breeds):

| Column Name | Type | Description |
|------------|------|-------------|
| `imperial` | string | Weight range in imperial units (e.g., "7 - 10"). |
| `metric` | string | Weight range in metric units (e.g., "3 - 5"). |

Example API request:

```bash
curl -X GET \
  -H "x-api-key: YOUR_API_KEY" \
  "https://api.thecatapi.com/v1/images/search?limit=1&has_breeds=true&size=med&mime_types=jpg"
```

Example API response:

```json
[
  {
    "id": "MTY3ODc4OA",
    "url": "https://cdn2.thecatapi.com/images/MTY3ODc4OA.jpg",
    "width": 500,
    "height": 333,
    "breeds": [
      {
        "id": "abys",
        "name": "Abyssinian",
        "temperament": "Active, Energetic, Independent, Intelligent, Gentle",
        "life_span": "14 - 15",
        "alt_names": "",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Abyssinian_(cat)",
        "origin": "Egypt",
        "weight": {
          "imperial": "7  - 10",
          "metric": "3 - 5"
        },
        "cfa_url": "http://cfa.org/Breeds/BreedsAB/Abyssinian.aspx",
        "vetstreet_url": "http://www.vetstreet.com/cats/abyssinian",
        "vcahospitals_url": "https://vcahospitals.com/know-your-pet/cat-breeds/abyssinian",
        "country_codes": "EG",
        "description": "The Abyssinian is easy to care for, and a joy to have in your home. They're affectionate cats and love both people and other animals.",
        "indoor": 0,
        "lap": 1,
        "adaptability": 5,
        "affection_level": 5,
        "child_friendly": 3,
        "dog_friendly": 4,
        "energy_level": 5,
        "grooming": 1,
        "health_issues": 2,
        "intelligence": 5,
        "shedding_level": 2,
        "social_needs": 5,
        "stranger_friendly": 5,
        "vocalisation": 1,
        "experimental": 0,
        "hairless": 0,
        "natural": 1,
        "rare": 0,
        "rex": 0,
        "suppressed_tail": 0,
        "short_legs": 0,
        "hypoallergenic": 0
      }
    ],
    "categories": []
  }
]
```

### `breeds` object

**Source endpoint**:  
`GET /breeds`

**Key behavior**:
- Returns a complete list of all cat breeds.
- No pagination required (typically returns ~100 breeds).
- Each breed object contains comprehensive information about the breed.

**High-level schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | string | Unique breed identifier. Primary key. |
| `name` | string | Breed name. |
| `temperament` | string | Comma-separated list of temperament traits. |
| `life_span` | string | Typical life span range (e.g., "12 - 15"). |
| `alt_names` | string or null | Alternative names for the breed. |
| `wikipedia_url` | string or null | Wikipedia URL for the breed. |
| `origin` | string | Country/region of origin. |
| `weight` | struct | Weight range object with `imperial` and `metric` fields. |
| `cfa_url` | string or null | CFA (Cat Fanciers' Association) URL. |
| `vetstreet_url` | string or null | Vetstreet URL. |
| `vcahospitals_url` | string or null | VCA Hospitals URL. |
| `country_codes` | string | ISO country codes (e.g., "US,GB"). |
| `description` | string | Breed description. |
| `indoor` | integer or null | Indoor preference (0 or 1). |
| `lap` | integer or null | Lap cat preference (0 or 1). |
| `adaptability` | integer | Adaptability score (1-5). |
| `affection_level` | integer | Affection level score (1-5). |
| `child_friendly` | integer | Child-friendly score (1-5). |
| `dog_friendly` | integer | Dog-friendly score (1-5). |
| `energy_level` | integer | Energy level score (1-5). |
| `grooming` | integer | Grooming needs score (1-5). |
| `health_issues` | integer | Health issues score (1-5). |
| `intelligence` | integer | Intelligence score (1-5). |
| `shedding_level` | integer | Shedding level score (1-5). |
| `social_needs` | integer | Social needs score (1-5). |
| `stranger_friendly` | integer | Stranger-friendly score (1-5). |
| `vocalisation` | integer | Vocalisation score (1-5). |
| `experimental` | integer | Experimental breed flag (0 or 1). |
| `hairless` | integer | Hairless breed flag (0 or 1). |
| `natural` | integer | Natural breed flag (0 or 1). |
| `rare` | integer | Rare breed flag (0 or 1). |
| `rex` | integer | Rex breed flag (0 or 1). |
| `suppressed_tail` | integer | Suppressed tail flag (0 or 1). |
| `short_legs` | integer | Short legs flag (0 or 1). |
| `hypoallergenic` | integer | Hypoallergenic flag (0 or 1). |

Example API request:

```bash
curl -X GET \
  -H "x-api-key: YOUR_API_KEY" \
  "https://api.thecatapi.com/v1/breeds"
```

### `categories` object

**Source endpoint**:  
`GET /categories`

**Key behavior**:
- Returns a complete list of image categories.
- No pagination required (typically returns ~10 categories).
- Static reference data.

**High-level schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique category identifier. Primary key. |
| `name` | string | Category name (e.g., "hats", "boxes", "sunglasses"). |

Example API request:

```bash
curl -X GET \
  -H "x-api-key: YOUR_API_KEY" \
  "https://api.thecatapi.com/v1/categories"
```

Example API response:

```json
[
  {
    "id": 1,
    "name": "hats"
  },
  {
    "id": 14,
    "name": "boxes"
  },
  {
    "id": 7,
    "name": "ties"
  }
]
```

### `votes` object

**Source endpoint**:  
`GET /votes`

**Key behavior**:
- Returns votes submitted by the authenticated user.
- Requires authentication (API key).
- Supports pagination via `page` and `limit` parameters.
- Append-only stream (votes cannot be modified, only created).

**High-level schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique vote identifier. Primary key. |
| `image_id` | string | ID of the image that was voted on. |
| `sub_id` | string | User-submitted identifier. |
| `created_at` | string (ISO 8601 datetime) | When the vote was created. |
| `value` | integer | Vote value (typically 1 for upvote, 0 for downvote). |
| `country_code` | string | ISO country code of the voter. |

Example API request:

```bash
curl -X GET \
  -H "x-api-key: YOUR_API_KEY" \
  "https://api.thecatapi.com/v1/votes?limit=10"
```

### `favourites` object

**Source endpoint**:  
`GET /favourites`

**Key behavior**:
- Returns favourite images saved by the authenticated user.
- Requires authentication (API key).
- Supports pagination via `page` and `limit` parameters.
- Supports create (POST) and delete (DELETE) operations, making it suitable for CDC-style ingestion.

**High-level schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique favourite identifier. Primary key. |
| `user_id` | string | User identifier who created the favourite. |
| `image_id` | string | ID of the favourited image. |
| `sub_id` | string | User-submitted identifier. |
| `created_at` | string (ISO 8601 datetime) | When the favourite was created. |
| `image` | struct | Full image object (same structure as images object). |

Example API request:

```bash
curl -X GET \
  -H "x-api-key: YOUR_API_KEY" \
  "https://api.thecatapi.com/v1/favourites?limit=10"
```

## **Get Object Primary Keys**

Primary keys for objects are **static** and defined as follows:

| Object Name | Primary Key Column(s) |
|------------|----------------------|
| `images` | `id` (string) |
| `breeds` | `id` (string) |
| `categories` | `id` (integer) |
| `votes` | `id` (integer) |
| `favourites` | `id` (integer) |

There is no API endpoint to retrieve primary key information dynamically. The primary keys are derived from the API response structure where each object contains a unique `id` field.

## **Object's ingestion type**

| Object Name | Ingestion Type | Rationale |
|------------|----------------|-----------|
| `images` | `snapshot` | Images are added to the collection over time, but there's no reliable way to track incremental changes. The API doesn't provide timestamps for when images were added, and images can be removed from the collection. Full snapshot is the safest approach. |
| `breeds` | `snapshot` | Breed information is relatively static reference data. Changes are infrequent, so periodic full snapshots are appropriate. |
| `categories` | `snapshot` | Categories are static reference data that rarely change. |
| `votes` | `append` | Votes are append-only. Once created, they cannot be modified or deleted. New votes can be tracked using `created_at` timestamp. |
| `favourites` | `cdc` | Favourites can be created and deleted. The `created_at` timestamp can be used as a cursor for incremental reads, and deleted favourites can be detected by comparing current state with previous state. |

## **Read API for Data Retrieval**

### `images` object

**Endpoint**: `GET /images/search`

**Method**: GET

**Authentication**: Required (x-api-key header)

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Number of results to return (default: 1, max: 100). |
| `page` | integer | No | Page number for pagination (0-indexed). |
| `order` | string | No | Sort order: `RANDOM`, `ASC`, `DESC` (default: `RANDOM`). |
| `size` | string | No | Image size: `thumb`, `small`, `med`, `full` (default: `full`). |
| `mime_types` | string | No | Comma-separated MIME types: `jpg`, `png`, `gif` (default: all). |
| `format` | string | No | Response format: `json`, `src` (default: `json`). |
| `breed_id` | string | No | Filter by breed ID. |
| `category_ids` | string | No | Comma-separated category IDs to filter by. |
| `has_breeds` | integer | No | Filter images with breed data: `0` (no breeds), `1` (has breeds) (default: `0`). |

**Pagination**:
- Use `page` and `limit` parameters for pagination.
- `page` is 0-indexed (page 0 is the first page).
- Maximum `limit` is 100 per request.
- To retrieve all images, iterate through pages until an empty array is returned.

**Incremental Strategy**:
- The `images` object uses **snapshot** ingestion type.
- There is no reliable cursor field for incremental reads (images don't have `created_at` or `updated_at` timestamps).
- The API doesn't provide a way to filter images by date or track deletions.
- Full snapshot approach: retrieve all images by paginating through all pages.

**Example API request**:

```bash
curl -X GET \
  -H "x-api-key: YOUR_API_KEY" \
  "https://api.thecatapi.com/v1/images/search?limit=10&page=0&has_breeds=1&size=med&mime_types=jpg"
```

**Example API response**:

```json
[
  {
    "id": "MTY3ODc4OA",
    "url": "https://cdn2.thecatapi.com/images/MTY3ODc4OA.jpg",
    "width": 500,
    "height": 333,
    "breeds": [...],
    "categories": []
  }
]
```

**Extra parameters needed to read the table**:
- None required. All parameters are optional filters.

**Rate Limits**:
- Rate limits vary by account type (free tier typically has lower limits).
- TBD: Exact rate limit values need to be confirmed from official documentation.
- Recommended: Implement rate limiting with exponential backoff to respect API limits.

### `breeds` object

**Endpoint**: `GET /breeds`

**Method**: GET

**Authentication**: Required (x-api-key header)

**Query Parameters**: None

**Pagination**: Not required (typically returns ~100 breeds in a single response).

**Incremental Strategy**:
- The `breeds` object uses **snapshot** ingestion type.
- Breed data is relatively static and changes infrequently.
- Full snapshot approach: retrieve all breeds in a single request.

**Example API request**:

```bash
curl -X GET \
  -H "x-api-key: YOUR_API_KEY" \
  "https://api.thecatapi.com/v1/breeds"
```

**Extra parameters needed to read the table**:
- None.

**Rate Limits**:
- Same as general API rate limits (TBD: exact values).

### `categories` object

**Endpoint**: `GET /categories`

**Method**: GET

**Authentication**: Required (x-api-key header)

**Query Parameters**: None

**Pagination**: Not required (typically returns ~10 categories in a single response).

**Incremental Strategy**:
- The `categories` object uses **snapshot** ingestion type.
- Categories are static reference data.
- Full snapshot approach: retrieve all categories in a single request.

**Example API request**:

```bash
curl -X GET \
  -H "x-api-key: YOUR_API_KEY" \
  "https://api.thecatapi.com/v1/categories"
```

**Extra parameters needed to read the table**:
- None.

**Rate Limits**:
- Same as general API rate limits (TBD: exact values).

### `votes` object

**Endpoint**: `GET /votes`

**Method**: GET

**Authentication**: Required (x-api-key header)

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Number of results to return (default: 10, max: 100). |
| `page` | integer | No | Page number for pagination (0-indexed). |
| `sub_id` | string | No | Filter by user-submitted identifier. |

**Pagination**:
- Use `page` and `limit` parameters for pagination.
- `page` is 0-indexed.
- Maximum `limit` is 100 per request.

**Incremental Strategy**:
- The `votes` object uses **append** ingestion type.
- Votes are append-only (cannot be modified or deleted).
- Use `created_at` field as cursor for incremental reads.
- Sort by `created_at` in descending order and track the latest timestamp.
- In subsequent runs, filter votes where `created_at` > last processed timestamp.

**Example API request**:

```bash
curl -X GET \
  -H "x-api-key: YOUR_API_KEY" \
  "https://api.thecatapi.com/v1/votes?limit=10&page=0"
```

**Extra parameters needed to read the table**:
- None required. `sub_id` is optional for filtering.

**Rate Limits**:
- Same as general API rate limits (TBD: exact values).

### `favourites` object

**Endpoint**: `GET /favourites`

**Method**: GET

**Authentication**: Required (x-api-key header)

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Number of results to return (default: 10, max: 100). |
| `page` | integer | No | Page number for pagination (0-indexed). |
| `sub_id` | string | No | Filter by user-submitted identifier. |

**Pagination**:
- Use `page` and `limit` parameters for pagination.
- `page` is 0-indexed.
- Maximum `limit` is 100 per request.

**Incremental Strategy**:
- The `favourites` object uses **cdc** ingestion type.
- Favourites can be created and deleted.
- Use `created_at` field as cursor for incremental reads.
- Sort by `created_at` in descending order and track the latest timestamp.
- In subsequent runs, filter favourites where `created_at` > last processed timestamp.
- Deleted favourites: Compare current state with previous state to detect deletions (favourites that existed before but are no longer present).

**Example API request**:

```bash
curl -X GET \
  -H "x-api-key: YOUR_API_KEY" \
  "https://api.thecatapi.com/v1/favourites?limit=10&page=0"
```

**Extra parameters needed to read the table**:
- None required. `sub_id` is optional for filtering.

**Rate Limits**:
- Same as general API rate limits (TBD: exact values).

## **Field Type Mapping**

The Cat API returns JSON responses with the following field type mappings:

| API Field Type | Standard Data Type | Notes |
|---------------|-------------------|-------|
| `string` | StringType | Text fields, URLs, IDs. |
| `integer` | LongType | Numeric fields (scores, flags, dimensions). Prefer LongType over IntegerType. |
| `boolean` | BooleanType | Not directly used; flags are represented as integers (0 or 1). |
| `array` | ArrayType | Arrays of objects (e.g., breeds array, categories array). |
| `object` | StructType | Nested objects (e.g., weight struct, image struct within favourites). |
| `null` | Nullable | Many fields can be null (e.g., `alt_names`, `wikipedia_url`). |
| ISO 8601 datetime string | TimestampType | Datetime fields (e.g., `created_at`). |

**Special field behaviors**:
- **Score fields** (adaptability, affection_level, etc.): Integer values ranging from 1-5.
- **Flag fields** (indoor, lap, experimental, etc.): Integer values of 0 or 1 (representing boolean false/true).
- **Weight struct**: Contains `imperial` and `metric` string fields with weight ranges.
- **Breeds array**: Can be empty if image has no breed information.
- **Categories array**: Can be empty if image has no category assignments.

## **Write API**

The Cat API supports write operations for user-specific data (votes and favourites). These operations require authentication.

### Creating a Vote

**Endpoint**: `POST /votes`

**Method**: POST

**Authentication**: Required (x-api-key header)

**Request Body**:

```json
{
  "image_id": "MTY3ODc4OA",
  "sub_id": "user123",
  "value": 1
}
```

**Request Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_id` | string | Yes | ID of the image to vote on. |
| `sub_id` | string | Yes | User-submitted identifier. |
| `value` | integer | Yes | Vote value: `1` (upvote) or `0` (downvote). |

**Response**:

```json
{
  "message": "SUCCESS",
  "id": 12345
}
```

**Validation**: After creating a vote, retrieve it using `GET /votes` to verify it was created successfully.

### Creating a Favourite

**Endpoint**: `POST /favourites`

**Method**: POST

**Authentication**: Required (x-api-key header)

**Request Body**:

```json
{
  "image_id": "MTY3ODc4OA",
  "sub_id": "user123"
}
```

**Request Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_id` | string | Yes | ID of the image to favourite. |
| `sub_id` | string | Yes | User-submitted identifier. |

**Response**:

```json
{
  "message": "SUCCESS",
  "id": 67890
}
```

**Validation**: After creating a favourite, retrieve it using `GET /favourites` to verify it was created successfully.

### Deleting a Favourite

**Endpoint**: `DELETE /favourites/{favourite_id}`

**Method**: DELETE

**Authentication**: Required (x-api-key header)

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `favourite_id` | integer | Yes | ID of the favourite to delete. |

**Response**:

```json
{
  "message": "SUCCESS"
}
```

**Validation**: After deleting a favourite, verify it no longer appears in `GET /favourites` response.

**Notes**:
- Write operations are only available for votes and favourites (user-specific data).
- Images, breeds, and categories are read-only (managed by The Cat API).
- All write operations require authentication via x-api-key header.

## **Research Log**

| Source Type | URL | Accessed (UTC) | Confidence (High/Med/Low) | What it confirmed |
|-------------|-----|----------------|---------------------------|-------------------|
| User-provided docs | https://developers.thecatapi.com/view-account/ylX4blBYT9FaoVd6OhvR?report=bOoHBz-8t | 2025-01-27 | High | Primary source for API documentation |
| Official Docs | https://docs.thecatapi.com/ | 2025-01-27 | High | API endpoints, authentication, schemas |
| Official Docs | https://thecatapi.com/ | 2025-01-27 | High | API key registration, general information |
| Postman Collection | https://www.postman.com/thatapicompany/thatapicompany-public-documentation/collection/5t6xsb2/the-cat-api | 2025-01-27 | Med | Endpoint examples and request/response formats |
| GitHub Client Library | https://github.com/thatapicompany/thecatapi | 2025-01-27 | Med | API usage patterns and field structures |

## **Sources and References**

### Official Documentation
- **The Cat API Documentation**: https://docs.thecatapi.com/
- **The Cat API Website**: https://thecatapi.com/
- **Account Dashboard**: https://account.thecatapi.com/
- **User-provided Documentation**: https://developers.thecatapi.com/view-account/ylX4blBYT9FaoVd6OhvR?report=bOoHBz-8t

### Developer Resources
- **Postman Collection**: https://www.postman.com/thatapicompany/thatapicompany-public-documentation/collection/5t6xsb2/the-cat-api
- **GitHub Client Library**: https://github.com/thatapicompany/thecatapi

### Confidence Levels
- **Official API docs**: Highest confidence - Primary source of truth for API structure, endpoints, and authentication.
- **User-provided documentation**: High confidence - Specific account documentation provided by user.
- **Postman Collection**: Medium confidence - Useful for understanding request/response formats but may not always reflect latest API changes.
- **GitHub Client Library**: Medium confidence - Provides implementation patterns but may abstract some API details.

### Known Gaps and TBD Items
- **Rate Limits**: Exact rate limit values (requests per hour/day) are TBD and need to be confirmed from official documentation or account dashboard.
- **Image Deletion Tracking**: The API doesn't provide a way to track when images are removed from the collection. This limits the ability to detect deletions for the `images` object.
- **Image Creation Timestamps**: Images don't have `created_at` or `updated_at` fields, making incremental ingestion challenging for the `images` object.

### Conflict Resolution
- No conflicts identified between sources. All sources align on core API structure and endpoints.
- User-provided documentation takes precedence for account-specific details.
- Official documentation takes precedence for general API behavior and schemas.

