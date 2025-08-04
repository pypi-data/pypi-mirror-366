"""Provide the data models for streams and their corresponding chunks.

This package defines the Pydantic models that represent collections of data
(streams) and the individual, processable units they are divided into (chunks).

A "stream" is a model that conforms to the
:py:class:`~digout.core.stream.StreamProtocol`, managing a full dataset and the
logic for partitioning it into "chunks".
"""

from __future__ import annotations
