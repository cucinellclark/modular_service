# Test UI: BV-BRC-Web "Modular Pipeline" form + modpipe API

The form is a normal BV-BRC-Web service page (Dojo, `AppBase`, the same workspace selectors as every
service), on the BV-BRC-Web branch **`modular-pipeline-ui`** (`cucinellclark/bvbrc_website`):

- `public/js/p3/widget/app/ModularPipeline.js` + `templates/ModularPipeline.html` (route `/app/ModularPipeline`)
- `app.js`: new config `modularPipelineServiceURL` (default `http://localhost:8765`)
- `views/bv-brc-header.ejs`: Services menu > Prototype > Modular Pipeline

Because the ModularPipeline app is not registered with the production app service, the form talks to a
small **modpipe API** (`bin/modpipe serve`, `lib/modpipe/api.py`) that lists templates, validates, and submits
jobs to Slurm on this host by running App-ModularPipeline exactly like `tests/app/run_app.sbatch`. Jobs run with
the signed-in user's BV-BRC token and write to their workspace.

## Running it
1. On the cluster host (where Slurm and the container are), start the API from the ModularService checkout:
   ```bash
   bin/modpipe serve --port 8765            # allowed site origins default to https://dev-5.bv-brc.org and http://localhost:3000;
                                            # pass --origin <scheme://host[:port]> (repeatable) for others
   ```
   Job state lives in `~/.modpipe-ui/` (job params, Slurm logs; token files are mode 600 and deleted when the job ends).
2. If the browser is on another machine, either tunnel the port (`ssh -L 8765:localhost:8765 <cluster host>`)
   or serve on the network over HTTPS so the token isn't sent in the clear:
   ```bash
   bin/modpipe serve --host 0.0.0.0 --port 12005 --self-signed
   ```
   `--self-signed` creates a certificate for this host once (`~/.modpipe-ui/tls/`, key mode 600). Open
   `https://<host>:12005/api/health` in the browser once and accept the warning; after that the form's calls work.
   A website served over https (e.g. https://dev-5.bv-brc.org) can only call an https API. With a real certificate use `--tls-cert cert.pem --tls-key key.pem` instead. Set
   `modularPipelineServiceURL` to `https://<host>:12005`.
3. Run BV-BRC-Web from the `modular-pipeline-ui` branch with your `p3-web.conf` (add
   `"modularPipelineServiceURL": "http://localhost:8765"` if you need a different URL). Run it **unbuilt**
   (development mode): the new widget isn't in the built release layers.
   **dev-5 setup:** `https://dev-5.bv-brc.org` is an nginx/Cloudflare proxy that forwards plain HTTP to
   `ash:12005`. Run `bin/modpipe serve --host 0.0.0.0 --port 12005` (no TLS; the proxy terminates HTTPS) and set
   `modularPipelineServiceURL` to `https://dev-5.bv-brc.org`.
4. Sign in, open **Services > Prototype > Modular Pipeline** (`/app/ModularPipeline`).

## Using the form
- **Template**: 17 curated pipelines grouped by category; the step chain is shown under the description.
- **Inputs**: per input, pick a source (workspace read pairs per sample, SRA accessions, workspace file(s),
  BV-BRC genome IDs/group, feature group/IDs, pasted FASTA, bundled reference). Collections get "+ Add sample".
- **Options**: optional steps (checkboxes) and the template's exposed parameters (typed widgets; string
  parameters enforce their allowed pattern; database parameters list registry choices).
- **Advanced JSON**: edit the instantiated pipeline directly (custom pipelines); Validate/Run use it as-is.
- **Validate**: server-side check: errors, notes (e.g. auto-inserted converters), estimated CPUs/memory/runtime.
- **Run**: submits; the **My Modular Pipeline jobs** panel (auto-refresh 20 s) shows Slurm state, pipeline
  status, a link to the result folder and the job log.

## API
`GET /api/health | /api/templates | /api/modules | /api/databases?type=`, `POST /api/instantiate | /api/validate`,
`POST /api/submit` (auth), `GET /api/jobs` (auth), `GET /api/jobs/<id>/log` (auth). See `lib/modpipe/api.py`;
tests in `tests/unit/test_api.py`.

Prototype limits: tokens are trusted as presented (workspace and data API still enforce access); a user only
sees their own jobs; jobs run as the Unix user that runs `modpipe serve`.
