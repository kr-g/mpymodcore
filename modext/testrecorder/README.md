
# TestRecorder

TestRecorder is a testing tool for testing based on the
[`IPO-Model`](https://en.wikipedia.org/wiki/IPO_model)

## Background

Every software component gets Input, does some Processing, and finally 
produces an Output - meaning also: test procedures can be written that 
they do so in case the software component as such do not produce a readable output.

This output can be captured and saved, and later compared against a new output
what the software produces in a different run.

When there are differences something has changed (incompatible).

Depending on the output, and the code, this tool can be used for both to
- check if the flow logic has changed, and/ or
- if the software component has changed

This is known also as
[`Back-Box Test`](https://en.wikipedia.org/wiki/Black-box_testing).

Depending on the requirements, and the coding, the testing can cover
different levels of granularity, or scopes.

In principle it can be used therefore also for
[`White-Box Test`](https://en.wikipedia.org/wiki/White-box_testing)
when test procedures are written in that way that they inspect the inner
behaviour (or state) of the software component.

