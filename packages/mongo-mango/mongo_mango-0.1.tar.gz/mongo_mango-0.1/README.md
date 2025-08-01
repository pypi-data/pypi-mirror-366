# easy_db
 
easy_db is a simple and easy-to-use Python library for interacting with MongoDB databases. It provides a convenient way to define schemas, create data objects, and perform basic database operations.

## Installation

You can install easy_db using pip:

```bash
pip install easy_db
```

## Usage

Here is an example of how to use easy_db:

```python
from easy_db import Database, Schema
from datetime import datetime
import random

# Define a schema
schema = Schema(
    {
        'name': {
            'type': str,
            'default': 'John Doe',
            'apply': lambda x: x.upper()
        },
        'age': {
            'type': int,
            'default': 18,
            'apply': lambda x: random.randint(18, 60),
            'required': True
        },
        'email': {
            'type': str,
            'default': 'example@example.com'
        },
        'posted_at': {
            'type': str,
            'default': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'apply': lambda x: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }
)

# Create a database instance
db = Database('mongodb+srv://username:password@cluster.mongodb.net/test', 'test', 'test')

# Insert data into the database
for i in range(10):
    db.create(schema, {})

# Print all data in the collection
db.printAll()
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
