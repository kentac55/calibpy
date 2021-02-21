from calibpy.usecase import (
    FailureOutput,
    IdInputData,
    Input,
    OutputData,
    SuccessOutput,
    SuccessOutputFactory,
)


def test_DTO_should_calc_hash() -> None:
    assert hash(IdInputData(id="foo")) == hash(IdInputData(id="foo"))


def test_Input_should_return_its_properties() -> None:
    data = IdInputData(id="foo")
    meta = {"a": 1, "b": 2}
    i = Input(data, meta)
    assert i.data is data
    assert i.meta is meta


def test_SuccessOutput_should_return_its_properties() -> None:
    class TestOutputData(OutputData):
        k: str

    data = TestOutputData(k="v")
    meta = {"a": 1, "b": 2}
    o = SuccessOutput(type_="Ok", data=data, meta=meta)
    assert o.data is data
    assert o.meta is meta
    assert o.type == "Ok"
    assert bool(o) is True


def test_SuccessOutputFactory_should_build_SuccessOutput() -> None:
    class TestOutputData(OutputData):
        k: str

    data = TestOutputData(k="v")
    assert SuccessOutputFactory.build_ok_output(data).type == "Ok"
    assert SuccessOutputFactory.build_created_output(data).type == "Created"
    assert SuccessOutputFactory.build_accepted_output(data).type == "Accepted"
    assert SuccessOutputFactory.build_no_content_output().type == "NoContent"


def test_FailureOutput_should_return_its_properties() -> None:
    e = Exception("aaa")
    meta = {"a": 1, "b": 2}
    o = FailureOutput(e, meta)
    assert o.e is e
    assert o.meta is meta
    assert bool(o) is False
