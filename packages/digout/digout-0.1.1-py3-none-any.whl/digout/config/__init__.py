"""Defines the Pydantic models for workflow and step configuration.

This package contains the data models used to define, parse, and validate a
complete workflow configuration. These models serve as the schema for
configuration files (e.g., YAML) and ensure that all components of a workflow,
from individual steps to runtime settings, are correctly specified before
execution.

The main models provided are:

- :py:class:`~step.StepConfig`: Represents the configuration of a single step,
  including its parameters and input sources.
- :py:class:`~workflow.WorkflowConfig`: The top-level model that consolidates all
  steps, streams, and runtime settings into a single, executable workflow
  definition.

"""

from __future__ import annotations
