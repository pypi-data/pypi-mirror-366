# Memory

## DrmInstances

Types:

```python
from entities.types.memory import (
    DrmInstance,
    DrmInstanceListResponse,
    DrmInstanceGetMemoryContextResponse,
    DrmInstanceGetMessagesResponse,
    DrmInstanceLogMessagesResponse,
)
```

Methods:

- <code title="post /api/memory/drm-instances/">client.memory.drm_instances.<a href="./src/entities/resources/memory/drm_instances.py">create</a>(\*\*<a href="src/entities/types/memory/drm_instance_create_params.py">params</a>) -> <a href="./src/entities/types/memory/drm_instance.py">DrmInstance</a></code>
- <code title="get /api/memory/drm-instances/{id}/">client.memory.drm_instances.<a href="./src/entities/resources/memory/drm_instances.py">retrieve</a>(id) -> <a href="./src/entities/types/memory/drm_instance.py">DrmInstance</a></code>
- <code title="patch /api/memory/drm-instances/{id}/">client.memory.drm_instances.<a href="./src/entities/resources/memory/drm_instances.py">update</a>(id, \*\*<a href="src/entities/types/memory/drm_instance_update_params.py">params</a>) -> <a href="./src/entities/types/memory/drm_instance.py">DrmInstance</a></code>
- <code title="get /api/memory/drm-instances/">client.memory.drm_instances.<a href="./src/entities/resources/memory/drm_instances.py">list</a>() -> <a href="./src/entities/types/memory/drm_instance_list_response.py">DrmInstanceListResponse</a></code>
- <code title="delete /api/memory/drm-instances/{id}/">client.memory.drm_instances.<a href="./src/entities/resources/memory/drm_instances.py">delete</a>(id) -> None</code>
- <code title="get /api/memory/drm-instances/{id}/memory-context/">client.memory.drm_instances.<a href="./src/entities/resources/memory/drm_instances.py">get_memory_context</a>(id) -> <a href="./src/entities/types/memory/drm_instance_get_memory_context_response.py">DrmInstanceGetMemoryContextResponse</a></code>
- <code title="get /api/memory/drm-instances/{id}/messages/">client.memory.drm_instances.<a href="./src/entities/resources/memory/drm_instances.py">get_messages</a>(id) -> <a href="./src/entities/types/memory/drm_instance_get_messages_response.py">DrmInstanceGetMessagesResponse</a></code>
- <code title="post /api/memory/drm-instances/{id}/log-messages/">client.memory.drm_instances.<a href="./src/entities/resources/memory/drm_instances.py">log_messages</a>(id, \*\*<a href="src/entities/types/memory/drm_instance_log_messages_params.py">params</a>) -> <a href="./src/entities/types/memory/drm_instance_log_messages_response.py">DrmInstanceLogMessagesResponse</a></code>

# Orgs

## APIKeys

Types:

```python
from entities.types.orgs import APIKey, APIKeyListResponse
```

Methods:

- <code title="post /api/orgs/api-keys/">client.orgs.api_keys.<a href="./src/entities/resources/orgs/api_keys.py">create</a>(\*\*<a href="src/entities/types/orgs/api_key_create_params.py">params</a>) -> <a href="./src/entities/types/orgs/api_key.py">APIKey</a></code>
- <code title="get /api/orgs/api-keys/{id}/">client.orgs.api_keys.<a href="./src/entities/resources/orgs/api_keys.py">retrieve</a>(id) -> <a href="./src/entities/types/orgs/api_key.py">APIKey</a></code>
- <code title="patch /api/orgs/api-keys/{id}/">client.orgs.api_keys.<a href="./src/entities/resources/orgs/api_keys.py">update</a>(id, \*\*<a href="src/entities/types/orgs/api_key_update_params.py">params</a>) -> <a href="./src/entities/types/orgs/api_key.py">APIKey</a></code>
- <code title="get /api/orgs/api-keys/">client.orgs.api_keys.<a href="./src/entities/resources/orgs/api_keys.py">list</a>() -> <a href="./src/entities/types/orgs/api_key_list_response.py">APIKeyListResponse</a></code>
- <code title="delete /api/orgs/api-keys/{id}/">client.orgs.api_keys.<a href="./src/entities/resources/orgs/api_keys.py">delete</a>(id) -> None</code>

## Organizations

Types:

```python
from entities.types.orgs import Organization, OrganizationListResponse
```

Methods:

- <code title="post /api/orgs/organizations/">client.orgs.organizations.<a href="./src/entities/resources/orgs/organizations.py">create</a>(\*\*<a href="src/entities/types/orgs/organization_create_params.py">params</a>) -> <a href="./src/entities/types/orgs/organization.py">Organization</a></code>
- <code title="get /api/orgs/organizations/{id}/">client.orgs.organizations.<a href="./src/entities/resources/orgs/organizations.py">retrieve</a>(id) -> <a href="./src/entities/types/orgs/organization.py">Organization</a></code>
- <code title="patch /api/orgs/organizations/{id}/">client.orgs.organizations.<a href="./src/entities/resources/orgs/organizations.py">update</a>(id, \*\*<a href="src/entities/types/orgs/organization_update_params.py">params</a>) -> <a href="./src/entities/types/orgs/organization.py">Organization</a></code>
- <code title="get /api/orgs/organizations/">client.orgs.organizations.<a href="./src/entities/resources/orgs/organizations.py">list</a>() -> <a href="./src/entities/types/orgs/organization_list_response.py">OrganizationListResponse</a></code>
- <code title="delete /api/orgs/organizations/{id}/">client.orgs.organizations.<a href="./src/entities/resources/orgs/organizations.py">delete</a>(id) -> None</code>
