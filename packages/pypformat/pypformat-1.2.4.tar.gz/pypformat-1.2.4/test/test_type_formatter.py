from typing import Any
from unittest.mock import patch

import pytest

from pformat.type_formatter import (
    CustomFormatter,
    TypeFormatter,
    make_formatter,
)

from .conftest import assert_does_not_throw, gen_derived_type

TYPES_DICT = {
    int: 123,
    float: 3.14,
    str: "string",
    bytes: b"bytes",
    list: [1, 2, 3],
    dict: {"k1": 1, "k2": 2},
}
TYPES = list(TYPES_DICT.keys())


class InvalidType:
    pass


def gen_concrete_fmt_type(fmt_type: type) -> type:
    class ConcreteFormatter(fmt_type):
        def __call__(self, obj: Any, depth: int = 0) -> str:
            fmt_type.__call__(self, obj, depth)

    return ConcreteFormatter


class TestTypeFormatterCommon:
    @pytest.fixture(params=TYPES, ids=[f"t={t.__name__}" for t in TYPES])
    def sut(self, request: pytest.FixtureRequest) -> TypeFormatter:
        self.type = request.param
        self.fmt_type = gen_concrete_fmt_type(TypeFormatter)
        return self.fmt_type(self.type)

    def test_eq_with_non_formatter_type(self, sut: TypeFormatter):
        with pytest.raises(TypeError) as err:
            sut == InvalidType()

        assert (
            str(err.value)
            == f"Cannot compare a `{self.fmt_type.__name__}` instance to an instance of `InvalidType`"
        )

    def test_repr(self, sut: TypeFormatter):
        assert repr(sut) == f"{self.fmt_type.__name__}({self.type.__name__})"

    def test_call(self, sut: TypeFormatter):
        with pytest.raises(NotImplementedError) as err:
            sut(self.type())

        assert str(err.value) == f"{repr(sut)}.__call__ is not implemented"

    @patch("pformat.type_specific_callable.has_valid_type")
    def test_has_valid_type(self, mock_has_valid_type, sut: TypeFormatter):
        class DummyType:
            pass

        dummy = DummyType()

        sut.has_valid_type(dummy)
        mock_has_valid_type.assert_called_once_with(dummy, self.type, False)

        mock_has_valid_type.reset_mock()

        sut.has_valid_type(dummy, exact_match=True)
        mock_has_valid_type.assert_called_once_with(dummy, self.type, True)

    def test_validate_type_invalid(self, sut: TypeFormatter):
        invalid_value = InvalidType()
        expected_err_msg = (
            f"[{repr(sut)}] Cannot process an object of type `InvalidType` - `{str(invalid_value)}`"
        )

        with pytest.raises(TypeError) as err_1:
            sut._validate_type(invalid_value)
        assert str(err_1.value) == expected_err_msg

        with pytest.raises(TypeError) as err_2:
            sut._validate_type(invalid_value, exact_match=True)
        assert str(err_2.value) == expected_err_msg

    def test_validate_type_valid(self, sut: TypeFormatter):
        assert_does_not_throw(sut._validate_type, self.type())
        assert_does_not_throw(sut._validate_type, self.type(), True)

    def test_validate_type_derived_with_exact_match(self, sut: TypeFormatter):
        derived_type = gen_derived_type(self.type)
        derived_value = derived_type()
        with pytest.raises(TypeError) as err:
            sut._validate_type(derived_value, exact_match=True)

        assert (
            str(err.value)
            == f"[{repr(sut)}] Cannot process an object of type `{derived_type.__name__}` - `{str(derived_value)}`"
        )


class TestCustomFormatter:
    @pytest.fixture(params=TYPES, ids=[f"t={t.__name__}" for t in TYPES])
    def sut(self, request: pytest.FixtureRequest) -> CustomFormatter:
        self.type = request.param
        self.fmt_func = lambda obj, depth: str(obj)
        return CustomFormatter(self.type, self.fmt_func)

    def test_call_with_invalid_type(self, sut: CustomFormatter):
        invalid_value = InvalidType()
        with pytest.raises(TypeError) as err:
            sut(invalid_value)

        assert (
            str(err.value)
            == f"[{repr(sut)}] Cannot process an object of type `InvalidType` - `{str(invalid_value)}`"
        )

    def test_call_with_correct_type(self, sut: CustomFormatter):
        value = TYPES_DICT[self.type]
        assert sut(value) == self.fmt_func(value, depth=0)

    @pytest.mark.parametrize("t", TYPES)
    def test_formatter_builder(self, t: type):
        fmt_func = lambda x, depth: str(x)
        sut = make_formatter(t, fmt_func)

        assert isinstance(sut, CustomFormatter)

        value = t()
        assert sut(value) == fmt_func(value, depth=0)
