# Worqhat

Types:

```python
from worqhat.types import GetServerInfoResponse
```

Methods:

- <code title="get /">client.<a href="./src/worqhat/_client.py">get_server_info</a>() -> <a href="./src/worqhat/types/get_server_info_response.py">GetServerInfoResponse</a></code>

# DB

Types:

```python
from worqhat.types import (
    DBDeleteRecordsResponse,
    DBExecuteQueryResponse,
    DBInsertRecordResponse,
    DBProcessNlQueryResponse,
    DBUpdateRecordsResponse,
)
```

Methods:

- <code title="delete /db/delete">client.db.<a href="./src/worqhat/resources/db.py">delete_records</a>(\*\*<a href="src/worqhat/types/db_delete_records_params.py">params</a>) -> <a href="./src/worqhat/types/db_delete_records_response.py">DBDeleteRecordsResponse</a></code>
- <code title="post /db/query">client.db.<a href="./src/worqhat/resources/db.py">execute_query</a>(\*\*<a href="src/worqhat/types/db_execute_query_params.py">params</a>) -> <a href="./src/worqhat/types/db_execute_query_response.py">DBExecuteQueryResponse</a></code>
- <code title="post /db/insert">client.db.<a href="./src/worqhat/resources/db.py">insert_record</a>(\*\*<a href="src/worqhat/types/db_insert_record_params.py">params</a>) -> <a href="./src/worqhat/types/db_insert_record_response.py">DBInsertRecordResponse</a></code>
- <code title="post /db/nl-query">client.db.<a href="./src/worqhat/resources/db.py">process_nl_query</a>(\*\*<a href="src/worqhat/types/db_process_nl_query_params.py">params</a>) -> <a href="./src/worqhat/types/db_process_nl_query_response.py">DBProcessNlQueryResponse</a></code>
- <code title="put /db/update">client.db.<a href="./src/worqhat/resources/db.py">update_records</a>(\*\*<a href="src/worqhat/types/db_update_records_params.py">params</a>) -> <a href="./src/worqhat/types/db_update_records_response.py">DBUpdateRecordsResponse</a></code>

# Health

Types:

```python
from worqhat.types import HealthCheckResponse
```

Methods:

- <code title="get /health">client.health.<a href="./src/worqhat/resources/health.py">check</a>() -> <a href="./src/worqhat/types/health_check_response.py">HealthCheckResponse</a></code>

# Flows

Types:

```python
from worqhat.types import (
    FlowGetMetricsResponse,
    FlowTriggerWithFileResponse,
    FlowTriggerWithPayloadResponse,
)
```

Methods:

- <code title="get /flows/metrics">client.flows.<a href="./src/worqhat/resources/flows.py">get_metrics</a>(\*\*<a href="src/worqhat/types/flow_get_metrics_params.py">params</a>) -> <a href="./src/worqhat/types/flow_get_metrics_response.py">FlowGetMetricsResponse</a></code>
- <code title="post /flows/file/{flowId}">client.flows.<a href="./src/worqhat/resources/flows.py">trigger_with_file</a>(flow_id, \*\*<a href="src/worqhat/types/flow_trigger_with_file_params.py">params</a>) -> <a href="./src/worqhat/types/flow_trigger_with_file_response.py">FlowTriggerWithFileResponse</a></code>
- <code title="post /flows/trigger/{flowId}">client.flows.<a href="./src/worqhat/resources/flows.py">trigger_with_payload</a>(flow_id, \*\*<a href="src/worqhat/types/flow_trigger_with_payload_params.py">params</a>) -> <a href="./src/worqhat/types/flow_trigger_with_payload_response.py">FlowTriggerWithPayloadResponse</a></code>
