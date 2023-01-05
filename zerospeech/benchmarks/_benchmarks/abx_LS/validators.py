import functools

import numpy as np
from pydantic import Field

from ...datasets import AbxLSDataset
from .... import validators
from ....model import m_benchmark, m_data_items


class AbxLSSubmissionValidator(m_benchmark.SubmissionValidation):
    """ File Validation for an ABXLS submission """
    dataset: AbxLSDataset = Field(default_factory=lambda: AbxLSDataset.load())

    @m_benchmark.validation_fn(target='dev_clean')
    def validate_dev_clean(self, dev_clean: m_data_items.FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.dev_clean.items.wav_list.files_list
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
            ),
            # Verify that files have the same dimensions
            validators.numpy_col_comparison(1)
        ]
        # Check file list
        results = validators.numpy_array_list_check(
            dev_clean, f_list_checks=f_list_checks, additional_checks=additional_checks
        )
        # add item tag
        m_benchmark.add_item('dev_clean', results)
        return results

    @m_benchmark.validation_fn(target='dev_other')
    def validate_dev_other(self, dev_other: m_data_items.FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.dev_other.items.wav_list.files_list
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
            ),
            # Verify that files have the same dimensions
            validators.numpy_col_comparison(1)
        ]
        # Check file list
        results = validators.numpy_array_list_check(
            dev_other, f_list_checks=f_list_checks, additional_checks=additional_checks
        )
        # add item tag
        m_benchmark.add_item('dev_other', results)
        return results

    @m_benchmark.validation_fn(target='test_clean')
    def validate_test_clean(self, test_clean: m_data_items.FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.test_clean.items.wav_list.files_list
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
            ),
            # Verify that files have the same dimensions
            validators.numpy_col_comparison(1)
        ]
        # Check file list
        results = validators.numpy_array_list_check(
            test_clean, f_list_checks=f_list_checks, additional_checks=additional_checks
        )
        # add item tag
        m_benchmark.add_item('test_clean', results)
        return results

    @m_benchmark.validation_fn(target='test_other')
    def validate_test_other(self, test_other: m_data_items.FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.test_other.items.wav_list.files_list
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
            ),
            # Verify that files have the same dimensions
            validators.numpy_col_comparison(1)
        ]
        # Check file list
        results = validators.numpy_array_list_check(
            test_other, f_list_checks=f_list_checks, additional_checks=additional_checks
        )
        # add item tag
        m_benchmark.add_item('test_other', results)
        return results
