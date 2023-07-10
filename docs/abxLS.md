# ABX-LS submission

The format of a submission is briefly explained here.
For a more detailed explanation go to our website [zerospeech.com](https://zerospeech.com)

## meta.yaml


## params.yaml


## /dev-{clean, other}, /test-{clean, other}

submission must contain the following subdirectories: `dev-clean`, `dev-other`, `test-clean` and `test-other`.

Each `.wav` file in the dataset must have its corresponding `.npy` file in the submission under the same directory structure. 
For example the dataset file /path/to/dataset/phonetic/dev-clean/1272-128104-0000.wav must have its submitted 
file /path/to/submission/phonetic/dev-clean/1272-128104-0000.npy.

> In the past .txt were used but binary npy files allow to reduce the size of the submission please prefer those

Each .npy file encodes a single 2D numpy array of floats, each line encoding one features frame. For example:

```
     42.286527175400906 -107.68503050450957 59.79000088588511 -113.85831030071697
     0.7872647311548775 45.33505222077471 -8.468742865224545 0
     328.05422046327067 -4.495454384937348 241.186547397405 40.16161685378687
```

- The number of columns (the features dimension) must be constant across the files. 
The number of lines depends on the speech sample duration.

- The frame shift (the shift between two successive frames) must be given in `params.yaml` along with the 
metric used for evaluation of those features.

- Each array must contain at least 2 frames (i.e. each file must have at least 2 lines).
