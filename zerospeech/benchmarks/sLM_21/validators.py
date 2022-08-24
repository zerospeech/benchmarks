from pydantic import Field

from .dataset import SLM21Dataset
from ...model import m_data_items, m_benchmark
from ... import validators


class SLM21SubmissionValidator(m_benchmark.SubmissionValidation):
    """ Class that contains all functions to validate a sLM21 submission """
    dataset: SLM21Dataset = Field(default_factory=lambda: SLM21Dataset.load())

    @m_benchmark.validation_fn(target='lexical_dev')
    def validating_lexical_dev(self, lexical_dev: m_data_items.FileItem):
        # check that file is a correct space separated list with two columns
        results, df = validators.dataframe_check(lexical_dev, expected_columns=['score'], sep=' ', header=None,
                                                 names=['filename', 'score'], index_col='filename')

        # check if all files from the dataset are represented in the filenames
        if df is not None:
            file_names = list(df.index)
            expected = [f.stem for f in self.dataset.index.subsets.lexical_dev.items.wav_list.files_list]
            results.extend(validators.list_checker(file_names, expected))

        # add item tag
        m_benchmark.add_item('lexical_dev', results)
        return results

    @m_benchmark.validation_fn(target='lexical_test')
    def validating_lexical_test(self, lexical_test: m_data_items.FileItem):
        # check that file is a correct space separated list with two columns
        results = []
        results1, df = validators.dataframe_check(lexical_test, expected_columns=['score'], sep=' ', header=None,
                                                  names=['filename', 'score'], index_col='filename')

        results.extend(results1)

        # check if all files from the dataset are represented in the filenames
        if df is not None:
            file_names = list(df.index)
            expected = [f.stem for f in self.dataset.index.subsets.lexical_test.items.wav_list.files_list]
            results2 = validators.list_checker(file_names, expected)
            results.extend(results2)

        # add item tag
        m_benchmark.add_item('lexical_test', results)
        return results

    @m_benchmark.validation_fn(target='semantic_dev_synthetic')
    def validating_semantic_dev_synthetic(self, lexical_test: m_data_items.FileItem):
        # todo: implement validation
        return []

    @m_benchmark.validation_fn(target='semantic_dev_librispeech')
    def validating_semantic_dev_librispeech(self, lexical_test: m_data_items.FileItem):
        # todo: implement validation
        return []

    @m_benchmark.validation_fn(target='semantic_test_synthetic')
    def validating_semantic_test_synthetic(self, lexical_test: m_data_items.FileItem):
        # todo: implement validation
        return []

    @m_benchmark.validation_fn(target='semantic_test_librispeech')
    def validating_semantic_test_librispeech(self, lexical_test: m_data_items.FileItem):
        # todo: implement validation
        return []

    @m_benchmark.validation_fn(target='syntactic_dev')
    def validating_syntactic_dev(self, lexical_test: m_data_items.FileItem):
        # todo: implement validation
        return []

    @m_benchmark.validation_fn(target='syntactic_test')
    def validating_syntactic_test(self, lexical_test: m_data_items.FileItem):
        # todo: implement validation
        return []
