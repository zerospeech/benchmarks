import abc
from functools import wraps
from typing import List

from pydantic import BaseModel

from ..generic import Submission, Dataset
from ...out import error_console, warning_console


def validation_fn(target: str):
    def fn_wrapper(method):
        @wraps(method)
        def _impl(self, *method_args, **method_kwargs):
            return method(self, *method_args, **method_kwargs)

        _impl._validation_fn = True
        _impl._validation_target = target
        return _impl
    return fn_wrapper


class ValidationResponse(abc.ABC):

    def valid(self):
        return getattr(self, 'valid_item', False)

    def __str__(self):
        item_name = getattr(self, 'item_name', '')
        msg = getattr(self, 'msg', '')
        data = getattr(self, 'data', '')
        cls_name = self.__class__.__name__
        return f'{cls_name}({item_name}): {msg}'


class ValidationWarning(ValidationResponse):

    def __init__(self, msg, *, data=None, item_name=None):
        self.valid_item = True
        self.item_name = item_name
        self.msg = msg
        self.data = data


class ValidationError(ValidationResponse):

    def __init__(self, msg, *, data=None, item_name=None):
        self.valid_item = False
        self.item_name = item_name
        self.msg = msg
        self.data = data


class ValidationOK(ValidationResponse):

    def __init__(self, msg, *, data=None, item_name=None):
        self.valid_item = True
        self.item_name = item_name
        self.msg = msg
        self.data = data


def has_errors(resp: List[ValidationResponse]):
    """ Check if all items are positive or warning responses"""
    return all([d.valid() for d in resp])


def remove_ok(resp: List[ValidationResponse]):
    return [d for d in resp if not d.valid()]


def add_item(item_name: str, resp: List[ValidationResponse]):
    """ Add item name """
    for r in resp:
        r.item_name = item_name


def show_errors(resp: List[ValidationResponse], allow_warnings: bool = True):
    error_list = remove_ok(resp)

    for item in error_list:
        if isinstance(item, ValidationWarning) and allow_warnings:
            warning_console.log(item)
        else:
            error_console.log(item)

    return len(error_list) != 0


class SubmissionValidation(BaseModel, abc.ABC):
    dataset: Dataset

    def _is_validation_fn(self, fn_name):
        fn = getattr(self, fn_name, {})
        return getattr(fn, '_validation_fn', False)

    def _get_validation_target(self, fn_name):
        fn = getattr(self, fn_name, {})
        return getattr(fn, '_validation_target')

    def validate(self, submission: Submission) -> List[ValidationResponse]:
        validators_items = {
            f"{self._get_validation_target(a)}": getattr(self, a)
            for a in dir(self) if self._is_validation_fn(a)
        }

        results = []
        for name, item in submission.items:
            validator = validators_items.get(name, None)
            if validator is not None:
                res = validator(item)
                results.extend(res)
            else:
                results.append(ValidationWarning("no validation found", item_name=name))

        return results
