from pydantic import Field

from . import AbxLSDataset
from ..validation import SubmissionValidation, validation_fn, validators, add_item
from ...data_items import FileListItem


class AbxLSSubmissionValidator(SubmissionValidation):
    dataset: AbxLSDataset = Field(default_factory=lambda: AbxLSDataset.load())

    @validation_fn(target='dev_clean')
    def validate_dev_clean(self, item: FileListItem):
        # todo: implement validation
        return []

    @validation_fn(target='dev_other')
    def validate_dev_other(self, item: FileListItem):
        # todo: implement validation
        return []

    @validation_fn(target='test_clean')
    def validate_test_clean(self, item: FileListItem):
        # todo: implement validation
        return []

    @validation_fn(target='test_other')
    def validate_test_other(self, item: FileListItem):
        # todo: implement validation
        return []
