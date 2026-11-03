# Shell-injection hardening

Users submit pipelines with their own parameter values, file names, sample ids and step names. These reach
shell commands (module templates, job scripts) and generated code (the Snakefile), so every path is defended:

| Where untrusted text goes | Defense | Enforced by |
|---|---|---|
| Module command templates | every untrusted value is piped through `| q` (shell quoting); string parameters also need a `pattern` | `modpipe lint`: **hostile rendering** (below) is an error; a string param without `pattern` is a warning (all current modules have one) |
| String parameter values | full-match against the parameter's `pattern`; reject control characters (newlines, tabs, NUL) and values > 1000 chars | `modpipe validate` (and so preflight) |
| int / float / bool / enum / database params | type, range, enum membership, registry id | `modpipe validate` |
| Step ids, input names, output names | `[A-Za-z][A-Za-z0-9_-]{0,63}`: they become directories, Snakefile rule names, workspace paths | `modpipe validate` |
| Sample ids, genome ids, SRA accessions | `[A-Za-z0-9][A-Za-z0-9_.-]*`, `\d+\.\d+`, `[SED]RR\d+`; sample keys are additionally sanitized when staged | `modpipe validate`, `materialize._safe` |
| Input file paths / labels in templates | always `| q` (checked by hostile rendering) | `modpipe lint` |
| job.sh wrapper | work dir, decompression paths and required-output paths are `shlex.quote`d | `materialize.write` |
| Snakefile | paths and `shell:` strings are emitted with Python `repr()`, never hand-quoted | `executors.SnakemakeExecutor` |
| Perl shell, staging | external programs run with argument lists (`IPC::Run`, `subprocess` lists), never through a shell | code review |

## Hostile rendering (`template.lint_shell_safety`)
Lint renders every command variant with booby-trapped values: free-text params, every input path and every
label become a string containing a space, `;`, `$( )`, backticks, quotes, `|`, `&`, `>` and globs. It then parses the
command as the shell would (`shlex.split`) and requires each trap value to come back as **one intact
argument**. Unquoted values, values in double quotes (where `$(...)` still runs) and broken quoting all fail.

## Writing templates safely
- Pipe anything that comes from inputs or string params through `| q`: `{{ inputs.reads.r1 | q }}`,
  `{{ params.organism | q }}`, `{{ inputs.contigs.label | q }}`.
- Give every string parameter a `pattern` that matches only legitimate values (it is a full match), e.g.
  `pattern: "auto|[0-9]{1,3}(,[0-9]{1,3})*"`.
- Output paths (`outputs.*`), database paths (`dbs.*`), ints/floats/bools/enums and `cpu`/`memory_gb` are trusted,
  because they come from descriptors, the registry or validated values.

Tests: `tests/unit/test_shell_safety.py` covers the lint (it catches unquoted, double-quoted and single-quoted
values), the patterns, identifier and source-id rejection, and a real run whose input file is named
`r 1;touch PWNED;$(touch PWNED2)`touch PWNED3`.fa` with a hostile parameter value. Nothing is executed.
