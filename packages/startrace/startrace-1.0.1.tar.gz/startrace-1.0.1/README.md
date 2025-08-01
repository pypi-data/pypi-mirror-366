# Star Trace

A program originally created by William Coker for ACU Atom Smashers

## Installation

### Pypi (pip)
This project is on the python install index, meaning you may install it via pip:
```bash
pip install startrace
```
### Release
There are pre-built `.whl` files in the releases section for this project on 
[github](https://github.com/wdc756/StarTrace) available for download. Once downloaded, call
```bash
pip install /location/of/your/file/startrace-x-x-x-py3-none-any.whl
```
### Build from source
Alternatively you may also clone this repository using
```bash 
git clone https://github.com/wdc756/StarTrace.git
```
Then you may make any changes you'd like, and call
```bash
python -m build
```
Note: This is assuming you already have `build`, `setuptools`, and `wheel` installed. If 
this is not the case run `pip install build setuptools wheel` first. Additionally 
there is already a file with unit tests in the `test/` dir. If you wish to run unit 
tests before building, run `pytest` (Assuming it's already installed)

## Usage

StarTrace is a lightweight python module aimed to help manage similarly-named files or objects.
Main usage generally follows this flow:
```python
# To cut down on verbosity, it's easier to just import everything 
from startrace import *
import numpy as np

# Create pattern via Token list
file_pattern = Pattern([
    Token('syn ', 1, Iter(1, 3, 1)),
    Token('.npy')
])

# While the pattern can increment, load each numpy file
while True:
    print(file_pattern.get_pattern())
    values = np.load(file_pattern.get_pattern())

    if not values.increment():
        break
```
This example code will create a file pattern that will load the following files:
```text
syn 1.npy
syn 2.npy
syn 3.npy
```
### Iters
Iters are the most basic dataclass included in StarTrace. They hold three Numbers: `start`, `end`,
and `step`. These values are then used when `Pattern.increment()` is called to either increment
the number or through a list of strings
### Tokens
Tokens are the main dataclass you will interact with when creating Patterns, and they can be 
created using several different arguments.
```python
from startrace import *
import numpy as np

# This will create a token that iterates over numbers 1-10
Token('', 1, Iter(1, 10, 1))
# This will also create a token iterating over 1-10
Token('', 1, (1, 10, 1))
# This creates a Token iterating over 1-9, counting by 3 -> (1, 3, 9)
Token('', 1, (1, 9, 3))

# This creates a Token that iterates over the string list -> 'test', 'hello', 'world'
Token(['test', 'hello', 'world'])
# This creates a Token that iterates over the int values in the list -> 1, 3, 4, 2, 5
list = [1, 3, 4, 2, 5]
Token(list)
# There's also numpy support, so you can enter 1D np.ndarrays for phrases and Token will interpret it
npList = np.arange(1, 10, 1)
Token("I'm a numpy value:", npList)
```
### Patterns
Patterns are the high-level dataclass you'll interact with most once created. It has two 
only two functions: `get_pattern()` and `increment()`. Get Pattern returns a string stitching
all Tokens together with their current number/str values, and Increment moves all numbers up by
one value, one Token at a time. For example
```python
from startrace import *

pat = Pattern([
    Token('syn', 1, (1, 2, 1)),
    Token('_percent', 1, (1, 3, 1))
])

while True:
    print(pat.get_pattern())
    if not pat.increment():
        break
```
will print
```text
syn1_percent1
syn1_percent2
syn1_percent3
syn2_percent1
syn2_percent2
syn2_percent3
```

## License

This project is under the GNU General Public License, feel free to modify or distribute this 
code however you see fit