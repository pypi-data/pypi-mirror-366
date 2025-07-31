"""Print a Mardown matrix of wheels."""
from copy import deepcopy
from functools import cache
import sys
from typing import Iterable
import httpx
import defopt
import json
import re
from packaging.utils import parse_wheel_filename
from wcwidth import wcswidth

__version__ = '0.3.2'


OS = str
Architecture = str
PyVersion = str


PLATFORMS = {
    'linux': ['x86_64', 'i686'],
    'windows': ['win32', 'amd64', 'arm64'],
    'mac': ['x86_64', 'arm64'],
}

Triple = tuple[PyVersion, OS, Architecture]
Matrix = dict[Triple, bool]


def get_arch(tag: str) -> Architecture:
    """Get the architecture targeted by a wheel platform tag.

    This only applies for certain OSes, so don't use this directly, use
    get_os_arch() instead.
    """
    if tag.endswith('_x86_64'):
        return 'x86_64'
    elif tag.endswith('_i686'):
        return 'i686'
    elif tag.endswith('_aarch64'):
        return 'aarch64'
    elif tag.endswith('_arm64'):
        return 'arm64'
    raise ValueError(f'Unknown architecture for {tag}')


def get_os_arches(tag: str) -> Iterable[tuple[OS, Architecture]]:
    """Identify the OS and architecture targeted by a wheel platform tag."""
    if tag.startswith('manylinux'):
        yield 'linux', get_arch(tag)
        return
    if tag.startswith('musllinux'):
        yield 'musllinux', get_arch(tag)
        return
    elif tag == 'win32':
        yield 'windows', 'win32'
        return
    elif tag == 'win_amd64':
        yield 'windows', 'amd64'
        return
    elif tag == 'win_arm64':
        yield 'windows', 'arm64'
        return
    elif tag.startswith('macosx'):
        if tag.endswith('_universal2'):
            for arch in ('x86_64', 'arm64'):
                yield 'mac', arch
        else:
            yield 'mac', get_arch(tag)
        return
    raise ValueError(f'Unknown wheel target {tag}')


@cache
def get_cpython_versions() -> list[str]:
    """Get all maintained versions of CPython.

    We use the GitHub REST API for this, to find the dev branches in the
    CPython repository. This approach excludes EOL interpreters (the branch is
    deleted) and also alpha releases (the branch is not yet cut, development
    happens on `main`.)
    """
    found: set[tuple[int, ...]] = set()
    for branch in get_github_repo_branches('python', 'cpython'):
        if mo := re.match(r'(\d+)\.(\d+)', branch):
            maj, min = mo.groups()
            found.add((int(maj), int(min)))
    return [
        'cp{}{}'.format(*v)
        for v in sorted(found, reverse=True)
    ]


def get_github_repo_branches(owner: str, repo: str) -> list[str]:
    """Fetch the branch names from a GitHub repository.

    Parameters:
    - owner: A string representing the username of the repository owner.
    - repo: A string representing the repository name.

    Returns:
    - A list of strings where each string is a branch name.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/branches"
    response = httpx.get(url).raise_for_status()
    branches = response.json()
    branch_names = [branch['name'] for branch in branches]
    return branch_names


def get_pypi_json(package: str) -> dict:
    """Get the JSON metadata about the given package."""
    return httpx.get(f'https://pypi.org/pypi/{package}/json').raise_for_status().json()


def interp_to_version(interp: str) -> tuple[int, int]:
    """Given an interpreter string, return its (major, minor) version.

    >>> interp_to_version('cp310')
    (3, 10)
    """
    if mo := re.match(r'[a-z]{2}(\d)(\d+)', interp):
        maj, minor = mo.groups()
        return int(maj), int(minor)
    raise ValueError(f"Failed to parse interpreter string {interp!r}")


def get_triples(
    wheel_filename: str,
    cpythons: list[str] | None = None,
) -> set[Triple]:
    """Get the (PyVersion, OS, Architecture) triples served by the given wheel.

    """
    if cpythons is None:
        cpythons = get_cpython_versions()

    triples = set()
    pkg, v, build, tags = parse_wheel_filename(wheel_filename)
    for tag in tags:
        if tag.abi == 'abi3':
            minversion = interp_to_version(tag.interpreter)
            interpreters = {tag.interpreter} | {
                p for p in cpythons
                if interp_to_version(p) >= minversion
            }
        else:
            interpreters = {tag.interpreter}
        for os, arch in get_os_arches(tag.platform):
            for i in interpreters:
                triples.add((i, os, arch))
    return triples


def sort_key(python: str) -> tuple:
    """Return a key with which to compare Python interpreter codes.

    CPython prefixes sort first, and versions are sorted in descending order.
    """
    if mo := re.match('([a-z]+)(\d)(\d+)', python):
        prefix, maj, min = mo.groups()
        return prefix != 'cp', prefix, -int(maj), -int(min)
    return False, python,


def identify_wheels(package: str, version: str | None = None, /):
    """Identify wheels for the given package and version.

    If version is not given it is the latest version of the package.
    """
    data = get_pypi_json(package)
    if version is None:
        version = data['info']['version']

    try:
        releases = data['releases'][version]
    except KeyError:
        sys.exit(f"{version} is not a valid version of {package}")

    pythons = get_cpython_versions()
    sdist = False
    matrix: Matrix = {}
    platforms = deepcopy(PLATFORMS)
    for r in releases:
        filename = r['filename']
        if filename.endswith('.whl'):
            for interpreter, os, arch in get_triples(filename):
                if arch not in platforms.setdefault(os, []):
                    platforms[os].append(arch)
                if interpreter not in pythons:
                    pythons.append(interpreter)
                matrix[interpreter, os, arch] = True
        elif filename.endswith('.tar.gz'):
            sdist = True

    headers = ['Python']
    table = [headers]
    for os, archs in platforms.items():
        for arch in archs:
            headers.append(f'{os} {arch}')
    pythons.sort(key=sort_key)
    for python in pythons:
        row = [python]
        for os, archs in platforms.items():
            for arch in archs:
                has_wheel = matrix.get((python, os, arch), False)
                row.append('✅' if has_wheel else '❌')
        table.append(row)

    col_widths = [0] * len(table[0])
    for row in table:
        for i, v in enumerate(row):
            col_widths[i] = max(col_widths[i], wcswidth(v))
    table.insert(1, ['-' * w for w in col_widths])

    for row in table:
        print('| {} |'.format(
            ' | '.join(v + ' ' * (w - wcswidth(v)) for v, w in zip(row, col_widths))))


def main():
    defopt.run(identify_wheels)
