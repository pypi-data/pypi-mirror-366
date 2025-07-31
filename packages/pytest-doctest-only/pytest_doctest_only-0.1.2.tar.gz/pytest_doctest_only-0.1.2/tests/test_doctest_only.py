def test_doctest_with_regular_tests(pytester):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    pytester.makepyfile("""
        def test_sth():
            assert 1 == 1
        def bbb():
            \"\"\"
            >>> 1
            1
            \"\"\"
    """)

    # run pytest with the following cmd args
    result = pytester.runpytest(
        "--doctest-modules"
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*[100%]*",
        "* 2 passed *",
    ])

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_doctest_with_regular_tests_only_doctest(pytester):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    pytester.makepyfile("""
        def test_sth():
            assert 1 == 1
        def bbb():
            \"\"\"
            >>> 1
            1
            \"\"\"
    """)

    # run pytest with the following cmd args
    result = pytester.runpytest(
        "--doctest-modules",
        "--doctest-only"
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*[100%]*",
        "* 1 passed *",
    ])

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0
