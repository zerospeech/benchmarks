#### downloadable items

- [X] `zrc datasets:{pull,rm}`: list, pull and delete datasets
- [X] `zrc checkpoints:{pull,rm}`: list pull and delete checkpoint archives
- [X] `zrc samples:{pull, rm}`: list pull and delete samples archives

#### benchmarks 

- [X] `zrc benchmarks`: list existing benchmarks
- [X] `zrc benchmarks:run <name> -o output <submission_dir>`: run a benchmark on a submission
- [X] `zrc benchmarks:run <name> -t <task_name> -o output <submission_dir>`: run only some tasks of a benchmark on a submission
- [X] `zrc benchmarks:run <name> -s <set_name> -o output <submission_dir>`: run a benchmark only on specific subsets of a submission
- [X] `zrc benchmarks:params <name> <submission_dir>`: generate `params.yaml` 

#### submissions

- [X] `zrc submission:init <benchmark_name> <submission_dir>`: create a submission directory
- [X] `zrc submission:verify <benchmark_name> <submission_dir>`: validate a submission directory
- [X] `zrc submission:zip <benchmark_name> <submission_dir>`: create an archive from a submission
- [ ] `zrc submission:zip <benchmark_name> <submission_dir>  --scores <scores_dir>`: create an archive from a submission with scores
- [ ] `zrc submission:upload <benchmark_name> <submission.zip>`: upload a submission from an archive
- [ ] `zrc submission:upload <benchmark_name> <submission> `: upload a submission from a directory
- [ ] `zrc submission:upload <benchmark_name> <submission> --scores <scores_dir>`: upload a submission from a directory with scores

#### leaderboards

- [X] `zrc leaderboard:generate <benchmark> <submission_dir> <scores_dir>`: generate leaderboard entry 
- [ ] `zrc leaderboard:upload <benchmark> <leaderboard.json>`: upload leaderboard entry

#### user 

- [ ] `zrc user`
- [ ] `zrc user:login`
- [ ] `zrc user:clear`


#### potential extensions & plugins

- plugin 1 : extractors --> implement some basic extractor for the most used models
    Extractor for CPC, Bert, LSTM, etc...

- plugin 2 : infSim adaptor wrapper package
    Wrapper module that allows to use this API to allow running benchmarks on infSim architecture

