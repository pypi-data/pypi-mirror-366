# Consumable

Bool that resets to false after use.

## Example

```py
from consumable import Consumable

consumable = Consumable(True)

if consumable:
    print("Consumable is true!!")

if consumable:
    print("Consumable is true!! Should not happen.")
```
