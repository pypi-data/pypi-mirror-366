import logging
from typing import Any, List

import pytest

from playa.document import Document
from playa.parser import (
    KEYWORD_DICT_BEGIN,
    KEYWORD_DICT_END,
    InlineImage,
    Lexer,
    ObjectParser,
)
from playa.pdftypes import (
    KWD,
    LIT,
    ObjRef,
    keyword_name,
    literal_name,
)

logger = logging.getLogger(__name__)

TESTDATA1 = rb"""%!PS
begin end
 "  @ #
/a/BCD /Some_Name /foo#5f#xbaa
0 +1 -2 .5 1.234
(abc) () (abc ( def ) ghi)
(def\040\0\0404ghi) (bach\\slask) (foo\nbaa)
(this % is not a comment.)
(foo
baa)
(foo\
baa)
<> <20> < 40 4020 >
<abcd00
12345>
func/a/b{(c)do*}def
[ 1 (z) ! ]
<< /foo (bar) / (baz) >>
"""
TOKENS1 = [
    (5, KWD(b"begin")),
    (11, KWD(b"end")),
    (16, KWD(b'"')),
    (19, KWD(b"@")),
    (21, KWD(b"#")),
    (23, LIT("a")),
    (25, LIT("BCD")),
    (30, LIT("Some_Name")),
    (41, LIT("foo_")),
    (48, KWD(b"#")),
    (49, KWD(b"xbaa")),
    (54, 0),
    (56, 1),
    (59, -2),
    (62, 0.5),
    (65, 1.234),
    (71, b"abc"),
    (77, b""),
    (80, b"abc ( def ) ghi"),
    (98, b"def \x00 4ghi"),
    (118, b"bach\\slask"),
    (132, b"foo\nbaa"),
    (143, b"this % is not a comment."),
    (170, b"foo\nbaa"),
    (180, b"foobaa"),
    (191, b""),
    (194, b" "),
    (199, b"@@ "),
    (211, b"\xab\xcd\x00\x124\x50"),
    (226, KWD(b"func")),
    (230, LIT("a")),
    (232, LIT("b")),
    (234, KWD(b"{")),
    (235, b"c"),
    (238, KWD(b"do*")),
    (241, KWD(b"}")),
    (242, KWD(b"def")),
    (246, KWD(b"[")),
    (248, 1),
    (250, b"z"),
    (254, KWD(b"!")),
    (256, KWD(b"]")),
    (258, KWD(b"<<")),
    (261, LIT("foo")),
    (266, b"bar"),
    (272, LIT("")),
    (274, b"baz"),
    (280, KWD(b">>")),
]
OBJS1 = [
    (5, KWD(b"begin")),
    (11, KWD(b"end")),
    (16, KWD(b'"')),
    (19, KWD(b"@")),
    (21, KWD(b"#")),
    (23, LIT("a")),
    (25, LIT("BCD")),
    (30, LIT("Some_Name")),
    (41, LIT("foo_")),
    (48, KWD(b"#")),
    (49, KWD(b"xbaa")),
    (54, 0),
    (56, 1),
    (59, -2),
    (62, 0.5),
    (65, 1.234),
    (71, b"abc"),
    (77, b""),
    (80, b"abc ( def ) ghi"),
    (98, b"def \x00 4ghi"),
    (118, b"bach\\slask"),
    (132, b"foo\nbaa"),
    (143, b"this % is not a comment."),
    (170, b"foo\nbaa"),
    (180, b"foobaa"),
    (191, b""),
    (194, b" "),
    (199, b"@@ "),
    (211, b"\xab\xcd\x00\x124\x50"),
    (226, KWD(b"func")),
    (230, LIT("a")),
    (232, LIT("b")),
    (234, [b"c", KWD(b"do*")]),
    (242, KWD(b"def")),
    (246, [1, b"z", KWD(b"!")]),
    (258, {"foo": b"bar", "": b"baz"}),
]


SIMPLE1 = b"""1 0 obj
<<
 /Type /Catalog
 /Outlines 2 0 R
 /Pages 3 0 R
>>
endobj
"""
SIMPLETOK = [
    1,
    0,
    KWD(b"obj"),
    KEYWORD_DICT_BEGIN,
    LIT("Type"),
    LIT("Catalog"),
    LIT("Outlines"),
    2,
    0,
    KWD(b"R"),
    LIT("Pages"),
    3,
    0,
    KWD(b"R"),
    KEYWORD_DICT_END,
    KWD(b"endobj"),
]


