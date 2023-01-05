#### downloadable items

- [X] `zrc datasets:{pull,rm}`: list, pull and delete datasets
- [X] `zrc checkpoints:{pull,rm}`: list pull and delete checkpoint archives
- [X] `zrc samples:{pull, rm}`: list pull and delete samples archives

#### benchmarks 

- [X] `zrc benchmarks`: list existing benchmarks
- [X] `zrc benchmarks:run <name> <submission_dir>`: run a benchmark on a submission
- [X] `zrc benchmarks:run <name> -t <task_name>`: run only some tasks of a benchmark on a submission
- [X] `zrc benchmarks:run <name> -s <set_name>`: run a benchmark only on specific subsets of a submission

#### submissions
- [X] `zrc submission:init <benchmark_name> <submission_dir>`: create a submission directory
  - [X] TODO: deduce benchmark from meta.yaml (remove it as argument to the command)
- [X] `zrc submission:params <submission_dir>`:  show current parameters 
- [X] `zrc submission:verify <submission_dir>`: validate a submission directory
- [ ] `zrc submission:upload <submission_dir> `: upload a submission from a directory
  - [ ] TODO: integrate leaderboard generation into submission 
  - [ ] TODO: add verification before upload
- [ ] `zrc submission:upload --check <submission_dir> `: check if submission can be uploaded (does not upload)
  
#### user 

- [X] `zrc user`
- [X] `zrc user:login`
- [X] `zrc user:clear`


#### Available Benchmark list

- [X] sLM21
- [X] abxLS
- [ ] abx17
> TODO: has some weird bugs when evaluating (check source)
> TODO: add score dir and leaderboard generation
> TODO: add validation
- [ ] abx15
> TODO: test dataset import
> TODO: add benchmark with overloaded the librispeech-abx task
> TODO: add validation
> TODO: score dir & leaderboard 
- [X] tde17
> TODO: eval not tested
> TODO: add score dir and leaderboard generation
> TODO: add validation
- [ ] tde15
> TODO: test dataset import
> TODO: add benchmark with overloaded the tdev2 task
> TODO: score dir & leaderboard
> TODO: validation
- [ ] tts019
> TODO: find the correct dataset
> TODO: find the eval code, and figure out an implementation.


#### potential extensions & plugins

- extension 1 : extractors --> implement some basic extractor for the most used models
    Extractor for CPC, Bert, LSTM, etc...

- extension 2 : infSim adaptor wrapper package
    Wrapper module that allows to use this API to allow running benchmarks on infSim architecture
