Inspired by programs that return 1 on success, exesexe lets you wrap a call
to an executable and selectively override its return codes. This allows you,
for example, to use an aberrant installer with configuration management
software that expects programs to return 0 when successful.

exesexe will use the first argument it receives as its own directive, but all
other arguments will be executed without modification. The directive is a
comma-separated list, where each segment may have one of these forms:

```
1      whitelist 1 (convert to 0)
-1=2   substitute -1 with 2
5:8=9  substitute 5, 6, 7, and 8 with 9
!1     blacklist 1 (don't convert 1 at all; convert everything else to 0)
*=3    substitute all others with 3
```

Examples:
  * `1,-1,2=3`
    * Convert 1 and -1 to 0.
    * Convert 2 to 3.

  * `!2`
    * Don't convert 2.
    * Convert everything else to 0.

  * `!-4=2`
    * Don't convert -4.
    * Convert everything else to 2.

  * `*=10`
    * Return 10 no matter what.

The precedence order is whitelists, specific substitutions, blacklists,
then *-substitutions, so `*=4,1=2,!3` would convert 1 to 2 rather than 4 or 0.
The lexical order only matters for overlapping segments, like `1=0,1=2`,
where the rightmost segment overrides the left segments.

Suppose you want to run the executable `foo`. You could issue any of these:

```
exesexe 1 foo         # return 0 if foo returns 1
exesexe 3=4 foo       # return 4 if foo returns 3
exesexe *=0 foo       # always return 0
exesexe !2 foo        # return 0 if foo does not return 2
exesexe !2,3=4 foo    # if foo returns 3, return 4;
                      # else, if foo does not return 2, return 0;
                      # else, pass back foo's real return code
```

You can also use exesexe as a library:

```python
import exesexe
whitelist, blacklist, substitutions = exesexe.parse_directive("1,!2,3=4")
exesexe.interpret(
    "foo --bar",
    whitelist=[1],
    blacklist=[2],
    substitutions={3: 4, "*": 1}
)
```
