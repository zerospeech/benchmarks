from pydantic import Field

from .dataset import AbxLSDataset
from ...model import m_benchmark, m_data_items


class AbxLSSubmissionValidator(m_benchmark.SubmissionValidation):
    dataset: AbxLSDataset = Field(default_factory=lambda: AbxLSDataset.load())

    @m_benchmark.validation_fn(target='dev_clean')
    def validate_dev_clean(self, item: m_data_items.FileListItem):
        # todo: implement validation
        return []

    @m_benchmark.validation_fn(target='dev_other')
    def validate_dev_other(self, item: m_data_items.FileListItem):
        # todo: implement validation
        return []

    @m_benchmark.validation_fn(target='test_clean')
    def validate_test_clean(self, item: m_data_items.FileListItem):
        # todo: implement validation
        return []

    @m_benchmark.validation_fn(target='test_other')
    def validate_test_other(self, item: m_data_items.FileListItem):
        # todo: implement validation
        return []
