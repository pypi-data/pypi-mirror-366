# DatabaseTask


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **str** | Add time index | [optional] 
**cron_expr** | **str** |  | [optional] 
**execute_time** | **int** | Add execution time index | [optional] 
**group_id** | **str** | Add group ID index | [optional] 
**id** | **str** |  | [optional] 
**immediate** | **bool** |  | [optional] 
**payload** | **str** |  | [optional] 
**project** | [**DatabaseProject**](DatabaseProject.md) |  | [optional] 
**project_id** | **int** | Task can belong to a project (optional) | [optional] 
**status** | **str** | Add multiple composite indexes | [optional] 
**trace_id** | **str** | Add trace ID index | [optional] 
**type** | **str** | Add composite index | [optional] 
**updated_at** | **str** |  | [optional] 

## Example

```python
from rcabench.openapi.models.database_task import DatabaseTask

# TODO update the JSON string below
json = "{}"
# create an instance of DatabaseTask from a JSON string
database_task_instance = DatabaseTask.from_json(json)
# print the JSON string representation of the object
print DatabaseTask.to_json()

# convert the object into a dict
database_task_dict = database_task_instance.to_dict()
# create an instance of DatabaseTask from a dict
database_task_form_dict = database_task.from_dict(database_task_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


