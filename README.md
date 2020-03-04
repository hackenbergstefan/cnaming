[![Build Status](https://travis-ci.org/hackenbergstefan/cnaming.png)](https://travis-ci.org/hackenberstefan/cnaming)
![test](https://github.com/hackenbergstefan/cnaming/workflows/test/badge.svg)
![flake8](https://github.com/hackenbergstefan/cnaming/workflows/flake8/badge.svg)
![coverage](https://github.com/hackenbergstefan/cnaming/workflows/coverage/badge.svg)


# CNaming
Naming convention check for C source files implemented in python with usage of libclang.

## Implemented Naming Conventions

### [Hungarian Naming Convention](https://en.wikipedia.org/wiki/Hungarian_notation)

Despite there are many opinions agains Hungarian notation some projects use it.

Hungarian ruleset is implemented in [hungarian.py](cnaming/rules/hungarian.py).

## How to use it

Run the script `cnaming-check RULESET FILE` to check a file.

### Example

Consider the following C source file:

```c
// tmp.c

#include <stdint.h>

typedef struct
{
    uint32_t A;
    uint32_t dwB;
    uint8_t C;
} sFoo_d;


void fubar(uint32_t dwFoo, uint8_t *prgbFoo)
{
    uint16_t *wX;
    uint8_t *pX;
    sFoo_d *psFoo;
}
```

Running `cnaming-check hungarian tmp.c` exits with code `1` and gives the output:
```
tmp.c:7:18:"uint32_t A": uint32_t starts with dw
tmp.c:9:17:"uint8_t C": uint8_t starts with b
tmp.c:15:19:"uint16_t * wX": pointer starts with p
tmp.c:16:18:"uint8_t * pX": uint8_t starts with b
```
