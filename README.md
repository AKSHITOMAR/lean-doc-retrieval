# Lean Documentation Retrieval

A minimal experimental prototype for studying whether providing relevant Lean documentation to an LLM helps it generate valid Lean 4 proofs.

## Current Experiment

The prototype compares two settings:

1. LLM generates Lean proof without documentation.
2. LLM generates Lean proof with a relevant documentation snippet.

Each generated proof is verified using the Lean 4 compiler.

## Current Test Cases

* And
* Or
* Exists
* intro
* apply

## Project Status

This is the initial prototype. The current `docs/` files contain manually created documentation snippets used to validate the retrieval pipeline.

The next stage is to replace these snippets with actual Lean/Mathlib documentation retrieval and repeat the experiments.

## Tech Stack

* Python
* OpenAI API
* Lean 4
* Lean compiler
