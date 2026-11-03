# BV-BRC invocations of `phispy` (phispy)

Auto-mined from `/opt/p3/deployment` by tools/mine_invocations.py. 6 hunk(s) in 5 file(s).
Matched lines are marked with `>>`. Review manually; some hits are doc/log strings.

Files:
- `plbin/rast_call_prophage_using_phispy.pl`
- `services/SolrProxy/start_service`
- `services/app_service/start_service`
- `services/genome_annotation/start_service`
- `services/homology_service/start_service`

## `plbin/rast_call_prophage_using_phispy.pl:151`

```
    145  my $typed_prefix = join(".", $id_prefix, $type);
    146  
    147  my $hostname = `hostname`;
    148  chomp $hostname;
    149  
    150  my $event = {
>>  151      tool_name => "phispy",
    152      execute_time => scalar gettimeofday,
    153      parameters => \@cmd,
    154      hostname => $hostname,
    155  };
    156  my $event_id = &GenomeTypeObject::add_analysis_event($genomeTO, $event);
    157  
    158  # The columns of the file are:
    159  #   - 1. Prophage number
    160  #   - 2. The contig upon which the prophage resides
    161  #   - 3. The start location of the prophage
    162  #   - 4. The stop location of the prophage
    163  # If we can detect the _att_ sites, the additional columns are:
```

## `plbin/rast_call_prophage_using_phispy.pl:187`

```
    181  	{
    182  	    &GenomeTypeObject::add_feature($genomeTO, {
    183  		-id_client => $id_client,
    184  		-id_prefix => $id_prefix,
    185  		-type       => $type,
    186  		-location   => [[ $contig, $beg, '+', $len ]],
>>  187  		-annotator  => 'phispy',
>>  188  		-annotation => 'Add feature called by phispy',
    189  		-analysis_event_id   => $event_id,
    190  		-function => 'phiSpy-predicted prophage',
    191  	    });
    192  	}
    193      }
    194      close(O);
    195  }
    196  else
    197  {
    198      my $err = read_file("$out/phispy.stderr");
    199      my $out = read_file("$out/phispy.stdout");
    200      print STDERR "Prophage run did not find any output. Stdout:\n$out\nStderr:\n$err\n";
```

## `services/SolrProxy/start_service:10`

```
      4  export PATH=$KB_TOP/bin:$KB_RUNTIME/bin:$KB_TOP/services/SolrProxy/bin:$KB_TOP/services/cdmi_api/bin:$PATH:$KB_RUNTIME/seedtk/bin
      5  export PERL5LIB=$KB_TOP/lib
      6  export KB_SERVICE_NAME="SolrProxy"
      7  export KB_SERVICE_LOG_DIR="$KB_TOP/services/SolrProxy"
      8  export KB_DEPLOYMENT_CONFIG="$KB_TOP/deployment.cfg"
      9  #
>>   10  # For phispy
     11  export R_LIBS="$KB_TOP/lib"
     12  
     13  #
     14  # Dancer apps config dir
     15  #
     16  export DANCER_CONFDIR="$KB_TOP/services/SolrProxy"
     17  
     18  export PERL_LWP_SSL_VERIFY_HOSTNAME=0
     19  
     20  
     21  pid_file=$KB_SERVICE_LOG_DIR/service.pid
     22  status_file=$KB_SERVICE_LOG_DIR/service.status
```

## `services/app_service/start_service:10`

```
      4  export PATH=$KB_TOP/bin:$KB_RUNTIME/bin:$KB_TOP/services/app_service/bin:$KB_TOP/services/cdmi_api/bin:$PATH:$KB_RUNTIME/seedtk/bin
      5  export PERL5LIB=$KB_TOP/lib
      6  export KB_SERVICE_NAME="app_service"
      7  export KB_SERVICE_LOG_DIR="$KB_TOP/services/app_service"
      8  export KB_DEPLOYMENT_CONFIG="$KB_TOP/deployment.cfg"
      9  #
>>   10  # For phispy
     11  export R_LIBS="$KB_TOP/lib"
     12  
     13  #
     14  # Dancer apps config dir
     15  #
     16  export DANCER_CONFDIR="$KB_TOP/services/app_service"
     17  
     18  export PERL_LWP_SSL_VERIFY_HOSTNAME=0
     19  
     20  
     21  pid_file=$KB_SERVICE_LOG_DIR/service.pid
     22  status_file=$KB_SERVICE_LOG_DIR/service.status
```

## `services/genome_annotation/start_service:20`

```
     14      fi
     15  fi
     16  export KB_SERVICE_LOG_DIR="/opt/p3/deployment/var/services/genome_annotation"
     17  
     18  export KB_DEPLOYMENT_CONFIG="$KB_TOP/deployment.cfg"
     19  #
>>   20  # For phispy
     21  export R_LIBS="$KB_TOP/lib"
     22  
     23  if [ -f $KB_TOP/setenv.sh ] ; then
     24    . $KB_TOP/setenv.sh
     25  fi
     26  if [ -f $KB_SERVICE_DIR/setenv.sh ] ; then
     27    . $KB_SERVICE_DIR/setenv.sh
     28  fi
     29  
     30  export TMPDIR=/tmp
     31  export TEMPDIR=/tmp
     32  
```

## `services/homology_service/start_service:10`

```
      4  export PATH=$KB_TOP/bin:$KB_RUNTIME/bin:$KB_TOP/services/homology_service/bin:$KB_TOP/services/cdmi_api/bin:$PATH
      5  export PERL5LIB=$KB_TOP/lib
      6  export KB_SERVICE_NAME="HomologyService"
      7  export KB_SERVICE_DIR="$KB_TOP/services/homology_service"
      8  export KB_DEPLOYMENT_CONFIG="$KB_TOP/deployment.cfg"
      9  #
>>   10  # For phispy
     11  export R_LIBS="$KB_TOP/lib"
     12  
     13  
     14  pid_file=$KB_SERVICE_DIR/service.pid
     15  
     16  
     17  
     18  starman_params="--listen :7134 --pid $pid_file $workers $max_requests"
     19  
     20  starman_params="$starman_params --error-log $KB_SERVICE_DIR/error.log"
     21  starman_params="$starman_params --access-log $KB_SERVICE_DIR/access.log"
     22  
```

