---
name: stake-engine-validation
description: Validate SDK changes, simulation books, lookup tables and frontend event contracts.
---
Read docs/ENGINE_CONTRACT.md and the actual SDK types/serialization. Run
scripts/test-setup.ps1 for Python tests and a bounded seeded sample. Verify IDs,
event indexes, board shape, integer payout units, bounds and compression.
Check that lookup IDs match book IDs and weights are valid. Review replay
handlers against every emitted event type. Do not treat the development sample
as a production distribution or evidence of RTP. Run upstream RGS checks only
against a complete generated game and record their actual result.
