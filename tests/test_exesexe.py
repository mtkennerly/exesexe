try:
    from unittest import mock
except ImportError:
    import mock

import pytest

import exesexe


@pytest.mark.parametrize(
    "argv",
    [
        ("exesexe", "1", "foo"),
        ("exesexe", "1,!2,3=4", "foo", "-a", "-b"),
        ("exesexe", "5", "foo", "-h")
    ]
)
def test__parse_args(argv):
    directive, command = exesexe._parse_args(argv)
    assert argv[1] == directive
    assert argv[2:] == command


@pytest.mark.parametrize(
    "argv, code",
    [
        (["exesexe", "-h"], 0),
        (["exesexe", "--help"], 0),
        (["exesexe", "-h", "1=0", "foo"], 0),
        (["exesexe"], 1),
        (["exesexe", 2], 1),
    ]
)
def test__parse_args_help(argv, code):
    with pytest.raises(SystemExit) as e:
        exesexe._parse_args(argv)
        assert e.code == code


@pytest.mark.parametrize(
    "wl_in, bl_in, sub_in, wl_out, bl_out, sub_out",
    [
        (1, None, None, [1], [], {}),
        (None, 2, {}, [], [2], {}),
        ([], [], {1: 2}, [], [], {1: 2}),
        (0, 0, {0: 0}, [0], [0], {0: 0})
    ]
)
def test__parse_subdirectives(wl_in, bl_in, sub_in, wl_out, bl_out, sub_out):
    wl, bl, sub = exesexe._parse_subdirectives(wl_in, bl_in, sub_in)
    assert wl == wl_out
    assert bl == bl_out
    assert sub == sub_out


@pytest.mark.parametrize(
    "wl_in, bl_in, sub_in",
    [
        (None, None, None),
        ([], [], {}),
    ]
)
def test__parse_subdirectives_without_crtieria(wl_in, bl_in, sub_in):
    with pytest.raises(ValueError):
        exesexe._parse_subdirectives(wl_in, bl_in, sub_in)


@pytest.mark.parametrize(
    "directive, whitelist, blacklist, substitutions",
    [
        ("1", [1], [], {}),
        ("!2", [], [2], {}),
        ("3=0", [], [], {3: 0}),
        ("1,!2,3,4=10", [1, 3], [2], {4: 10}),
        ("-1,!-2,-3=-10", [-1], [-2], {-3: -10}),
        ("1=0,!2,*=10", [], [2], {1: 0, "*": 10}),
        ("1=0,1=2", [], [], {1: 2}),
        ("1:3", [1, 2, 3], [], {}),
        ("!1:3", [], [1, 2, 3], {}),
        ("1:3=4", [], [], {1: 4, 2: 4, 3: 4}),
        ("1:2,!3:4,5:6=7,*=9", [1, 2], [3, 4], {5: 7, 6: 7, "*": 9}),
        ("!1=2", [], [1], {"*": 2})
    ]
)
def test_parse_directive(directive, whitelist, blacklist, substitutions):
    wl, bl, sub = exesexe.parse_directive(directive)
    assert wl == whitelist
    assert bl == blacklist
    assert sub == substitutions


@pytest.mark.parametrize(
    "whitelist, blacklist, substitutions, call_code, exit_code",
    [
        ([1], [], {}, 1, 0),  # straightforward whitelist
        ([1], [], {}, 5, 5),  # whitelist fails, so no change
        ([1], [], {1: 3}, 1, 0),  # whitelist match overrides n-substitution
        ([1], [], {3: 5}, 2, 2),  # whitelist and sub fail, so no change
        ([1], [], {5: 4}, 5, 4),  # whitelist fails, but n-sub registers
        ([1], [], {"*": 5}, 1, 0),  # whitelist match overrides *-substitution
        ([1], [], {"*": 4}, 5, 4),  # whitelist fails, but *-sub registers
        ([], [2], {}, 5, 0),  # blacklist-absent, so changed to 0
        ([], [2], {}, 2, 2),  # blacklist-present, so no change
        ([], [2], {3: 4}, 3, 4),  # blacklist-absent overridden by n-sub
        ([], [2], {2: 4}, 2, 4),  # blacklist-present overridden by n-sub
        ([], [2], {"*": 4}, 1, 4),  # blacklist-absent overridden by *-sub
        ([], [2], {"*": 4}, 2, 2),  # blacklist-present overrides *-sub
        ([], [], {1: 5}, 1, 5),  # n-substitution registers
        ([], [], {1: 5}, 2, 2),  # n-substitution does not register
        ([], [], {"*": 5}, 0, 5),  # *-substitution registers
        ([], [], {1: 0, "*": 2}, 1, 0),  # n-sub matches, overrides *-sub
        ([], [], {1: 0, "*": 5}, 3, 5),  # n-sub fails, *-sub matches
        ([], [3], {1: 2, "*": 4}, 1, 2),  # n-sub overrides blacklist and *-sub
        ([1, 2], [3, 4], {2: 6}, 2, 0),  # all fields, whitelist > n-sub > blacklist
        ([1, 2], [3, 5], {5: 6}, 5, 6),  # all fields, n-sub > blacklist
        ([1], [2], {3: 4, "*": 5}, 2, 2),  # all fields, blacklist-present > *-sub
        ([1], [2], {3: 4, "*": 5}, 9, 5)  # all fields, *-sub > blacklist-absent
    ]
)
def test_interpret(whitelist, blacklist, substitutions, call_code, exit_code):
    with mock.patch("exesexe.subprocess.call", return_value=call_code):
        code = exesexe.interpret("example -f", whitelist, blacklist, substitutions)
        assert code == exit_code
