from __future__ import annotations

import logging
import shutil
from pathlib import Path

import pytest

logging.basicConfig(level=logging.INFO, format="[*] %(message)s")

logger = logging.getLogger(__name__)


CWD = Path(__file__).parent
DIR_ROOT = CWD.parent
DIR_EXAMPLES = DIR_ROOT / "examples"


pytest_plugins = [
    "tests.fixtures.cli",
    "tests.fixtures.dirs",
    "tests.fixtures.projects",
]

slow_tests = []


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--runslow",
        action="store_true",
        default=False,
        help="Run slow tests",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    if not config.getoption("--runslow"):
        skip_slow = pytest.mark.skip(reason="需要 --runslow 选项")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[None],
) -> None:
    """自动添加slow标记."""
    if call.when == "call":
        runtime = call.duration
        if runtime > 1.0:  # 阈值设为1秒
            item.add_marker(pytest.mark.slow)
            slow_tests.append((item.name, runtime))


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:  # noqa: ARG001
    if slow_tests:
        logger.info("\n慢测试报告:")
        for name, time in slow_tests:
            logger.info(f"{name}: {time:.2f}s")
    else:
        logger.info("没有慢测试!")


@pytest.fixture
def dir_examples() -> Path:
    return DIR_EXAMPLES


@pytest.fixture(autouse=True, scope="session")
def clear_dist_folders() -> None:
    dist_folders = [x for x in DIR_EXAMPLES.rglob("dist") if x.is_dir()]
    for dist_folder in dist_folders:
        shutil.rmtree(dist_folder, ignore_errors=True)
