# Health

Methods:

- <code title="get /health">client.health.<a href="./src/spatialise/resources/health.py">check</a>() -> object</code>

# Batch

Types:

```python
from spatialise.types import BatchStatus, BatchCreateResponse, BatchRetrieveStatusResponse
```

Methods:

- <code title="post /v1/batch/">client.batch.<a href="./src/spatialise/resources/batch.py">create</a>(\*\*<a href="src/spatialise/types/batch_create_params.py">params</a>) -> <a href="./src/spatialise/types/batch_create_response.py">BatchCreateResponse</a></code>
- <code title="get /v1/batch/{batch_id}/status">client.batch.<a href="./src/spatialise/resources/batch.py">retrieve_status</a>(batch_id, \*\*<a href="src/spatialise/types/batch_retrieve_status_params.py">params</a>) -> <a href="./src/spatialise/types/batch_retrieve_status_response.py">BatchRetrieveStatusResponse</a></code>
