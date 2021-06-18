---
layout: post
title: exception
---

# ref
https://itanium-cxx-abi.github.io/cxx-abi/abi-eh.html

# landing pad
landing pad
:
A section of user code intended to catch, or otherwise clean up after, an exception. It gains control from the exception runtime via the personality routine, and after doing the appropriate processing either merges into the normal user code or returns to the runtime by resuming or raising a new exception.

# personality
Lastly, a language and vendor specific personality routine will be stored by the compiler in the unwind descriptor for the stack frames requiring exception processing. The personality routine is called by the unwinder to handle language-specific tasks such as identifying the frame handling a particular exception.


# unwind process
The runtime framework then starts a two-phase process:

In the search phase, the framework repeatedly calls the personality routine, with the _UA_SEARCH_PHASE flag as described below, first for the current PC and register state, and then unwinding a frame to a new PC at each step, until the personality routine reports either success (a handler found in the queried frame) or failure (no handler) in all frames. It does not actually restore the unwound state, and the personality routine must access the state through the API.
If the search phase reports failure, e.g. because no handler was found, it will call terminate() rather than commence phase 2.
If the search phase reports success, the framework restarts in the cleanup phase. Again, it repeatedly calls the personality routine, with the _UA_CLEANUP_PHASE flag as described below, first for the current PC and register state, and then unwinding a frame to a new PC at each step, until it gets to the frame with an identified handler. At that point, it restores the register state, and control is transferred to the user landing pad code.

# llvm doc
https://llvm.org/docs/ExceptionHandling.html