def list_parsers(data: bytes, expected: List[Any], discard_pos: bool = False) -> None:
    bp = Lexer(data)
    if discard_pos:
        tokens: List[Any] = [tok for pos, tok in list(bp)]
    else:
        tokens = list(bp)
    assert tokens == expected


def test_new_parser() -> None:
    # Do a lot of them to make sure buffering works correctly
    list_parsers(SIMPLE1 * 100, SIMPLETOK * 100, discard_pos=True)


def test_new_parser_eof() -> None:
    # Make sure we get a keyword at eof
    list_parsers(SIMPLE1[:-1], SIMPLETOK, discard_pos=True)


PAGE17 = b"""
    /A;Name_With-Various***Characters?
    /lime#20Green
    /paired#28#29parentheses
"""


def test_new_parser1() -> None:
    list_parsers(b"123.456", [(0, 123.456)])
    list_parsers(b"+.013", [(0, 0.013)])
    list_parsers(b"123", [(0, 123)])
    list_parsers(b"true false", [(0, True), (5, False)])
    list_parsers(b"(foobie bletch)", [(0, b"foobie bletch")])
    list_parsers(b"(foo", [])


def test_new_parser_names() -> None:
    # Examples from PDF 1.7 page 17
    list_parsers(
        PAGE17,
        [
            (5, LIT("A;Name_With-Various***Characters?")),
            (44, LIT("lime Green")),
            (62, LIT("paired()parentheses")),
        ],
    )


def test_new_parser_strings() -> None:
    list_parsers(
        rb"( Strings may contain balanced parentheses ( ) and "
        rb"special characters ( * ! & } ^ % and so on ) . )",
        [
            (
                0,
                rb" Strings may contain balanced parentheses ( ) and "
                rb"special characters ( * ! & } ^ % and so on ) . ",
            )
        ],
    )
    list_parsers(b"()", [(0, b"")])
    list_parsers(
        rb"""( These \
two strings \
are the same . )
    """,
        [(0, b" These two strings are the same . ")],
    )
    list_parsers(b"(foo\rbar)", [(0, b"foo\nbar")])
    list_parsers(b"(foo\r)", [(0, b"foo\n")])
    list_parsers(b"(foo\r\nbar\r\nbaz)", [(0, b"foo\nbar\nbaz")])
    list_parsers(b"(foo\n)", [(0, b"foo\n")])
    list_parsers(rb"(foo\r\nbaz)", [(0, b"foo\r\nbaz")])
    list_parsers(rb"(foo\r\nbar\r\nbaz)", [(0, b"foo\r\nbar\r\nbaz")])
    list_parsers(
        rb"( This string contains \245two octal characters\307 . )",
        [(0, b" This string contains \245two octal characters\307 . ")],
    )
    list_parsers(rb"(\0053 \053 \53)", [(0, b"\0053 \053 +")])
    list_parsers(
        rb"< 4E6F762073686D6F7A206B6120706F702E >", [(0, b"Nov shmoz ka pop.")]
    )
    list_parsers(rb"<73 686 D6F7A2>", [(0, b"shmoz ")])
    list_parsers(rb"(\400)", [(0, b"")])


def test_invalid_strings_eof() -> None:
    list_parsers(rb"(\00", [])
    list_parsers(rb"(abracadab", [])


def test_literals():
    """Test the (actually internal) functions for interpreting
    literals as strings"""
    assert literal_name(LIT("touché")) == "touché"
    # Invalid UTF-8, but we will treat it as "ISO-8859-1"
    # (i.e. Unicode code points 0-255)
    assert keyword_name(KWD(b"\x80\x83\xfe\xff")) == "\x80\x83\xfe\xff"


def test_interns():
    """Verify that interning only accepts certain values."""
    with pytest.raises(ValueError):
        _ = KWD("not-a-bytes")
    with pytest.raises(ValueError):
        _ = LIT(b"not-a-str")


STREAMDATA = b"""
/Hello
<< /Type/Catalog/Outlines 2 0 R /Pages 3 0 R >>
[ 1 0 R ]
(foo (bar) baz...)
null null null
4 0 R
"""


def test_objects():
    """Test the basic object stream parser."""
    parser = ObjectParser(STREAMDATA)
    objects = list(parser)
    assert objects == [
        (1, LIT("Hello")),
        (
            8,
            {
                "Type": LIT("Catalog"),
                "Outlines": ObjRef(None, 2),
                "Pages": ObjRef(None, 3),
            },
        ),
        (56, [ObjRef(None, 1)]),
        (66, b"foo (bar) baz..."),
        (85, None),
        (90, None),
        (95, None),
        # Note unparsed indirect object reference
        (100, 4),
        (102, 0),
        (104, KWD(b"R")),
    ]


