# sLM21 submission

The format of a submission is briefly explained here.
For a more detailed explanation go to our website [zerospeech.com](https://zerospeech.com)

## meta.yaml

A yaml file specifying various information about the submission.

## params.yaml

A yaml file specifying various runtime parameters :

- quiet: a boolean specifying if the console needs to not print information and loading bars
- semantic/librispeech: a boolean specifying if the use of semantic subset librispeech is to be used
- semantic/synthetic:  a boolean specifying if the use of semantic subset synthetic is to be used
- semantic/metric: a string specifying which metric function to use (any metric supported by scipy.spatial.distance.cdist is supported)
- semantic/pooling: pooling method used (must be 'min','max', 'mean', 'sum', 'last' or 'lastlast')
- n_jobs: how many processes to use to speed-up certain parallelized parts of evaluation


## /lexical and /syntactic
The /lexical and /syntactic folders of the submission must contain the two files dev.txt and test.txt. For each *.wav file in the dataset must correspond a line either in dev.txt or test.txt with its corresponding pseudo-probability (order does not matter). For example if the dev dataset contains:

```
   /path/to/dataset/lexical/dev
   ├── aAAfmkmQpVz.wav
   ├── AaaggUZsvkR.wav
   ├── aAakhKfuvQI.wav
   ├── aAaOswLeeBL.wav
   ├── AaasVuoMJnS.wav   
 ```

The submitted file dev.txt must contain entries like:

```
   aAAfmkmQpVz -313.37445068359375
   AaaggUZsvkR -447.8950500488281
   aAakhKfuvQI -383.8902587890625
   aAaOswLeeBL -430.2048645019531
   AaasVuoMJnS -356.9426574707031
```

## /semantic

The semantic folder of the submission must contain the following subdirectories: dev/synthetic, dev/librispeech, test/synthtic and test/librispeech.

Each .wav file in the dataset must have its corresponding .txt file in the submission under the same directory structure. For example the dataset file /path/to/dataset/semantic/dev/synthetic/aAbcsWWKCz.wav must have its submitted file /path/to/submission/semantic/dev/synthetic/aAbcsWWKCz.txt.

Each .txt file encodes a single 2D numpy array of floats, each line encoding one features frame. For example:

```
     42.286527175400906 -107.68503050450957 59.79000088588511 -113.85831030071697
     0.7872647311548775 45.33505222077471 -8.468742865224545 0
     328.05422046327067 -4.495454384937348 241.186547397405 40.16161685378687
```

The number of columns (the features dimension) must be constant across the files. The number of lines depends on the speech sample duration.

The metric and pooling method used for evaluation must be specified in params.yaml