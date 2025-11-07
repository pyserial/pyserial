import codecs
import contextlib
import io

import pytest

import serial.tools.hexlify_codec as hexlify_codec


@pytest.fixture(scope="module", autouse=True)
def hexlify():
    """Register the hexlify codec while running tests in this module.

    In addition, return the codec info itself for use in test functions.
    """

    codec_info = hexlify_codec.getregentry()

    def search_function(name):
        return codec_info if name == codec_info.name else None

    # Register the codec and confirm it's registered.
    codecs.register(search_function)
    assert codecs.lookup(codec_info.name) == codec_info

    yield codec_info

    # Unregister the codec and confirm it's unregistered.
    codecs.unregister(search_function)
    with pytest.raises(LookupError):
        codecs.lookup(codec_info.name)


@pytest.mark.parametrize("leading", ("", " "))
@pytest.mark.parametrize("trailing", ("", " "))
def test_encode(leading, trailing):
    text = leading + "3F 40 41 42" + trailing
    assert text.encode(encoding="hexlify") == b"?@AB"


def test_encode_empty():
    assert "".encode(encoding="hexlify") == b""

@pytest.mark.parametrize(
    "data, expected",
    (
        (b"?@AB", "3F 40 41 42 "),
        (b"", ""),
    )
)
def test_decode(data, expected):
    assert data.decode(encoding="hexlify") == expected


@pytest.mark.parametrize("data", (" 3f 40 41 42 ", "3F404142"))
def test_incremental(data):
    stream = io.BytesIO()
    wrapper = io.TextIOWrapper(stream, encoding="hexlify", errors="strict")

    for c in data:
        wrapper.write(c)
    wrapper.seek(0)

    assert wrapper.read() == "3F 40 41 42 "
    assert stream.getvalue() == b"?@AB"


@pytest.mark.parametrize(
    "data, message",
    (
        ("40 4 41", "odd number of hex digits"),
        ("40 ! 41", "non-hex digit found"),
    ),
)
@pytest.mark.parametrize(
    "errors, context_manager",
    (
        ("strict", lambda msg: pytest.raises(ValueError, match=msg)),
        ("ignore", lambda msg: contextlib.nullcontext(msg)),
    )
)
def test_incremental_errors(data, message, errors, context_manager):
    stream = io.BytesIO()
    wrapper = io.TextIOWrapper(stream, encoding="hexlify", errors=errors)

    with context_manager(message):
        wrapper.write(data)
        # This will only be reached if *errors* is not "strict".
        wrapper.seek(0)
        assert wrapper.read() == "40 41 "


def test_stream_reader(hexlify):
    reader = hexlify.streamreader(io.BytesIO(b"?"))

    assert reader.read(1) == "3"
    assert reader.read(1) == "F"
    assert reader.read(1) == " "
    assert reader.read(1) == ""


def test_stream_writer(hexlify):
    stream = io.BytesIO(b"")
    writer = hexlify.streamwriter(stream)

    assert writer.write("3f 40 41 42") is None
    assert stream.getvalue() == b"?@AB"


def test_encode_error(hexlify):
    with pytest.raises(ValueError):
        hexlify.encode("!")
