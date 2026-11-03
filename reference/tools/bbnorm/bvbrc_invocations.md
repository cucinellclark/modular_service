# BV-BRC invocations of `bbnorm.sh` (bbnorm)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 2 hunk(s) in 1 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `lib/ReadLibrary.py`

## `lib/ReadLibrary.py:462`

```
    456          bbnorm_stdout = out_file1 + "_bbnorm_stats.txt"
    457          out_file1 = out_file1 + suffix
    458          if file2:
    459              out_file2 = out_file2 + suffix
    460  
    461          bbnorm_fh = open(bbnorm_stdout, 'w')
>>  462          command = ['bbnorm.sh', 'in='+file1, 'target='+str(target_depth), 'out='+out_file1]
    463          if file2:
    464              command.extend(('in2='+file2, 'out2='+out_file2))
    465          command.extend(['threads={}'.format(ReadLibrary.NUM_THREADS), '-Xmx{:.0f}g'.format(ReadLibrary.MEMORY * 0.85)])
    466  
    467          ReadLibrary.LOG.write("normalize, command line = "+" ".join(command)+"\n")
    468          proc = subprocess.Popen(command, shell=False, stderr=bbnorm_fh)
    469          proc.wait()
    470          bbnorm_fh.close()
    471  
    472          if os.path.exists(out_file1) and os.path.getsize(out_file1) > 0:
    473              # if successful, store current version and move on to normalized version
    474              self.store_current_version()
```

## `lib/ReadLibrary.py:487`

```
    481                      os.unlink(file2)
    482              self.study_reads()    
    483              self.transformation = 'normalize to target depth'
    484              self.command = " ".join(command)
    485              self.process_time = time() - startTime
    486  
>>  487              proc = subprocess.run("bbnorm.sh", capture_output=True, text=True)
    488              for line in proc.stdout.split("\n"):
    489                  m = re.match("Last modified\s*(\S.*\S)", line)
    490                  if m:
    491                      bbnorm_version = m.group(1)
    492                      ReadLibrary.program_version['bbnorm'] = bbnorm_version
    493                      break
    494  
    495          else:
    496              # keep current, unnormalized, version
    497              ReadLibrary.LOG.write("bbnorm failed to normalize\n")
    498              
    499  
```

