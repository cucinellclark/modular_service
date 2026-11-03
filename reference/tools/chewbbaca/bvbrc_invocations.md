# BV-BRC invocations of `chewBBACA.py` (chewbbaca)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 10 hunk(s) in 3 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `plbin/p3x-compute-cgmlst.pl`
- `pybin/core-genome-mlst-utils.py`
- `workflows/bvbrc_CoreGenomeMLST/snakefile/run_cgMLST_snakefile`

## `plbin/p3x-compute-cgmlst.pl:250`

```
    244  
    245              if (!$do_cluster) {
    246          print STDERR "Skipping clustering — allele call quality below ${cluster_threshold}%.\n";
    247          push(@{$gto_in->{sequence_types}}, $sequence_typing);
    248          } else {
    249  
>>  250              # Join new allele call with master allele call using chewBBACA JoinProfiles
    251              my $master_table = application_backend_dir . "/CoreGenomeMLST/precomputed_clusters/refs/" . lc($dir_name) . "_11_25_2025_joined.tsv";
    252              my $master_joined = "$tmp_dir/master_joined.tsv";
    253              my $copy_of_master = "$tmp_dir/master_copy.tsv";
    254  
    255              run_cmd(["cp",  $master_table, $copy_of_master], "Copy Master Table");
    256  
    257              run_cmd([
>>  258                  "chewBBACA.py", "JoinProfiles",
    259                  "--profiles", $copy_of_master, $new_allele_call,
    260                  "--output-file", $master_joined
    261              ], "Join Profiles");
    262  
    263              run_cmd([
    264                  "core-genome-mlst-utils",
    265                  "clean-allelic-profile", $master_joined
    266              ], "Clean Allele Call");
    267  
    268              my $precomputed_clusters_dir  = application_backend_dir . "/CoreGenomeMLST/precomputed_clusters/";
    269              my $precomputed_clusters_path_npz = $precomputed_clusters_dir . lc($dir_name) . ".cgMLSTv1.npz";
    270              my $precomputed_clusters_path_hcc = $precomputed_clusters_dir . lc($dir_name) . ".cgMLSTv1.HierCC.gz";
```

## `plbin/p3x-compute-cgmlst.pl:145`

```
    139      my $clean_fasta_dir = "$tmp_dir/clean_fastas";
    140      my $allele_call_out = "$tmp_dir/new_genomes_allele_call/";
    141      my $schema_path = application_backend_dir . "/CoreGenomeMLST/chewbbaca_schemas/" . $dir_name;
    142      
    143      mkdir $clean_fasta_dir or die "Cannot create clean fastas directory: $!\n";
    144      
>>  145      # rename to be certain it ends with 'fasta' for chewBBACA
    146      run_cmd(["cp", "$in_file", "$clean_fasta_dir/input.fasta"], "Add extension");
    147  
    148      # new genome allele call
    149      my @allele_call_cmd = (
>>  150          "chewBBACA.py", "AlleleCall",
    151          "--input-files", $clean_fasta_dir,
    152          "--schema-directory", $schema_path,
    153          "--output-directory", $allele_call_out,
    154          "--cpu", "1",
    155          "--output-unclassified",
    156          "--output-missing",
    157          "--output-novel",
    158          "--no-inferred"
    159      );
    160      run_cmd(\@allele_call_cmd, "Allele Call");
    161      
    162      # Check percent of loci have an exact allele match
```

## `workflows/bvbrc_CoreGenomeMLST/snakefile/run_cgMLST_snakefile:126`

