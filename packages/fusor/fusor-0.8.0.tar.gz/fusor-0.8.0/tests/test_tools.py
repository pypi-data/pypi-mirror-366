"""Test FUSOR tools."""

import pytest
from pydantic import BaseModel, ValidationError

from fusor.exceptions import IDTranslationException
from fusor.tools import get_error_message, translate_identifier


def test_translate_identifier(fusor_instance):
    """Test that translate_identifier method works correctly."""
    expected = "ga4gh:SQ.ijXOSP3XSsuLWZhXQ7_TJ5JXu4RJO6VT"
    identifier = translate_identifier(fusor_instance.seqrepo, "NM_152263.3")
    assert identifier == expected

    identifier = translate_identifier(fusor_instance.seqrepo, "refseq:NM_152263.3")
    assert identifier == expected

    # test non-default target
    identifier = translate_identifier(
        fusor_instance.seqrepo, "ga4gh:SQ.ijXOSP3XSsuLWZhXQ7_TJ5JXu4RJO6VT", "refseq"
    )
    assert identifier == "refseq:NM_152263.3"

    # test no namespace
    with pytest.raises(IDTranslationException):
        identifier = translate_identifier(fusor_instance.seqrepo, "152263.3")

    # test unrecognized namespace
    with pytest.raises(IDTranslationException):
        identifier = translate_identifier(
            fusor_instance.seqrepo, "fake_namespace:NM_152263.3"
        )


class _TestModel(BaseModel):
    field1: int
    field2: str


def test_get_error_message():
    """Test that get_error_message works correctly"""
    # test single error message
    try:
        _TestModel(field1="not_an_int", field2="valid_str")
    except ValidationError as e:
        error_message = get_error_message(e)
        assert "should be a valid integer" in error_message

    # test multiple error messages in one ValidationError
    try:
        _TestModel(field1="not_an_int", field2=123)
    except ValidationError as e:
        error_message = get_error_message(e)
        assert "should be a valid integer" in error_message
        assert "should be a valid string" in error_message
