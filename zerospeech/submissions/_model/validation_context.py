import abc
from typing import Optional, Protocol, Literal, List, Union

from zerospeech.out import error_console, warning_console


class ValidationResponse(abc.ABC):
    """ Abstract class defining a Message object specifying validation Errors/Warnings/Checks """

    def __init__(self, msg, *, data=None, item_name=None, filename=None, location=None):
        self.item_name = item_name
        self.filename = filename
        self.location = location
        self.msg = msg
        self.data = data

    def valid(self):
        return getattr(self, '__is_valid__', False)

    def warning(self):
        return getattr(self, '__is_warning__', False)

    def error(self):
        return getattr(self, '__is_error__', False)

    def ok(self):
        return getattr(self, '__is_ok__', False)

    def __str__(self):
        item_name = '-'
        if self.item_name:
            item_name = self.item_name
        filename = '[-'
        if self.filename:
            filename = f"[{self.filename}"
        location = ':-]'
        if self.location:
            location = f":{self.location}]"
        msg = ''
        if self.msg:
            msg = self.msg

        cls_name = self.__class__.__name__
        return f'{cls_name}({item_name}){filename}{location}>> {msg}'


class ValidationWarning(ValidationResponse):
    """ Class designating a validation warning """
    __is_warning__ = True
    __is_valid__ = True


class ValidationError(ValidationResponse):
    """ Class designating a validation error """
    __is_error__ = True
    __is_valid__ = False


class ValidationOK(ValidationResponse):
    """ Class designating a successful validation check """
    __is_ok__ = True
    __is_valid__ = True


class HasStr(Protocol):

    def __str__(self) -> str:
        """ Convert to string """
        pass


class ValidationContext:

    def __init__(self):
        """ Initially context is empty """
        self._outputs: List[ValidationResponse] = []

    def __invert__(self) -> List[ValidationResponse]:
        """ Bitwise invert extracts the context """
        return self._outputs

    def __lshift__(self, item: Union[ValidationResponse, List[ValidationResponse]]):
        """ Extend outputs """
        if isinstance(item, list):
            self._outputs.extend(item)
        else:
            if not isinstance(item, ValidationResponse):
                raise ValueError(f'Cannot extend item of type {type(item)}')
            self._outputs.append(item)

    def __add__(self, other: "ValidationContext") -> "ValidationContext":
        """ Addition creates new context """
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cannot add item of type {type(other)}')

        nw_ctx = self.__class__()
        nw_ctx._outputs = [
            *self._outputs,
            *other._outputs
        ]
        return nw_ctx

    def __iadd__(self, other: "ValidationContext") -> "ValidationContext":
        if not isinstance(other, self.__class__):
            raise ValueError(f'Cannot add item of type {type(other)}')

        self._outputs.extend(other._outputs)
        return self

    def assertion(self, expr: bool, as_type: Literal['error', 'warning'], msg: str, **kwargs):
        """ Create an assertion """
        if not expr:
            if as_type == 'error':
                self._outputs.append(
                    ValidationError(
                        msg, item_name=kwargs.get("item_name", None),
                        data=kwargs.get("data", None), filename=kwargs.get("filename", None),
                        location=kwargs.get("location", None)
                    )
                )
            elif as_type == 'warning':
                self._outputs.append(
                    ValidationWarning(
                        msg, item_name=kwargs.get("item_name", None),
                        data=kwargs.get("data", None), filename=kwargs.get("filename", None),
                        location=kwargs.get("location", None)
                    )
                )

    def error_assertion(
            self, expr: bool, *, msg: str, item_name: Optional[str] = None,
            filename: Optional[str] = None, location: Optional[str] = None,
            data: Optional[HasStr] = None
    ):
        """ Create an error assertion """
        self.assertion(
            expr, as_type='error', msg=msg, item_name=item_name, filename=filename,
            location=location, data=data
        )

    def warn_assertion(
            self, expr: bool, *, msg: str, item_name: Optional[str] = None,
            filename: Optional[str] = None, location: Optional[str] = None,
            data: Optional[HasStr] = None
    ):
        """ Create an error assertion """
        self.assertion(
            expr, as_type='warning', msg=msg, item_name=item_name, filename=filename,
            location=location, data=data
        )

    def add_filename(self, filename):
        """ Add filename to all assertions """
        for i in self._outputs:
            i.filename = filename

    def add_item(self, item_name: str):
        """ Add item_name to all assertions """
        for i in self._outputs:
            i.item_name = item_name

    def print(self, allow_warnings: bool = True):
        """ Print Outputs """
        error_list = [r for r in self._outputs if not r.ok()]

        if not allow_warnings:
            error_list = [r for r in self._outputs if not r.warning()]

        for item in error_list:
            if item.warning() and allow_warnings:
                warning_console.log(item)
            else:
                error_console.log(item)

    def fails(self) -> bool:
        """ Check if Validation Fails """
        # only errors fail the validation
        return len([r for r in self._outputs if not r.valid()]) != 0

    def has_warnings(self) -> bool:
        """ Check if Validation has warnings """
        return len([r for r in self._outputs if r.warning()]) > 0

    def get_ok(self):
        """ Filter Ok Messages """
        return [r for r in self._outputs if r.ok()]

    def get_warnings(self):
        """ Filter Warning Messages """
        return [r for r in self._outputs if r.warning()]

    def get_errors(self):
        """Filter Error Messages """
        return [r for r in self._outputs if r.error()]