```
    120         new_genomes_allele_call_results = "{}/new_genomes_allele_call/results_alleles.tsv".format(work_dir),
    121      output:
    122          genome_group_specific_existing_allele_results = "{}/genome_group_results.tsv".format(work_dir),
    123      shell:
    124          """
    125          # 1 join all alleles in the genome group
>>  126          chewBBACA.py JoinProfiles \
    127              -p {params.new_genomes_allele_call_results} {input.pre_processed_from_api} \
    128              -o {output.genome_group_specific_existing_allele_results}
    129          """
    130  
    131  
    132  rule extract_cgMLST:
    133      input:
    134          allele_call_complete_touchpoint
    135      params:
    136          extract_cgmlst_dir = directory("{}/extract_cg_mlst/".format(output_dir)),
    137          final_allele_results = final_allele_result
    138      output:
    139          extract_cgmlst_out = "{}/extract_cg_mlst/presence_absence.tsv".format(output_dir),
    140          loci_list = "{}/extract_cg_mlst/cgMLSTschema95.txt".format(output_dir)
    141      shell:
    142          """
    143          mkdir -p {params.extract_cgmlst_dir}
    144  
>>  145          chewBBACA.py ExtractCgMLST \
    146              --input-file {params.final_allele_results} \
    147              --output-directory {params.extract_cgmlst_dir}
    148          """
    149  
    150  rule run_allele_call_evaluator:
    151      input:
    152          allele_call_complete_touchpoint
    153      params:
    154          schema_dir = schema_path,
    155          allele_call_input_dir_ = allele_call_input_dir,
    156          allele_evaulator_out = directory("{}/allele_call_evaulator".format(output_dir)),
    157      output:
    158          #allele_call_report = "{}/allele_call_evaulator/allelecall_report.html".format(output_dir),
    159          touchpoint = "{}/allelecall_evaulation_complete.txt".format(work_dir)
    160      shell:
    161          """
>>  162          chewBBACA.py AlleleCallEvaluator \
    163              --input-files {params.allele_call_input_dir_} \
    164              --schema-directory {params.schema_dir} \
    165              --output-directory {params.allele_evaulator_out} \
    166              --cpu 4
    167  
    168          touch {output.touchpoint}
    169          """
    170     
    171  rule run_grapetree_cli:
    172      input:
    173          allele_call_complete_touchpoint = allele_call_complete_touchpoint,
    174          config = "{}/config.json".format(current_directory),
```

## `pybin/core-genome-mlst-utils.py:265`

```
    259      coverage_df = pd.DataFrame(records).set_index("genome_id")
    260  
    261      return genome_ids, loci_ids, df, coverage_df
    262  
    263  
    264  # ---------------------------------------------------------------------------
>>  265  # Distance calculation — exact replication of chewBBACA's pipeline
    266  # ---------------------------------------------------------------------------
>>  267  # These functions replicate the logic from chewBBACA's:
    268  #   - CHEWBBACA/utils/iterables_manipulation.py  (replace_chars)
    269  #   - CHEWBBACA/ExtractCgMLST/determine_cgmlst.py (binarize_matrix, presAbs, compute_cgMLST)
    270  #   - CHEWBBACA/utils/distance_matrix.py          (compute_distances)
    271  #   - CHEWBBACA/AlleleCallEvaluator/evaluate_calls.py (pipeline orchestration)
    272  # ---------------------------------------------------------------------------
    273  
    274  def _chewbbaca_replace_chars(column, missing_char='0'):
>>  275      """Mask a single column of allelic calls — exact replica of chewBBACA's
    276      iterables_manipulation.replace_chars.
    277  
    278      Applied column-by-column via DataFrame.apply(), matching the way
>>  279      chewBBACA invokes it: ``profiles_matrix.apply(im.replace_chars)``.
    280  
    281      Steps:
    282        1. Strip 'INF-' prefix from inferred alleles  (INF-5  -> 5)
    283        2. Strip '*'    prefix from Chewie-NS alleles  (*5     -> 5)
    284        3. Replace all remaining non-numeric values    (LNF, ASM, ... -> 0)
    285      """
    286      replaced_inf = column.replace(to_replace='INF-', value='', regex=True)
    287      replaced_ns = replaced_inf.replace(to_replace=r'\*', value='', regex=True)
    288      replaced_special = replaced_ns.replace(to_replace=r'\D+.*',
    289                                             value=missing_char, regex=True)
    290      return replaced_special
    291  
    292  
    293  def _chewbbaca_binarize(column):
    294      """Convert a column to presence (1) / absence (0) — exact replica of
>>  295      chewBBACA's determine_cgmlst.binarize_matrix."""
    296      return np.int64(pd.to_numeric(column) > 0)
    297  
    298  
    299  def _chewbbaca_above_threshold(column, column_length, threshold):
    300      """Test whether a locus is present at or above *threshold* — exact replica
>>  301      of chewBBACA's determine_cgmlst.above_threshold."""
    302      return (np.sum(column) / column_length) >= threshold
    303  
    304  
    305  def _compute_distance_matrix(np_matrix):
    306      """Compute a symmetric pairwise allelic distance matrix — exact replica
>>  307      of chewBBACA's distance_matrix.compute_distances.
    308  
    309      For each pair of samples, the distance is the number of loci where both
    310      have a non-zero (exact) allele AND those alleles differ.
    311  
    312      Parameters
    313      ----------
    314      np_matrix : np.ndarray, shape (n_samples, n_loci), dtype int32
    315  
    316      Returns
    317      -------
    318      dist_matrix : np.ndarray, shape (n_samples, n_samples), dtype int32
    319      """
```

