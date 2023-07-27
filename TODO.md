#### downloadable items

- [X] `zrc datasets:{pull,import,rm}`: list, pull, import and delete datasets archives
- [X] `zrc checkpoints:{pull,import,rm}`: list pull, import and delete checkpoint archives
- [X] `zrc samples:{pull,import,rm}`: list pull and, import delete samples archives

#### benchmarks 

- [X] `zrc benchmarks`: list existing benchmarks
- [X] `zrc benchmarks:info`: details on each benchmark
- [X] `zrc benchmarks:run <name> <submission_dir>`: run a benchmark on a submission
- [X] `zrc benchmarks:run <name> -t <task_name>`: run only some tasks of a benchmark on a submission
- [X] `zrc benchmarks:run <name> -s <set_name>`: run a benchmark only on specific subsets of a submission

### Index

- [X] auto-update: auto update: conditions: if local file is older than a week, if remote file has been updated
- [X] manual update `zrc reset-index`

#### submissions
- [X] `zrc submission:init <benchmark_name> <submission_dir>`: create a submission directory
  - [X] TODO: deduce benchmark from meta.yaml (remove it as argument to the command)
- [X] `zrc submission:params <submission_dir>`:  show current parameters 
- [X] `zrc submission:verify <submission_dir>`: validate a submission directory


# Submit
- [ ] `zrc submit <submission_dir> `: upload a submission from a directory
  - [X] submission verification
  - [X] leaderboard generation
  - [X] zip_submission 
  - [X] upload zip (with resume function)
  - [ ] TODO: connect to backend
  
#### user 

- [X] `zrc user`
- [X] `zrc user:login`
- [X] `zrc user:clear`


#### Available Benchmark list

- [X] sLM21
- [X] abxLS
- [ ] abx17
> TODO: add score dir and leaderboard generation
- [X] tde17
- [ ] tts019
> TODO: find the correct dataset
> TODO: find the eval code, and figure out an implementation.


#### potential extensions & plugins

- extension 0: vocolab_extension:
  - [X] implement for leaderboard validation/management
  - [ ] TODO: implement for submission validation 

- extension 1 : extractors --> implement some basic extractor for the most used models
    Extractor for CPC, Bert, LSTM, etc...

- extension 2 : infSim adaptor wrapper package
    Wrapper module that allows to use this API to allow running benchmarks on infSim architecture