INLINEDATA1 = b"""
BI /L 42 ID
012345678901234567890123456789012345678901
EI
BI /Length 30 /Filter /A85 ID


<^BVT:K:=9<E)pd;BS_1:/aSV;ag~>



EI
BI
/Foo (bar)
ID
VARIOUS UTTER NONSENSE
EI
BI
/F /AHx
ID\r4f 4d 47575446\r\n\r\nEI
BI /F /AHx ID 4f4d47575446EI
BI ID(OMG)(WTF)
EI
BI
/F /A85
ID
<^BVT:K:=9<E)pd;BS_1:/aSV;ag~>
EI
BI
/F /A85
ID
<^BVT:K:=9<E)pd;BS_1:/aSV;ag~
>
EI
BI /F /A85 ID<^BVT:K:=9<E)pd;BS_1:/aSV;ag~>EI
BI
/OMG (WTF)
ID
BLAHEIBLAHBLAH\rEI
BI ID
OLD MACDONALD\rEIEIO
EI
BI ID OLDMACDONALDEIEIO EI
BI ID
OLDMACDONALDEIEIOEI
(hello world)
"""


def test_inline_images():
    parser = ObjectParser(INLINEDATA1)
    pos, img = next(parser)
    assert isinstance(img, InlineImage)
    assert img.buffer == b"012345678901234567890123456789012345678901"
    pos, img = next(parser)
    assert isinstance(img, InlineImage)
    assert img.buffer == b"VARIOUS UTTER NONSENSE"
    pos, img = next(parser)
    assert isinstance(img, InlineImage)
    assert img.attrs["Foo"] == b"bar"
    assert img.rawdata == b"VARIOUS UTTER NONSENSE"
    pos, img = next(parser)
    assert isinstance(img, InlineImage)
    assert img.buffer == b"OMGWTF"
    pos, img = next(parser)
    assert isinstance(img, InlineImage)
    assert img.buffer == b"OMGWTF"
    pos, img = next(parser)
    assert isinstance(img, InlineImage)
    assert img.buffer == b"(OMG)(WTF)"
    pos, img = next(parser)
    assert isinstance(img, InlineImage)
    assert img.buffer == b"VARIOUS UTTER NONSENSE"
    pos, img = next(parser)
    assert isinstance(img, InlineImage)
    assert img.buffer == b"VARIOUS UTTER NONSENSE"
    pos, img = next(parser)
    assert isinstance(img, InlineImage)
    assert img.buffer == b"VARIOUS UTTER NONSENSE"
    pos, img = next(parser)
    assert isinstance(img, InlineImage)
    assert img.buffer == b"BLAHEIBLAHBLAH"
    pos, img = next(parser)
    assert isinstance(img, InlineImage)
    assert img.buffer == b"OLD MACDONALD\rEIEIO"
    pos, img = next(parser)
    assert isinstance(img, InlineImage)
    assert img.buffer == b"OLDMACDONALDEIEIO"
    pos, img = next(parser)
    assert isinstance(img, InlineImage)
    assert img.buffer == b"OLDMACDONALDEIEIO"


def test_cached_inline_images():
    doc = Document(b"")
    first = list(ObjectParser(INLINEDATA1, doc, streamid=0))
    second = list(ObjectParser(INLINEDATA1, doc, streamid=0))
    assert first == second
    third = list(ObjectParser(INLINEDATA1, doc, streamid=1))
    assert first != third


def test_reverse_solidus():
    """Test the handling of useless backslashes that are not escapes."""
    parser = Lexer(rb"(OMG\ WTF \W \T\ F)")
    assert next(parser) == (0, b"OMG WTF W T F")


def test_number_syntax():
    """Verify that all types of number objects are accepted."""
    numbers = [1, 12, 1.2, 1.0, 0.2, 12.34, 12.0, 0.34]
    texts = b"1 12 1.2 1. .2 12.34 12. .34"
    objs = [obj for _, obj in Lexer(texts)]
    assert objs == numbers
    plus_texts = b" ".join((b"+" + x) for x in texts.split())
    objs = [obj for _, obj in Lexer(plus_texts)]
    assert objs == numbers
    minus_texts = b" ".join(b"-" + x for x in texts.split())
    objs = [-obj for _, obj in Lexer(minus_texts)]
    assert objs == numbers
