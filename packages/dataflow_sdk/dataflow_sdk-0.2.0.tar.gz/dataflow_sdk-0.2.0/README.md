# dataflow-sdk

## Example

```python
from datetime import datetime

from dataflow_sdk import save_items, Record
from dataflow_sdk.entity.model import SinkType

result = {
    'name': 'xiaoming',
    "age": 25,
    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "hello": "world",
    "world": 1121211
}

records = [Record(
    parent_url="https://www.json.cn",
    sink_type=SinkType.ITEM,
    store_key=f"https://www.json.cn{x}/",
    data=result,
    metadata={"name": "gage"},
) for x in range(10)]

save_items('77963b7a931377ad4ab5ad6a9cd718aa', records)
```