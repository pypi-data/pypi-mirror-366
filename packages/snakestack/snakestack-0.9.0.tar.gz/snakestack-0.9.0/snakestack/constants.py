# Unidades de tamanho
KILOBYTE = 1024
MEGABYTE = 1024 * 1024
GIGABYTE = 1024 * 1024 * 1024
TERABYTE = 1024 * 1024 * 1024 * 1024

# Unidades de tempo
MILLISECONDS = 0.001
SECONDS = 1
MINUTES = 60 * SECONDS
HOURS = 60 * MINUTES

# Docs
ERROR_DETAIL_SCHEMA_DESCRIPTION = "Error message or explanation"
PAGINATE_LIMIT_SCHEMA_DESCRIPTION = "The maximum number of items to return per page."
PAGINATE_OFFSET_SCHEMA_DESCRIPTION = (
    "The number of items to skip before starting "
    "to collect the result set."
)
PAGINATE_TOTAL_PAGES_SCHEMA_DESCRIPTION = (
    "Total number of pages based on total items and page size."
)
PAGINATE_HAS_PREV_SCHEMA_DESCRIPTION = (
    "Indicates if there is a previous page available."
)
PAGINATE_HAS_NEXT_SCHEMA_DESCRIPTION = "Indicates if there is a next page available."
PAGINATE_SIZE_SCHEMA_DESCRIPTION = (
    "Total number of pages based on total items and page size."
)
PAGINATE_PAGE_SCHEMA_DESCRIPTION = "Current page number, starting at 1."
PAGINATE_TOTAL_SCHEMA_DESCRIPTION = "Total number of data available in the database."
PAGINATE_ITEMS_SCHEMA_DESCRIPTION = "List of resources returned in the current page."
