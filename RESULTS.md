# Evaluation Results

Gemma 4 extraction and matching on 12 hand-labeled posts.

- Case 01: expected `p06`; ranked `p06, p23, p02`; top-1 True; top-3 True.
- Case 02: expected `p02`; ranked `p01, p25, p09`; top-1 False; top-3 False.
- Case 03: expected `p03`; ranked `p28, p08, p17`; top-1 False; top-3 False.
- Case 04: expected `p04`; ranked `p07, p24, p14`; top-1 False; top-3 False.
- Case 05: expected `p05`; ranked `p09, p24, p07`; top-1 False; top-3 False.
- Case 06: expected `p06`; ranked `p01, p25, p09`; top-1 False; top-3 False.
- Case 07: expected `p07`; ranked `p04, p27, p22`; top-1 False; top-3 False.
- Case 08: expected `p09`; ranked `p02, p29, p05`; top-1 False; top-3 False.
- Case 09: expected `p11`; ranked `p14, p24, p07`; top-1 False; top-3 False.
- Case 10: expected `p16`; ranked `p28, p09, p22`; top-1 False; top-3 False.
- Case 11: expected `p19`; ranked `p15, p29, p06`; top-1 False; top-3 False.
- Case 12: expected `p27`; ranked `p03, p14, p20`; top-1 False; top-3 False.

- Top-1 agreement: 1/12 (8.3%)
- Top-3 agreement: 1/12 (8.3%)

This small hand-labeled set is a smoke test, not a measure of real-world matching quality.