## `workflows/bvbrc_CoreGenomeMLST/snakefile/run_cgMLST_snakefile:99`

```
     93          clean_fasta_dir_ = clean_fasta_dir,
     94          schema_dir = schema_path,
     95      output:
     96          touchpoint = "{}/new_genomes_allele_call_complete.txt".format(work_dir),
     97      shell:
     98          """
>>   99          chewBBACA.py AlleleCall \
    100              --input-files {params.clean_fasta_dir_} \
    101              --schema-directory {params.schema_dir} \
    102              --output-directory {params.allele_call_out} \
    103              --cpu 4 \
    104              --output-unclassified \
    105              --output-missing \
    106              --output-novel \
    107              --no-inferred
    108          
    109          touch {output.touchpoint}
    110          """
    111  
```

## `pybin/core-genome-mlst-utils.py:175`

```
    169      extracted_content = re.findall(r'<body>(.*?)</body>', plotly_html_content, re.DOTALL)
    170      plotly_graph_content = extracted_content[0] if extracted_content else ''
    171      return plotly_graph_content
    172  
    173  
    174  # ---------------------------------------------------------------------------
>>  175  # Classification codes chewBBACA uses for missing / problematic loci
    176  # ---------------------------------------------------------------------------
    177  MISSING_CODES = {"LNF", "ASM", "ALM", "NIPH", "NIPHEM", "PLOT3", "PLOT5"}
    178  
    179  
    180  # ---------------------------------------------------------------------------
    181  # cgMLST report helper functions
    182  # ---------------------------------------------------------------------------
    183  
    184  def create_cgmlst_metadata_table(metadata_json, tsv_out):
    185      """Load genome metadata, keeping genome_id dots intact (not converted to underscores).
    186  
    187      Parameters
```

## `pybin/core-genome-mlst-utils.py:220`

```
    214  def parse_result_alleles(result_alleles_tsv):
    215      """Read result_alleles.tsv and return summary information.
    216  
    217      Parameters
    218      ----------
    219      result_alleles_tsv : str
>>  220          Path to chewBBACA AlleleCall result_alleles.tsv.
    221  
    222      Returns
    223      -------
    224      genome_ids : list of str
    225          Sample identifiers (first column, underscores replaced with periods).
    226      loci_ids : list of str
    227          Locus identifiers (header row, columns 1 onwards).
    228      raw_df : pd.DataFrame
    229          Raw DataFrame with original values (genome IDs as index).
    230      coverage_df : pd.DataFrame
    231          Per-sample counts of: exact, INF, and each missing code.
    232      """
```

## `pybin/core-genome-mlst-utils.py:341`

