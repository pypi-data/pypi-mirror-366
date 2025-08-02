# T-Toolbox

My toolbox for python.

## Freeform

Freeform is a class that can turn any set of arguments into fields.

### Examples

```py
# Import the Freeform class
from t_toolbox import Freeform

# Create a Freeform instance with class fields
my_data = Freeform(name="John", age=30, city="New York")

# Access the class fields
print("Name:", my_data.name)
print("Age:", my_data.age)
print("City:", my_data.city)

```

## Consumable

Bool that resets to false after use.

### Examples

```py
from consumable import Consumable

consumable = Consumable(True)

if consumable:
    print("Consumable is true!!")

if consumable:
    # Will not activate, previous use sets consumable to False!
    print("Consumable is true again!! Should not happen.")
```
