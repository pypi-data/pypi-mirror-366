# LiRAYS API Python Client

A comprehensive Python client library for the LiRAYS API - Fiber Network Design. This library provides a clean, intuitive interface to interact with all LiRAYS API endpoints including authentication, project management, plan execution, layer management, feature operations, and tools execution.

## Features

- **🔐 Authentication**: Secure JWT-based authentication with automatic token refresh
- **📊 Project Management**: Create and manage GIS projects with hierarchical organization
- **📋 Plan Execution**: Define and execute analysis plans with status tracking
- **🗂️ Layer Management**: Handle different types of geographic layers with classification
- **📍 Feature Operations**: CRUD operations for geographic features (points, lines, polygons)
- **🛠️ Tools Execution**: Real-time streaming execution of GIS analysis tools
- **📦 Type Safety**: Full Pydantic model support for request/response validation
- **🔄 Context Manager**: Automatic resource cleanup and connection management
- **⚡ Async Support**: Streaming and callback-based tool execution

## Installation

```bash
pip install lirays-api-client
```

## Quick Start

```python
from lirays_client import LiRAYSClient, LayerClass, GeomType

# Initialize and authenticate
with LiRAYSClient() as client:
    # Login
    client.login("your-email@example.com", "your-password")
    
    # Create a project
    project = client.create_project("My GIS Project", "Project description")
    
    # Create a plan
    plan = client.create_plan(project.id, "Phase 1 Analysis")
    
    # Create a layer
    layer = client.create_layer(plan.id, LayerClass.PARCELS, "Property Parcels")
    
    # Add a point feature
    feature = client.create_point_feature(layer.id, -122.4194, 37.7749)
    
    # Execute a tool
    result = client.execute_tool("analysis_action", config={}, input_data={})
```

## API Reference

### Authentication

```python
# Login with email and password
auth_response = client.login("user@example.com", "password")

# Refresh access token
refresh_response = client.refresh_access_token()

# Check authentication status
if client.is_authenticated():
    print("Client is authenticated")

# Logout (clear tokens)
client.logout()
```

### Project Management

```python
# Create a project
project = client.create_project("Project Name", "Optional description")

# Get projects with pagination
projects_page = client.get_projects(page=1, per_page=10)

# Get all projects (handles pagination automatically)
all_projects = client.list_projects()

# Get specific project
project = client.get_project(project_id)

# Update project
updated_project = client.update_project(project_id, name="New Name")

# Delete project
client.delete_project(project_id)
```

### Plan Management

```python
from lirays_client import PlanStatus

# Create a plan
plan = client.create_plan(
    project_id=project.id,
    name="Analysis Plan",
    description="Plan description",
    status=PlanStatus.NOT_ASSIGNED
)

# Get plans for a project
plans = client.get_plans_by_project(project.id)

# Update plan status
updated_plan = client.update_plan(plan.id, status=PlanStatus.IN_PROGRESS)
```

### Layer Management

```python
from lirays_client import LayerClass

# Create a layer
layer = client.create_layer(
    plan_id=plan.id,
    lclass=LayerClass.FIBER_24,
    name="24-Fiber Network"
)

# Get layers for a plan
layers = client.get_layers_by_plan(plan.id)

# Get available layer types
layer_types = client.get_layer_types()
```

### Feature Operations

```python
from lirays_client import GeomType

# Create different types of features
point_feature = client.create_point_feature(layer.id, longitude, latitude)

linestring_feature = client.create_linestring_feature(
    layer.id, 
    coordinates=[[-122.4194, 37.7749], [-122.4184, 37.7759]]
)

polygon_feature = client.create_polygon_feature(
    layer.id,
    coordinates=[[
        [-122.4200, 37.7740],
        [-122.4180, 37.7740], 
        [-122.4180, 37.7760],
        [-122.4200, 37.7760],
        [-122.4200, 37.7740]
    ]]
)

# Update feature geometry
updated_feature = client.update_feature(
    feature.id,
    geom_type=GeomType.POINT,
    coordinates=[new_longitude, new_latitude]
)
```

### Tools Execution

```python
# Get available tool actions
actions = client.get_available_actions()

# Simple tool execution
result = client.execute_tool(
    action="analysis_action",
    config={"parameter": "value"},
    input_data={"input": "data"}
)

# Streaming tool execution with progress updates
for update in client.execute_tool_stream(action, config, input_data):
    print(f"Progress: {update.get('progress', 0)}%")
    if update.get('status') == 'completed':
        print("Tool completed!")
        break

# Async execution with callback
def progress_callback(update):
    print(f"Progress: {update.get('progress', 0)}%")

result = client.execute_tool_async(
    action, config, input_data, 
    callback=progress_callback
)
```

## Error Handling

The client provides specific exception types for different error scenarios:

```python
from lirays_client import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    LiRAYSAPIError
)

try:
    client.login("user@example.com", "wrong-password")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
except LiRAYSAPIError as e:
    print(f"API error: {e}")
```

## Configuration

### Client Configuration

```python
# Custom configuration
client = LiRAYSClient(
    base_url="https://custom-api.lirays.com",
    timeout=60.0,  # Custom timeout in seconds
)

# Using environment variables
import os
client = LiRAYSClient(
    base_url=os.getenv("LIRAYS_API_URL", "https://api.lirays.com")
)
```

### Using as Context Manager

```python
# Recommended approach for automatic cleanup
with LiRAYSClient() as client:
    client.login("user@example.com", "password")
    # ... perform operations ...
# Client is automatically closed
```

## Advanced Usage

### Pagination Handling

```python
# Manual pagination
page = 1
while True:
    projects_page = client.get_projects(page=page, per_page=50)
    
    for project in projects_page.resources:
        print(f"Project: {project.name}")
    
    if page >= projects_page.pages:
        break
    page += 1

# Automatic pagination (recommended)
all_projects = client.list_projects()
```

### Bulk Operations

```python
# Create multiple features efficiently
features = []
coordinates_list = [
    [-122.4194, 37.7749],
    [-122.4184, 37.7759],
    [-122.4174, 37.7769]
]

for coords in coordinates_list:
    feature = client.create_point_feature(layer.id, coords[0], coords[1])
    features.append(feature)
```

### Health Monitoring

```python
# Check API health
if client.health_check():
    print("API is healthy")
else:
    print("API is not responding")
```

## Examples

See the `examples/` directory for comprehensive usage examples:

- `basic_usage.py` - Basic API operations and resource management
- `streaming_tools.py` - Tool execution with streaming and progress tracking  
- `context_manager.py` - Using the client as a context manager

## API Reference

For detailed API documentation, refer to the [LiRAYS API OpenAPI specification](https://api.lirays.com/openapi.json).

## Requirements

- Python 3.8+
- httpx >= 0.24.0
- pydantic >= 2.0.0
- python-dateutil >= 2.8.0

## Development

### Setup Development Environment

```bash
git clone https://github.com/lirays/lirays-api-python-client.git
cd lirays-api-python-client

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black lirays_client/
isort lirays_client/

# Type checking
mypy lirays_client/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Email: support@lirays.com
- Documentation: [GitHub Repository](https://github.com/lirays/lirays-api-python-client)
- Issues: [GitHub Issues](https://github.com/lirays/lirays-api-python-client/issues)
