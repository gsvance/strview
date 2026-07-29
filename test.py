import unittest

from strview import StrView


def is_alpha(sv: StrView) -> bool:
    return sv.isalpha()


class TestStrView(unittest.TestCase):

    def test_construct(self) -> None:
        self.assertEqual(StrView("Foo"), StrView("Foo", start=0, length=3))
        self.assertEqual(StrView("Foo"), "Foo")

    def test_strip(self) -> None:
        self.assertEqual(
            StrView("hello    "), StrView("    hello    ").lstrip(),
        )
        self.assertEqual(
            StrView("    hello"), StrView("    hello    ").rstrip(),
        )
        self.assertEqual(
            StrView("hello"), StrView("    hello    ").strip(),
        )

    def test_chop_by_delim(self) -> None:
        # Existing
        input_ = StrView("hello\nworld")
        line, input_ = input_.lchop_by_delim('\n')
        self.assertEqual(StrView("hello"), line)
        self.assertEqual(StrView("world"), input_)

        # Non-Existing
        input_ = StrView("hello\nworld")
        line, input_ = input_.lchop_by_delim(' ')
        self.assertEqual(StrView("hello\nworld"), line)
        self.assertEqual(StrView(""), input_)

    def test_chop_by_wide_delim(self) -> None:
        # Existing
        input_ = StrView("hello\nworld\ngoodbye")
        line, input_ = input_.lchop_by_delim(StrView("\nwor"))
        self.assertEqual(StrView("hello"), line)
        self.assertEqual(StrView("ld\ngoodbye"), input_)

        # Non-Existing
        input_ = StrView("hello\nworld")
        line, input_ = input_.lchop_by_delim(StrView("goodbye"))
        self.assertEqual(StrView("hello\nworld"), line)
        self.assertEqual(StrView(""), input_)

    '''
    # Try to chop by delimiter
        # Existing
        {
            String_View input = SV_STATIC("hello\nworld");
            String_View line = SV_NULL;
            bool result = sv_try_chop_by_delim(&input, '\n', &line);
            ASSERT_TRUE(result);
            ASSERT_EQ(String_View, SV("hello"), line);
            ASSERT_EQ(String_View, SV("world"), input);
        }

        # Non-Existing
        {
            String_View input = SV_STATIC("hello\nworld");
            String_View line = SV_NULL;
            bool result = sv_try_chop_by_delim(&input, ' ', &line);
            ASSERT_TRUE(!result);
            ASSERT_EQ(String_View, SV(""), line);
            ASSERT_EQ(String_View, SV("hello\nworld"), input);
        }
    '''

    def test_chop_n_characters(self) -> None:
        # Chop left
        input_ = StrView("hello")
        hell, input_ = input_.lchop(4)
        self.assertEqual(StrView("o"), input_)
        self.assertEqual(StrView("hell"), hell)

        # Overchop left
        input_ = StrView("hello")
        hell, input_ = input_.lchop(10)
        self.assertEqual(StrView(""), input_)
        self.assertEqual(StrView("hello"), hell)

        # Chop right
        input_ = StrView("hello")
        input_, hell = input_.rchop(4)
        self.assertEqual(StrView("h"), input_)
        self.assertEqual(StrView("ello"), hell)

        # Overchop right
        input_ = StrView("hello")
        input_, hell = input_.rchop(10)
        self.assertEqual(StrView(""), input_)
        self.assertEqual(StrView("hello"), hell)

    def test_take_while(self) -> None:
        # Take while is_alpha
        input_ = StrView("hello1234")
        hello = input_.ltake_while(is_alpha)
        self.assertEqual(StrView("hello1234"), input_)
        self.assertEqual(StrView("hello"), hello)

        # Overtake while
        input_ = StrView("helloworld")
        hello = input_.ltake_while(is_alpha)
        self.assertEqual(StrView("helloworld"), input_)
        self.assertEqual(StrView("helloworld"), hello)

    def test_chop_while(self) -> None:
        # Chop while is_alpha
        input_ = StrView("hello1234")
        hello, input_ = input_.lchop_while(is_alpha)
        self.assertEqual(StrView("1234"), input_)
        self.assertEqual(StrView("hello"), hello)

        # Overchop while
        input_ = StrView("helloworld")
        hello, input_ = input_.lchop_while(is_alpha)
        self.assertEqual(StrView(""), input_)
        self.assertEqual(StrView("helloworld"), hello)

    def test_equals_ignoring_case(self) -> None:
        # Exactly equal
        input_ = StrView("hello, world")
        self.assertTrue(input_.eq_ignorecase(StrView("hello, world")))

        # Equal ignoring case
        input_ = StrView("Hello, World")
        self.assertTrue(input_.eq_ignorecase(StrView("hello, world")))

        # Unequal
        input_ = StrView("Goodbye, World")
        self.assertFalse(input_.eq_ignorecase(StrView("Hello, World")))

    def test_find_and_index(self) -> None:
        index = StrView("hello world").find(' ')
        self.assertNotEqual(index, -1)
        self.assertEqual(5, index)

        sv = StrView('hi world', start=3)
        index = sv.index('w')
        self.assertEqual(0, index)

    def test_prefix_suffix_check(self) -> None:
        self.assertTrue(StrView("Hello, World").startswith(StrView("Hello")))
        self.assertTrue(StrView("Hello, World").endswith(StrView("World")))

    def test_to_integer(self) -> None:
        input_ = StrView("1234567890")

        self.assertEqual(1234567890, int(input_))
        self.assertEqual(input_, StrView("1234567890"))

        integer, input_ = input_.lchop_int()
        self.assertEqual(1234567890, integer)
        self.assertEqual(len(input_), 0)
