[![Build Status](https://travis-ci.org/hackenbergstefan/cnaming.png)](https://travis-ci.org/hackenberstefan/cnaming)
![test](https://github.com/hackenbergstefan/cnaming/workflows/test/badge.svg)
![flake8](https://github.com/hackenbergstefan/cnaming/workflows/flake8/badge.svg)
![coverage](https://github.com/hackenbergstefan/cnaming/workflows/coverage/badge.svg)


# CNaming
Naming convention check for C source files implemented in python with usage of libclang.

## Implemented Naming Conventions

### [Hungarian Naming Convention](https://en.wikipedia.org/wiki/Hungarian_notation)

Despite there are many opinions agains Hungarian notation some projects use it.


## How to use it

Run the script `cnaming-check FILE` to check a file.

For instance: Consider the following C source file:

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

Running `cnaming-check tmp.c` exits with code `1` and gives the output:
```
7:14: "A" at "uint32_t A" does not match "dw([A-Z][a-z0-9]*)+"
9:13: "C" at "uint8_t C" does not match "b([A-Z][a-z0-9]*)+"
15:15: Pointername "wX" does not match its type "uint16_t *"
16:14: "X" at "uint8_t pX" does not match "b([A-Z][a-z0-9]*)+"
```
