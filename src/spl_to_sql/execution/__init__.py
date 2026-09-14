"""SQL execution module — Stage 5 of the spl-to-sql pipeline.

Handles executing generated SQL against a target database, with
exponential backoff retry and an error feedback loop that sends
execution errors back to the LLM for correction.

TODO: Add connection pooling support.
"""