```
    335      return dist_matrix
    336  
    337  
    338  def chewbbaca_distance_pipeline(result_alleles_tsv):
    339      """Full chewBBACA-compatible distance computation pipeline.
    340  
>>  341      Replicates the exact sequence of operations from chewBBACA's
    342      AlleleCallEvaluator/evaluate_calls.py:
    343  
>>  344        1. Read allelic profiles (letting pandas infer dtypes, matching chewBBACA)
    345        2. Mask with column-by-column apply of replace_chars
    346        3. Compute presence-absence matrix (binarize_matrix)
    347        4. Determine cgMLST at 100% threshold (loci present in ALL samples)
    348        5. Compute symmetric distance matrix on cgMLST loci only
    349  
    350      Parameters
    351      ----------
    352      result_alleles_tsv : str
>>  353          Path to chewBBACA result_alleles.tsv.
    354  
    355      Returns
    356      -------
    357      genome_ids : list of str
    358          Sample identifiers (original, with underscores).
    359      genome_ids_display : list of str
    360          Sample identifiers (underscores replaced with periods, for display).
    361      cgmlst_loci : list of str
    362          Locus identifiers in the cgMLST-100%.
    363      dist_matrix : np.ndarray, shape (n, n), dtype int32
    364          Symmetric pairwise distance matrix.
    365      """
>>  366      # Step 1 — Read profiles matching chewBBACA
    367      # chewBBACA: pd.read_csv(file, header=0, index_col=0, sep='\t', low_memory=False)
    368      # pandas 2.x ignores dtype for the index column when index_col is used,
    369      # causing numeric-looking IDs like "211759.20" to lose trailing zeros.
    370      # Read all columns as str first, then set the index manually.
    371      profiles = pd.read_csv(result_alleles_tsv, header=0,
    372                             sep='\t', low_memory=False, dtype=str)
    373      _id_col = profiles.columns[0]
    374      profiles = profiles.set_index(_id_col)
    375      genome_ids = profiles.index.tolist()
    376      genome_ids_display = [gid.replace('_', '.') for gid in genome_ids]
    377  
>>  378      # Step 2 — Mask (column-by-column, matching chewBBACA)
    379      # chewBBACA: masked_profiles = profiles_matrix.apply(im.replace_chars)
    380      masked_profiles = profiles.apply(_chewbbaca_replace_chars)
    381  
    382      # Step 3 — Presence-absence matrix
    383      # chewBBACA: pa_matrix = masked_profiles.apply(binarize_matrix)
    384      pa_matrix = masked_profiles.apply(_chewbbaca_binarize)
    385  
    386      # Step 3b — Drop genomes with zero valid allele calls (all loci absent).
    387      # A single all-zero row prevents any locus from reaching the 100% threshold.
    388      loci_per_genome = pa_matrix.sum(axis=1)
    389      zero_coverage = loci_per_genome[loci_per_genome == 0].index.tolist()
    390      if zero_coverage:
```

## `pybin/core-genome-mlst-utils.py:1501`

```
   1495      reading frames (ORFs). To be considered, a CDS must be classified as such by
   1496      <a href="https://github.com/althonos/pyrodigal" target="_blank">Pyrodigal</a>. These
   1497      coding regions are then compared to the known alleles. If the Blast Score Ratio (BSR) of a
   1498      known allele is equal to or greater than 0.6 it is considered an Exact Match. Note: matches
   1499      are made at the gene level. If a sequence does not match any of the known alleles it is
   1500      considered a new allele candidate and stored as INF-###. These alleles are not added to our
>> 1501      schemas (chewBBACA does allow for this functionality). The allele calling results are used
   1502      throughout the rest of the pipeline.
   1503    </p>
   1504    <p>The AlleleCall module assigns one of the following classification codes to each locus:</p>
   1505    <div style="background:#e8f4f8; border-left:5px solid #2196f3; border-radius:4px;
   1506                padding:16px 20px; margin-top:8px;">
   1507      <dl style="margin:0; display:grid; grid-template-columns:max-content 1fr; gap:6px 20px;
   1508                 align-items:baseline;">
   1509        <dt style="font-weight:bold; white-space:nowrap;">EXC</dt>
   1510        <dd style="margin:0;">Exact Locus Match — an exact allele match was found.</dd>
   1511  
   1512        <dt style="font-weight:bold; white-space:nowrap;">INF</dt>
   1513        <dd style="margin:0;">Inferred New Allele — a valid but previously unobserved allele sequence.</dd>
```

## `pybin/core-genome-mlst-utils.py:1747`

```
   1741                help="Path to service config.json (used for tree viewer link and low-coverage QC).")
   1742  def write_html_report(result_alleles, metadata_json, html_report_path, svg_dir, config_json):
   1743      """Generate an interactive cgMLST HTML report.
   1744  
   1745      \b
   1746      Arguments:
>> 1747        RESULT_ALLELES   Path to chewBBACA result_alleles.tsv
   1748        METADATA_JSON    Path to genome_metadata.json
   1749        HTML_REPORT_PATH Path for the output HTML report
   1750      """
   1751      click.echo("Using result_alleles: {}".format(result_alleles))
   1752  
   1753      tree_ws_path = ""
   1754      if config_json:
   1755          with open(config_json) as f:
   1756              config = json.load(f)
   1757          params = config.get("params", {})
   1758          ws_output_path = params.get("output_path", "")
   1759          ws_output_file = params.get("output_file", "")
```

