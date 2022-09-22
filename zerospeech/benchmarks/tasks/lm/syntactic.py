from typing import TYPE_CHECKING

import pandas as pd

from .params import SyntacticParams
from ....data_loaders import load_dataframe
from ....model import m_benchmark, m_data_items

if TYPE_CHECKING:
    from ..._benchmarks.sLM_21 import SLM21Submission
    from ...datasets import SLM21Dataset

default_params = SyntacticParams()


class SyntacticTask(m_benchmark.Task):
    """Allows the computation of the score by sentences pair and by syntax type."""
    _name = "syntactic"
    sets = ('dev', 'test')
    result_filenames = default_params.result_filenames

    @staticmethod
    def syntactic_by_pair(data: pd.DataFrame) -> pd.DataFrame:
        """Returns a data frame with the scores by (sentence, non sentence) pair"""
        # compute the score for each pair in an additional 'score' column, then
        # delete the 'score word' and 'score non word' columns that become useless
        score = data.loc[:, ['score sentence', 'score non sentence']].to_numpy()
        data['score'] = (
                0.5 * (score[:, 0] == score[:, 1])
                + (score[:, 0] > score[:, 1]))
        data.drop(columns=['score sentence', 'score non sentence'], inplace=True)

        # finally get the mean score across voices for all pairs
        score = data.groupby(['type', 'subtype', 'id']).apply(lambda x: (
            x.iat[0, 2],  # type
            x.iat[0, 3],  # subtype
            x.iat[0, 4],  # sentence
            x.iat[0, 5],  # non sentence
            x['score'].mean()))
        return pd.DataFrame(
            score.to_list(),
            columns=['type', 'subtype', 'sentence', 'non sentence', 'score'])

    @staticmethod
    def syntactic_by_type(data: pd.DataFrame) -> pd.DataFrame:
        """Returns a data frame with mean scores by syntax error type"""
        return data.score.groupby([data['type']]).agg(
            n='count', score='mean', std='std').reset_index()

    def run_syntactic_comparison(self, gold: m_data_items.FileItem, sub_file: m_data_items.FileItem):
        """ This function creates a syntactic comparison based on inputs

        data_formatting:
            Each line of the data frame contains a pair of (correct,
        incorrect) sentences and has the following columns: 'id', 'voice', 'type',
        'sentence', 'score sentence', 'non sentence', 'score non sentence'.

        """
        gold_df = load_dataframe(gold, header=0, index_col='filename')
        sub_df = load_dataframe(sub_file, sep=' ', header=None,
                                names=['filename', 'score'], index_col='filename')

        # merge the gold and score using filenames, then remove the columns
        # 'phones' and 'filename' as we don't use them for evaluation
        data = pd.concat([gold_df, sub_df], axis=1)
        data.reset_index(drop=True, inplace=True)

        # going from a word per line to a pair (word, non word) per line
        data = pd.concat([
            data.loc[data['correct'] == 1].reset_index().rename(
                lambda x: 's_' + x, axis=1),
            data.loc[data['correct'] == 0].reset_index().rename(
                lambda x: 'ns_' + x, axis=1)], axis=1)
        data.drop(
            ['s_index', 'ns_index', 'ns_voice', 'ns_type', 'ns_subtype',
             's_correct', 'ns_correct', 'ns_id'],
            axis=1, inplace=True)

        data.rename(
            {'s_id': 'id',
             's_voice': 'voice',
             's_type': 'type',
             's_subtype': 'subtype',
             's_transcription': 'sentence',
             'ns_transcription': 'non sentence',
             's_score': 'score sentence',
             'ns_score': 'score non sentence'},
            axis=1, inplace=True)

        by_pair = self.syntactic_by_pair(data)
        by_type = self.syntactic_by_type(by_pair)

        # remove (type, subtype) from by_pair data since by_type is complete
        by_pair.drop(['type', 'subtype'], axis=1, inplace=True)

        return by_pair, by_type

    def eval(self, submission: "SLM21Submission", dataset: "SLM21Dataset"):
        """ Executes syntactic comparison on required sets and writes results to score_dir """
        output_dir = submission.score_dir
        self.sets = submission.sets

        if 'dev' in self.sets:
            gold_file = dataset.index.subsets.syntactic_dev.items.gold
            sub_file = submission.items.syntactic_dev

            with self.console.status('Running syntactic_dev evaluation....', spinner="aesthetic"):
                by_pair, by_type = self.run_syntactic_comparison(gold_file, sub_file)

            filename = output_dir / f"{self.result_filenames['dev']['by_pair']}"
            self.console.print(f":pencil: writing {self.result_filenames['dev']['by_pair']}",
                               style="underline yellow4")
            by_pair.to_csv(filename, index=False, float_format='%.4f')

            filename = output_dir / f"{self.result_filenames['dev']['by_type']}"
            self.console.print(f":pencil: writing {self.result_filenames['dev']['by_type']}",
                               style="underline yellow4")
            by_type.to_csv(filename, index=False, float_format='%.4f')

        if 'test' in self.sets:
            gold_file = dataset.index.subsets.syntactic_test.items.gold
            sub_file = submission.items.syntactic_test

            with self.console.status('Running syntactic_test evaluation....', spinner="aesthetic"):
                by_pair, by_type = self.run_syntactic_comparison(gold_file, sub_file)

            filename = output_dir / f"{self.result_filenames['test']['by_pair']}"
            self.console.print(f":pencil: writing {self.result_filenames['test']['by_pair']}",
                               style="underline yellow4")
            by_pair.to_csv(filename, index=False, float_format='%.4f')

            filename = output_dir / f"{self.result_filenames['test']['by_type']}"
            self.console.print(f":pencil: writing {self.result_filenames['test']['by_type']}",
                               style="underline yellow4")
            by_type.to_csv(filename, index=False, float_format='%.4f')
