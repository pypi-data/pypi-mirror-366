import pytest


def add_live_test_options(parser: pytest.Parser, *, include_tree: bool = False) -> None:
    parser.addoption(
        "--live-test-verbose",
        action="store_true",
        help="Pass verbose=True to LiveTest",
    )
    parser.addoption(
        "--live-test-message-summary",
        action="store_true",
        help="Pass message_summary=True to LiveTest",
    )
    parser.addoption(
        "--child-verbose",
        action="store_true",
        help="Pass child_verbose=True to LiveTest",
    )
    parser.addoption(
        "--child-message-summary",
        action="store_true",
        help="Pass child_message_summary=True to LiveTest",
    )
    parser.addoption(
        "--parent-verbose",
        action="store_true",
        help="Pass parent_verbose=True to LiveTest",
    )
    parser.addoption(
        "--parent-message-summary",
        action="store_true",
        help="Pass parent_message_summary=True to LiveTest",
    )
    parser.addoption(
        "--parent-on-screen",
        action="store_true",
        help="Pass parent_on_screen=True to LiveTest",
    )
    if include_tree:
        parser.addoption(
            "--child1-verbose",
            action="store_true",
            help="Pass child1_verbose=True to TreeLiveTest",
        )
        parser.addoption(
            "--child1-message-summary",
            action="store_true",
            help="Pass child1_message_summary=True to TreeLiveTest",
        )
        parser.addoption(
            "--child2-verbose",
            action="store_true",
            help="Pass child2_verbose=True to TreeLiveTest",
        )
        parser.addoption(
            "--child2-message-summary",
            action="store_true",
            help="Pass child2_message_summary=True to TreeLiveTest",
        )
        parser.addoption(
            "--child2-on-screen",
            action="store_true",
            help="Pass child2_on_screen=True to TreeLiveTest",
        )
