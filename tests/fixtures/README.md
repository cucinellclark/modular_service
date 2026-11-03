# Test fixtures

`manifest.json` lists every fixture: its source, tier, our data type, size, and
sha256. `fetch_fixtures.py` downloads them into `data/` (gitignored). See
[docs/TEST_DATA.md](../../docs/TEST_DATA.md) for why these were chosen.

```bash
python3 tests/fixtures/fetch_fixtures.py --list
python3 tests/fixtures/fetch_fixtures.py --container /vol/patric3/production/containers/ubuntu-176-build12-2.sif   # T0+T1, ~67 MB, ~20 s
python3 tests/fixtures/fetch_fixtures.py --tier T0 --skip-bvbrc     # smoke set only, no container needed
python3 tests/fixtures/fetch_fixtures.py --only portiera_hybrid     # a named set
python3 tests/fixtures/fetch_fixtures.py --tier T2                  # pangolin-data (44 MB)
```

- **Sources**: nf-core/test-datasets pinned to commit `3170f64e` (MIT; sha256
  checked strictly), and BV-BRC genomes via `p3-genome-fasta --contig`
  (sha256 mismatch only warns, since BV-BRC data can change).
- **Tiers**: T0 smoke (~1 MB), T1 realistic-small (~66 MB), T2 optional heavy.
- **Sets** are named groupings for pipeline tests (`sarscov2_samples`,
  `bfragilis_samples`, `portiera_pe`, `portiera_hybrid`, `portiera_genomes`,
  `hs_rnaseq`, `sarscov2_rnaseq_smoke`).
- After a fetch, `data/fixtures_index.json` maps fixture ids and resolved
  sets to absolute paths, ready to plug into pipeline JSON `inputs`. Extracted
  database tarballs are indexed as `<id>:dir`.
- To add a fixture, add an entry to `manifest.json`, then run with
  `--only <id> --update-checksums`.
