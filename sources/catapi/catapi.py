import requests
from typing import Iterator, Any, Dict, List
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    LongType,
    IntegerType,
    ArrayType,
)


class LakeflowConnect:
    def __init__(self, options: dict[str, str]) -> None:
        """
        Initialize the CatAPI connector with API key authentication.

        Expected options:
            - api_key: API key for The Cat API authentication (required).
            - base_url (optional): Override for Cat API base URL. Defaults to https://api.thecatapi.com/v1.
        """
        api_key = options.get("api_key")
        if not api_key:
            raise ValueError("CatAPI connector requires 'api_key' in options")

        self.base_url = options.get("base_url", "https://api.thecatapi.com/v1").rstrip("/")

        # Configure a session with proper headers for The Cat API
        self._session = requests.Session()
        self._session.headers.update(
            {
                "x-api-key": api_key,
                "Content-Type": "application/json",
            }
        )

        # Supported tables
        self.supported_tables = [
            "images",
            "breeds",
            "categories",
            "votes",
            "favourites",
        ]

    def list_tables(self) -> list[str]:
        """
        List names of all tables supported by this connector.
        """
        return self.supported_tables

    def get_table_schema(
        self, table_name: str, table_options: dict[str, str]
    ) -> StructType:
        """
        Fetch the schema of a table.

        The schema is static and derived from The Cat API documentation.
        """
        if table_name not in self.supported_tables:
            raise ValueError(f"Unsupported table: {table_name!r}")

        if table_name == "images":
            return self._get_images_schema()
        elif table_name == "breeds":
            return self._get_breeds_schema()
        elif table_name == "categories":
            return self._get_categories_schema()
        elif table_name == "votes":
            return self._get_votes_schema()
        elif table_name == "favourites":
            return self._get_favourites_schema()

    def _get_images_schema(self) -> StructType:
        """Get schema for the images table."""
        # Nested weight struct schema (within breeds)
        weight_struct = StructType(
            [
                StructField("imperial", StringType(), True),
                StructField("metric", StringType(), True),
            ]
        )

        # Nested breed struct schema (within images)
        breed_struct = StructType(
            [
                StructField("id", StringType(), True),
                StructField("name", StringType(), True),
                StructField("temperament", StringType(), True),
                StructField("life_span", StringType(), True),
                StructField("alt_names", StringType(), True),
                StructField("wikipedia_url", StringType(), True),
                StructField("origin", StringType(), True),
                StructField("weight", weight_struct, True),
                StructField("cfa_url", StringType(), True),
                StructField("vetstreet_url", StringType(), True),
                StructField("vcahospitals_url", StringType(), True),
                StructField("country_codes", StringType(), True),
                StructField("description", StringType(), True),
                StructField("indoor", LongType(), True),
                StructField("lap", LongType(), True),
                StructField("adaptability", LongType(), True),
                StructField("affection_level", LongType(), True),
                StructField("child_friendly", LongType(), True),
                StructField("dog_friendly", LongType(), True),
                StructField("energy_level", LongType(), True),
                StructField("grooming", LongType(), True),
                StructField("health_issues", LongType(), True),
                StructField("intelligence", LongType(), True),
                StructField("shedding_level", LongType(), True),
                StructField("social_needs", LongType(), True),
                StructField("stranger_friendly", LongType(), True),
                StructField("vocalisation", LongType(), True),
                StructField("experimental", LongType(), True),
                StructField("hairless", LongType(), True),
                StructField("natural", LongType(), True),
                StructField("rare", LongType(), True),
                StructField("rex", LongType(), True),
                StructField("suppressed_tail", LongType(), True),
                StructField("short_legs", LongType(), True),
                StructField("hypoallergenic", LongType(), True),
            ]
        )

        # Nested category struct schema (within images)
        category_struct = StructType(
            [
                StructField("id", LongType(), True),
                StructField("name", StringType(), True),
            ]
        )

        # Primary images table schema
        images_schema = StructType(
            [
                StructField("id", StringType(), False),
                StructField("url", StringType(), True),
                StructField("width", LongType(), True),
                StructField("height", LongType(), True),
                StructField("breeds", ArrayType(breed_struct, True), True),
                StructField("categories", ArrayType(category_struct, True), True),
                StructField("sub_id", StringType(), True),
            ]
        )

        return images_schema

    def _get_breeds_schema(self) -> StructType:
        """Get schema for the breeds table."""
        # Nested weight struct schema
        weight_struct = StructType(
            [
                StructField("imperial", StringType(), True),
                StructField("metric", StringType(), True),
            ]
        )

        breeds_schema = StructType(
            [
                StructField("id", StringType(), False),
                StructField("name", StringType(), True),
                StructField("temperament", StringType(), True),
                StructField("life_span", StringType(), True),
                StructField("alt_names", StringType(), True),
                StructField("wikipedia_url", StringType(), True),
                StructField("origin", StringType(), True),
                StructField("weight", weight_struct, True),
                StructField("cfa_url", StringType(), True),
                StructField("vetstreet_url", StringType(), True),
                StructField("vcahospitals_url", StringType(), True),
                StructField("country_codes", StringType(), True),
                StructField("description", StringType(), True),
                StructField("indoor", LongType(), True),
                StructField("lap", LongType(), True),
                StructField("adaptability", LongType(), True),
                StructField("affection_level", LongType(), True),
                StructField("child_friendly", LongType(), True),
                StructField("dog_friendly", LongType(), True),
                StructField("energy_level", LongType(), True),
                StructField("grooming", LongType(), True),
                StructField("health_issues", LongType(), True),
                StructField("intelligence", LongType(), True),
                StructField("shedding_level", LongType(), True),
                StructField("social_needs", LongType(), True),
                StructField("stranger_friendly", LongType(), True),
                StructField("vocalisation", LongType(), True),
                StructField("experimental", LongType(), True),
                StructField("hairless", LongType(), True),
                StructField("natural", LongType(), True),
                StructField("rare", LongType(), True),
                StructField("rex", LongType(), True),
                StructField("suppressed_tail", LongType(), True),
                StructField("short_legs", LongType(), True),
                StructField("hypoallergenic", LongType(), True),
            ]
        )

        return breeds_schema

    def _get_categories_schema(self) -> StructType:
        """Get schema for the categories table."""
        categories_schema = StructType(
            [
                StructField("id", LongType(), False),
                StructField("name", StringType(), True),
            ]
        )

        return categories_schema

    def _get_votes_schema(self) -> StructType:
        """Get schema for the votes table."""
        votes_schema = StructType(
            [
                StructField("id", LongType(), False),
                StructField("image_id", StringType(), True),
                StructField("sub_id", StringType(), True),
                StructField("created_at", StringType(), True),
                StructField("value", LongType(), True),
                StructField("country_code", StringType(), True),
            ]
        )

        return votes_schema

    def _get_favourites_schema(self) -> StructType:
        """Get schema for the favourites table."""
        # Nested weight struct schema (within breeds within image)
        weight_struct = StructType(
            [
                StructField("imperial", StringType(), True),
                StructField("metric", StringType(), True),
            ]
        )

        # Nested breed struct schema (within image)
        breed_struct = StructType(
            [
                StructField("id", StringType(), True),
                StructField("name", StringType(), True),
                StructField("temperament", StringType(), True),
                StructField("life_span", StringType(), True),
                StructField("alt_names", StringType(), True),
                StructField("wikipedia_url", StringType(), True),
                StructField("origin", StringType(), True),
                StructField("weight", weight_struct, True),
                StructField("cfa_url", StringType(), True),
                StructField("vetstreet_url", StringType(), True),
                StructField("vcahospitals_url", StringType(), True),
                StructField("country_codes", StringType(), True),
                StructField("description", StringType(), True),
                StructField("indoor", LongType(), True),
                StructField("lap", LongType(), True),
                StructField("adaptability", LongType(), True),
                StructField("affection_level", LongType(), True),
                StructField("child_friendly", LongType(), True),
                StructField("dog_friendly", LongType(), True),
                StructField("energy_level", LongType(), True),
                StructField("grooming", LongType(), True),
                StructField("health_issues", LongType(), True),
                StructField("intelligence", LongType(), True),
                StructField("shedding_level", LongType(), True),
                StructField("social_needs", LongType(), True),
                StructField("stranger_friendly", LongType(), True),
                StructField("vocalisation", LongType(), True),
                StructField("experimental", LongType(), True),
                StructField("hairless", LongType(), True),
                StructField("natural", LongType(), True),
                StructField("rare", LongType(), True),
                StructField("rex", LongType(), True),
                StructField("suppressed_tail", LongType(), True),
                StructField("short_legs", LongType(), True),
                StructField("hypoallergenic", LongType(), True),
            ]
        )

        # Nested category struct schema (within image)
        category_struct = StructType(
            [
                StructField("id", LongType(), True),
                StructField("name", StringType(), True),
            ]
        )

        # Nested image struct schema (within favourites)
        image_struct = StructType(
            [
                StructField("id", StringType(), True),
                StructField("url", StringType(), True),
                StructField("width", LongType(), True),
                StructField("height", LongType(), True),
                StructField("breeds", ArrayType(breed_struct, True), True),
                StructField("categories", ArrayType(category_struct, True), True),
                StructField("sub_id", StringType(), True),
            ]
        )

        favourites_schema = StructType(
            [
                StructField("id", LongType(), False),
                StructField("user_id", StringType(), True),
                StructField("image_id", StringType(), True),
                StructField("sub_id", StringType(), True),
                StructField("created_at", StringType(), True),
                StructField("image", image_struct, True),
            ]
        )

        return favourites_schema

    def read_table_metadata(
        self, table_name: str, table_options: dict[str, str]
    ) -> dict:
        """
        Fetch metadata for the given table.
        """
        if table_name not in self.supported_tables:
            raise ValueError(f"Unsupported table: {table_name!r}")

        if table_name == "images":
            return {
                "primary_keys": ["id"],
                "ingestion_type": "snapshot",
            }
        elif table_name == "breeds":
            return {
                "primary_keys": ["id"],
                "ingestion_type": "snapshot",
            }
        elif table_name == "categories":
            return {
                "primary_keys": ["id"],
                "ingestion_type": "snapshot",
            }
        elif table_name == "votes":
            return {
                "primary_keys": ["id"],
                "cursor_field": "created_at",
                "ingestion_type": "append",
            }
        elif table_name == "favourites":
            return {
                "primary_keys": ["id"],
                "cursor_field": "created_at",
                "ingestion_type": "cdc",
            }

    def read_table(
        self, table_name: str, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """
        Read records from a table and return an iterator of records and an offset.
        """
        if table_name not in self.supported_tables:
            raise ValueError(f"Unsupported table: {table_name!r}")

        if table_name == "images":
            return self._read_images(start_offset, table_options)
        elif table_name == "breeds":
            return self._read_breeds(start_offset, table_options)
        elif table_name == "categories":
            return self._read_categories(start_offset, table_options)
        elif table_name == "votes":
            return self._read_votes(start_offset, table_options)
        elif table_name == "favourites":
            return self._read_favourites(start_offset, table_options)

    def _read_images(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the `images` table."""
        # Get pagination parameters
        limit = 100  # Maximum allowed by API
        try:
            limit = int(table_options.get("limit", 100))
        except (TypeError, ValueError):
            limit = 100
        limit = max(1, min(limit, 100))

        # Get starting page from offset
        page = 0
        if start_offset and isinstance(start_offset, dict):
            page = start_offset.get("page", 0)
        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 0
        page = max(0, page)

        # Optional filter parameters
        breed_id = table_options.get("breed_id")
        category_ids = table_options.get("category_ids")
        size = table_options.get("size")
        mime_types = table_options.get("mime_types")
        has_breeds = table_options.get("has_breeds")
        order = table_options.get("order", "ASC")  # Use ASC for consistent ordering

        # Build request parameters
        params = {
            "limit": limit,
            "page": page,
            "order": order,
        }
        if breed_id:
            params["breed_id"] = breed_id
        if category_ids:
            params["category_ids"] = category_ids
        if size:
            params["size"] = size
        if mime_types:
            params["mime_types"] = mime_types
        if has_breeds is not None:
            params["has_breeds"] = has_breeds

        url = f"{self.base_url}/images/search"
        records: list[dict[str, Any]] = []

        # Make API request
        response = self._session.get(url, params=params, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(
                f"CatAPI error for images: {response.status_code} {response.text}"
            )

        images = response.json() or []
        if not isinstance(images, list):
            raise ValueError(
                f"Unexpected response format for images: {type(images).__name__}"
            )

        # Process records - ensure nested structures are properly handled
        for image in images:
            record: dict[str, Any] = dict(image)
            
            # Ensure breeds array exists (can be empty)
            if "breeds" not in record:
                record["breeds"] = None
            
            # Ensure categories array exists (can be empty)
            if "categories" not in record:
                record["categories"] = None
            
            records.append(record)

        # Determine next offset
        # If we got fewer records than requested (or empty), we've reached the end
        # Return the same offset to signal completion (per interface contract)
        if len(images) == 0 or len(images) < limit:
            # No more pages - return the same offset to signal end
            # If start_offset was None, use current page; otherwise return start_offset
            if start_offset:
                next_offset = start_offset
            else:
                next_offset = {"page": page}
        else:
            # More pages might exist
            next_offset = {"page": page + 1}

        def record_iterator():
            for record in records:
                yield record

        return record_iterator(), next_offset

    def _read_breeds(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the `breeds` table."""
        url = f"{self.base_url}/breeds"
        
        response = self._session.get(url, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(
                f"CatAPI error for breeds: {response.status_code} {response.text}"
            )

        breeds = response.json() or []
        if not isinstance(breeds, list):
            raise ValueError(
                f"Unexpected response format for breeds: {type(breeds).__name__}"
            )

        records: list[dict[str, Any]] = []
        for breed in breeds:
            record: dict[str, Any] = dict(breed)
            records.append(record)

        # Breeds are read in one batch (no pagination)
        def record_iterator():
            for record in records:
                yield record

        return record_iterator(), None

    def _read_categories(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the `categories` table."""
        url = f"{self.base_url}/categories"
        
        response = self._session.get(url, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(
                f"CatAPI error for categories: {response.status_code} {response.text}"
            )

        categories = response.json() or []
        if not isinstance(categories, list):
            raise ValueError(
                f"Unexpected response format for categories: {type(categories).__name__}"
            )

        records: list[dict[str, Any]] = []
        for category in categories:
            record: dict[str, Any] = dict(category)
            records.append(record)

        # Categories are read in one batch (no pagination)
        def record_iterator():
            for record in records:
                yield record

        return record_iterator(), None

    def _read_votes(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the `votes` table."""
        # Get pagination parameters
        limit = 100  # Maximum allowed by API
        try:
            limit = int(table_options.get("limit", 100))
        except (TypeError, ValueError):
            limit = 100
        limit = max(1, min(limit, 100))

        # Get starting page from offset
        page = 0
        if start_offset and isinstance(start_offset, dict):
            page = start_offset.get("page", 0)
        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 0
        page = max(0, page)

        # Optional filter parameter
        sub_id = table_options.get("sub_id")

        params = {
            "limit": limit,
            "page": page,
        }
        if sub_id:
            params["sub_id"] = sub_id

        url = f"{self.base_url}/votes"
        records: list[dict[str, Any]] = []

        response = self._session.get(url, params=params, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(
                f"CatAPI error for votes: {response.status_code} {response.text}"
            )

        votes = response.json() or []
        if not isinstance(votes, list):
            raise ValueError(
                f"Unexpected response format for votes: {type(votes).__name__}"
            )

        for vote in votes:
            record: dict[str, Any] = dict(vote)
            records.append(record)

        # Determine next offset
        # If we got fewer records than requested (or empty), we've reached the end
        # Return the same offset to signal completion (per interface contract)
        if len(votes) == 0 or len(votes) < limit:
            # No more pages - return the same offset to signal end
            if start_offset:
                next_offset = start_offset
            else:
                next_offset = {"page": page}
        else:
            # More pages might exist
            next_offset = {"page": page + 1}

        def record_iterator():
            for record in records:
                yield record

        return record_iterator(), next_offset

    def _read_favourites(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the `favourites` table."""
        # Get pagination parameters
        limit = 100  # Maximum allowed by API
        try:
            limit = int(table_options.get("limit", 100))
        except (TypeError, ValueError):
            limit = 100
        limit = max(1, min(limit, 100))

        # Get starting page from offset
        page = 0
        if start_offset and isinstance(start_offset, dict):
            page = start_offset.get("page", 0)
        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 0
        page = max(0, page)

        # Optional filter parameter
        sub_id = table_options.get("sub_id")

        params = {
            "limit": limit,
            "page": page,
        }
        if sub_id:
            params["sub_id"] = sub_id

        url = f"{self.base_url}/favourites"
        records: list[dict[str, Any]] = []

        response = self._session.get(url, params=params, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(
                f"CatAPI error for favourites: {response.status_code} {response.text}"
            )

        favourites = response.json() or []
        if not isinstance(favourites, list):
            raise ValueError(
                f"Unexpected response format for favourites: {type(favourites).__name__}"
            )

        for favourite in favourites:
            record: dict[str, Any] = dict(favourite)
            
            # Ensure image struct exists (can be None)
            if "image" not in record:
                record["image"] = None
            
            records.append(record)

        # Determine next offset
        # If we got fewer records than requested (or empty), we've reached the end
        # Return the same offset to signal completion (per interface contract)
        if len(favourites) == 0 or len(favourites) < limit:
            # No more pages - return the same offset to signal end
            if start_offset:
                next_offset = start_offset
            else:
                next_offset = {"page": page}
        else:
            # More pages might exist
            next_offset = {"page": page + 1}

        def record_iterator():
            for record in records:
                yield record

        return record_iterator(), next_offset

