import functools

import numpy as np
from pydantic import Field

from ...datasets import SLM21Dataset
from .... import validators
from ....model import m_data_items, m_benchmark


class SLM21SubmissionValidator(m_benchmark.SubmissionValidation):
    """ Class that contains all functions to validate a sLM21 submission """
    dataset: SLM21Dataset = Field(default_factory=lambda: SLM21Dataset.load())

    @m_benchmark.validation_fn(target='lexical_dev')
    def validating_lexical_dev(self, lexical_dev: m_data_items.FileItem):
        additional_df_checks = [
            # Verify that result df has expected columns
            functools.partial(
                validators.dataframe_column_check, expected_columns=['score']),
            # Verify that result df has all filenames in set
            functools.partial(
                validators.dataframe_index_check,
                expected=[f.stem for f in self.dataset.index.subsets.lexical_dev.items.wav_list.files_list]
            ),
            # Verify that scores are in float
            functools.partial(
                validators.dataframe_type_check,
                col_name='score',
                expected_type=float
            )
        ]

        # check dataframe
        results = validators.dataframe_check(lexical_dev, additional_df_checks, sep=' ', header=None,
                                             names=['filename', 'score'], index_col='filename')

        # add item tag
        m_benchmark.add_item('lexical_dev', results)
        return results

    @m_benchmark.validation_fn(target='lexical_test')
    def validating_lexical_test(self, lexical_test: m_data_items.FileItem):
        # check that file is a correct space separated list with two columns
        additional_df_checks = [
            # Verify that result df has expected columns
            functools.partial(
                validators.dataframe_column_check, expected_columns=['score']),
            # Verify that result df has all filenames in set
            functools.partial(
                validators.dataframe_index_check,
                expected=[f.stem for f in self.dataset.index.subsets.lexical_test.items.wav_list.files_list]
            ),
            # Verify that scores are in float
            functools.partial(
                validators.dataframe_type_check,
                col_name='score',
                expected_type=float
            )
        ]

        # check dataframe
        results = validators.dataframe_check(lexical_test, additional_df_checks, sep=' ', header=None,
                                             names=['filename', 'score'], index_col='filename')

        # add item tag
        m_benchmark.add_item('lexical_test', results)
        return results

    @m_benchmark.validation_fn(target='semantic_dev_synthetic')
    def validating_semantic_dev_synthetic(self, semantic_dev_synthetic: m_data_items.FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.semantic_dev.items.synthetic_wav_list.files_list
            )
        ]
        additional_checks = [
            # Verify that type of array is float
            functools.partial(
                validators.numpy_dtype_check,
                dtype=np.dtype('float')
            ),
            # Verify that array has 2 dimensions
            functools.partial(
                validators.numpy_dimensions_check,
                ndim=2
            )
        ]

        # Check file list
        results = validators.numpy_array_list_check(
            semantic_dev_synthetic, f_list_checks=f_list_checks, additional_checks=additional_checks
        )

        # add item tag
        m_benchmark.add_item('semantic_dev_synthetic', results)
        return results

    @m_benchmark.validation_fn(target='semantic_dev_librispeech')
    def validating_semantic_dev_librispeech(self, semantic_dev_librispeech: m_data_items.FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.semantic_dev.items.librispeech_wav_list.files_list
            )
        ]
        additional_checks = [
            # Verify that type of array is float
            functools.partial(
                validators.numpy_dtype_check,
                dtype=np.dtype('float')
            ),
            # Verify that array has 2 dimensions
            functools.partial(
                validators.numpy_dimensions_check,
                ndim=2
            )
        ]

        # Check file list
        results = validators.numpy_array_list_check(
            semantic_dev_librispeech, f_list_checks=f_list_checks, additional_checks=additional_checks
        )

        # add item tag
        m_benchmark.add_item('semantic_dev_librispeech', results)
        return results

    @m_benchmark.validation_fn(target='semantic_test_synthetic')
    def validating_semantic_test_synthetic(self, semantic_test_synthetic: m_data_items.FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.semantic_test.items.synthetic_wav_list.files_list
            )
        ]
        additional_checks = [
            # Verify that type of array is float
            functools.partial(
                validators.numpy_dtype_check,
                dtype=np.dtype('float')
            ),
            # Verify that array has 2 dimensions
            functools.partial(
                validators.numpy_dimensions_check,
                ndim=2
            )
        ]

        # Check file list
        results = validators.numpy_array_list_check(
            semantic_test_synthetic, f_list_checks=f_list_checks, additional_checks=additional_checks
        )

        # add item tag
        m_benchmark.add_item('semantic_test_synthetic', results)
        return results

    @m_benchmark.validation_fn(target='semantic_test_librispeech')
    def validating_semantic_test_librispeech(self, semantic_test_librispeech: m_data_items.FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.semantic_test.items.librispeech_wav_list.files_list
            )
        ]
        additional_checks = [
            # Verify that type of array is float
            functools.partial(
                validators.numpy_dtype_check,
                dtype=np.dtype('float')
            ),
            # Verify that array has 2 dimensions
            functools.partial(
                validators.numpy_dimensions_check,
                ndim=2
            )
        ]

        # Check file list
        results = validators.numpy_array_list_check(
            semantic_test_librispeech, f_list_checks=f_list_checks, additional_checks=additional_checks
        )

        # add item tag
        m_benchmark.add_item('semantic_test_librispeech', results)
        return results

    @m_benchmark.validation_fn(target='syntactic_dev')
    def validating_syntactic_dev(self, syntactic_dev: m_data_items.FileItem):
        additional_df_checks = [
            # Verify that result df has expected columns
            functools.partial(
                validators.dataframe_column_check, expected_columns=['score']),
            # Verify that result df has all filenames in set
            functools.partial(
                validators.dataframe_index_check,
                expected=[f.stem for f in self.dataset.index.subsets.syntactic_dev.items.wav_list.files_list]
            ),
            # Verify that scores are in float
            functools.partial(
                validators.dataframe_type_check,
                col_name='score',
                expected_type=float
            )
        ]

        # check dataframe
        results = validators.dataframe_check(syntactic_dev, additional_df_checks, sep=' ', header=None,
                                             names=['filename', 'score'], index_col='filename')

        # add item tag
        m_benchmark.add_item('syntactic_dev', results)
        return results

    @m_benchmark.validation_fn(target='syntactic_test')
    def validating_syntactic_test(self, syntactic_test: m_data_items.FileItem):
        additional_df_checks = [
            # Verify that result df has expected columns
            functools.partial(
                validators.dataframe_column_check, expected_columns=['score']),
            # Verify that result df has all filenames in set
            functools.partial(
                validators.dataframe_index_check,
                expected=[f.stem for f in self.dataset.index.subsets.syntactic_test.items.wav_list.files_list]
            ),
            # Verify that scores are in float
            functools.partial(
                validators.dataframe_type_check,
                col_name='score',
                expected_type=float
            )
        ]

        # check dataframe
        results = validators.dataframe_check(syntactic_test, additional_df_checks, sep=' ', header=None,
                                             names=['filename', 'score'], index_col='filename')

        # add item tag
        m_benchmark.add_item('syntactic_test', results)
        return results
