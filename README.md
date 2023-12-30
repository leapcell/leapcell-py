# Python Library

## Installation

```bash
pip install leapcell
```

## Usage

### Preparation

Leapcell uses an `API Token` for API access. Learn more about API Tokens [here](https://docs.leapcell.com/api/overview#authentication).

### Initializing the Client

You can either place the API Token in the environment variables or pass it directly.

- `REPO_NAME`: Your repository name, e.g., if it's `leapcell.io/issac/blog`, then `REPO_NAME` is `issac/blog`.
- `TABLE_ID`: Your table ID, e.g., if your table is `leapcell.io/issac/blog/table/12345678`, then `TABLE_ID` is `12345678`.

By default, the table uses the table name. If you want to use the table ID, set `name_type` to `id`.

```python
from leapcell import Leapcell
import os

# Get API token from env
api_token = os.environ.get("LEAPCELL_API_KEY")

# Initialize client with the token
leapclient = Leapcell(api_token)

# Initialize table instance
table = leapclient.table("{{REPO_NAME}}", "{{TABLE_ID}}")

# Initialize table instance with table id
# table = leapclient.table("{{REPO_NAME}}", "{{TABLE_ID}}", name_type="id")
```

### Getting Table Meta Info

```python
# Get table meta info
print(table.meta().toJSON())

# Output:
# {'resource': 'issac/blog', 'table_id': 'tbl1726117346872295424', 'fields': {'category': <field id: fld129608161 name: category, type: LABELS>, 'content': <field id: fld3419043789 name: content, type: LONG_TEXT>, 'cover': <field id: fld2448453439 name: cover, type: IMAGES>, 'summary': <field id: fld4203215423 name: summary, type: LONG_TEXT>, 'title': <field id: fld1188108910 name: title, type: STR>}}
```

### Creating a Record

Leapcell automatically converts data based on the table's field types. If the conversion fails, an exception is raised.

```python
# Create a record
record = table.create({"title": "hello issac"})

# Output:
# {'record_id': '60387060-6b27-47b4-b7e6-2770742654b8', 'data': {'title': 'hello issac'}, 'create_time': 1703150140, 'update_time': 1703150140}
```

### Updating a Record

```python
# Update a record
record["title"] = "hello issac again"
record.save()

# Output:
# {'record_id': '60387060-6b27-47b4-b7e6-2770742654b8', 'data': {'title': 'hello issac again'}, 'create_time': 1703150140, 'update_time': 1703150140}
```

### Getting a Record By ID

```python
# Get a record by ID
record = table.get_by_id(record.id)

# Output:
# {'record_id': '60387060-6b27-47b4-b7e6-2770742654b8', 'data': {'category': None, 'content': None, 'cover': None, 'summary': None, 'title': 'hello issac again'}, 'create_time': 1703150140, 'update_time': 1703150491}
```

### Deleting a Record By ID

```python
# Delete a record
record.delete()

# or

table.delete_by_id(record.id)
```

### Getting a Record By Filter

Leapcell supports various query methods. Use `where` to perform queries, and fields are represented by `table["field_name"]`.

Get a record if the title is "hello":

```python
# Get record if title is hello
records = table.select().where(table["title"] == "hello").limit(10).offset(0).first()
```

#### AND

Get a record if the title is "hello" and the category is "tutorial":

```python
records = table.select().where(
    (table["title"] == "hello" & table["category"] == "tutorial")
).limit(10).offset(0).first()
```

#### OR

Get a record if the title is "hello" or the category is "tutorial":

```python
records = table.select().where(
    (table["title"] == "hello" | table["category"] == "tutorial")
).limit(10).offset(0).first()
```

### Field Operators

For information about the operators supported by fields, refer to [Field Operators](https://docs.leapcell.com/api/field-operators).

The mapping between `op` and Python operators is as follows:

```python
# op: eq
table["title"] == "hello"

# op: gt
table["title"] > "hello"

# op: gte
table["title"] >= "hello"

# op: lt
table["title"] < "hello"

# op: lte
table["title"] <= "hello"

# op: neq
table["title"] != "hello"

# op: contain
table["title"].contain("hello")

# "hello" in table["title"]

# op: in
table["title"].in_(["hello", "world"])

# op: not_in
table["title"].not_in(["hello", "world"])

# op: is_null
table["title"].is_null()

# op: is_not_null
table["title"].is_not_null()
```

### Getting Records and Sorting

```python
records = table.select().where(table["title"] == "hello").order_by(table['title'].asc()).query()

records = table.select().where(table["title"] == "hello").order_by(table['title'].desc()).query()
```

### Get Records and Pagination

Retrieve records with a limit of 10 and an offset of 0.

```python
records = table.select().where(table["title"] == "hello").limit(10).offset(0).query()
```

### Update Record By Filter

Update records where the title is "hello issac again."

```python
# Update records
table.select().where(
    {
        "title": "hello issac again",
    }
).update(
    {
        "title": "here is leapcell",
    }
)
```

### Delete Record By Filter

Delete records where the title is "hello issac again."

```python
# Delete records
table.select().where(
    {
        "title": "hello issac again",
    }
).delete()
```

### Bulk Create

Bulk create records.

```python
# Bulk create
records = table.bulk_create(
    [
        {
            "title": "hello issac",
        },
        {
            "title": "hello jude",
        },
    ]
)
```

### Search

By default, the search is performed on all fields. If you want to specify fields, use the `fields` parameter.

Similar to a search engine, Leapcell tokenizes search keywords and performs searches. When you search for "hello issac," Leapcell searches for "hello" and then "issac," finally merging the results.

```python
# Search
records = table.search("hello")

# Search for "hello" and "jude"
records = table.search("hello jude")

# Search in the "title" field
records = table.search("hello", fields=["title"])

# Pagination
records = table.select().limit(10).offset(0).search("hello")
```

### Image Upload

Leapcell supports image uploads. You can upload images to Leapcell and save the image URL to the table.

Images will be uploaded to the CDN.

```python
import requests

# Fetch image
image_req = requests.get(
    "https://leapcell-dev-bucket.s3.amazonaws.com/920417ee6a70435084fe6b40d58dad4e.jpeg"
)

image = image_req.content
resp = table.upload_file(image)
# Output:
# LeapcellFile(id=img07201ffc5ce24f85abb6fabc9e63fa80-file.jpeg, link=https://cdn1.leapcell.io/img07201ffc5ce24f85abb6fabc9e63fa80-file.jpeg, width=0, height=0)

# Save image ID to the table
record["cover"] = resp.id
record.save()
```

Upload multiple images.

```python
import requests

# Fetch image
image_req = requests.get(
    "https://leapcell-dev-bucket.s3.amazonaws.com/920417ee6a70435084fe6b40d58dad4e.jpeg"
)

resp = table.upload_files([image, image])
# Output:
# [{"id": "imge8ba2e9ba6b64afaab953239869fb564-files.jpeg", "link": "https://cdn1.leapcell.io/imge8ba2e9ba6b64afaab953239869fb564-files.jpeg", "meta": {"width": 0, "height": 0}}, {"id": "img31277a9417044d2c80fee16f42e6b654-files.jpeg", "link": "https://cdn1.leapcell.io/img31277a9417044d2c80fee16f42e6b654-files.jpeg", "meta": {"width": 0, "height": 0}}]

record["cover"] = [resp[0].id, resp[1].id]
record.save()
```
