"""Core package of the **DIGOUT** library.

This package contains the abstractions needed to describe a workflow and to
run it.

Design
------

Key Concepts
~~~~~~~~~~~~

* **Streams**: see :py:class:`.stream.StreamProtocol`.
  A stream is a data object that can be split into independent **chunks**,
  that can be processed in parallel.

* **Steps**: see :py:class:`.step.StepProtocol`.
  A step consumes one or more **sources**, receives a **context**, and produces a
  single **target**.
  Two kinds exist (:py:class:`.step.StepKind`):

  * :py:attr:`~.step.StepKind.STREAM`: runs once and works on whole streams.
  * :py:attr:`~.step.StepKind.CHUNK`: runs once per chunk.

* A **context**: see :py:class:`.context.ContextProtocol`.
  A context manages and shares information across steps.
  During the chunk phase a dedicated context is derived for each chunk.
  Since steps are static, apart from the sources, the context is the only object
  that can carry dynamic information, such as the chunk index or name.
  During the chunking phase, a dedicated context is created for each chunk.
  Because steps are static, the context is the sole mechanism for providing
  them with dynamic, chunk-specific data (like an index or name) before runtime.

Execution Model
~~~~~~~~~~~~~~~

A generic workflow runs in two distinct phases:

1. **stream phase**: every stream step runs once to build or process the required
   streams.
2. **chunk phase**: the streams are split and every chunk step runs once for
   each chunk. This phase can run in parallel.


The following components run these phases:

* **Orchestrator**, see :py:class:`.orchestrator.OrchestratorProtocol`.
  Executes a **runnable workflow** (either the stream workflow or a chunk
  workflow).

* **Scheduler**, see :py:class:`.scheduler.SchedulerProtocol`.
  Breaks a chunk workflow into per-chunk jobs and calls the orchestrator for
  each of them.


Workflow Objects
~~~~~~~~~~~~~~~~

Workflows are defined in :py:mod:`digout.core.workflow`. Each workflow contains
a **context** and a directed-acyclic graph (DAG) of steps and data targets.

* :py:class:`.workflow.GenericWorkflow`: Full DAG containing both stream and chunk
  steps; not directly runnable.
* :py:class:`.workflow.RunnableWorkflow`: A DAG that contains **only stream**
  *or* **only chunk** steps and data; runnable by an orchestrator.
* :py:class:`.workflow.ChunkWorkflow`
  Special holding all chunk workflows. It yields a **runnable workflow** for a
  specific chunk via :py:meth:`.workflow.ChunkWorkflow.select_chunk`.


High-level Runner
~~~~~~~~~~~~~~~~~

The runner wires a *generic workflow*, an *orchestrator* and an optional
*scheduler*:

1. Extracts and runs the **stream workflow** with the **orchestrator**.
2. Builds the **chunk workflow** from the stream results.
3. Executes:

   * a single chunk via :py:meth:`.runner.Runner.orchestrate_chunk`, or
   * all chunks via :py:meth:`.runner.Runner.schedule`.

All public interfaces are defined as **protocols** so you can supply your own
implementations.
"""

from __future__ import annotations
