CHANGELOG
=========

PyPI pythonic-fp.fptools project.

Semantic Versioning
-------------------

Strict 3 digit semantic versioning adopted 2025-05-19.

- **MAJOR** version incremented for incompatible API changes
- **MINOR** version incremented for backward compatible added functionality
- **PATCH** version incremented for backward compatible bug fixes

See `Semantic Versioning 2.0.0 <https://semver.org>`_.

Releases and Important Milestones
---------------------------------

5.0.0 - TBD
~~~~~~~~~~~~~~~~~~

Coordinated entire project pythonic-fp PyPI deployment.

- moved maybe.py and xor.py from containers, renamed xor.py -> either.py.

4.0.0 - 2025-07-13
~~~~~~~~~~~~~~~~~~

Dropped developer status to Beta

- Development Status :: 4 - Beta
- planning to shuffle packages around a bit

TODO: After next Boring Math (bm) deployment, I should be able to archive
my dtools namespace repos

3.0.0 - 2025-07-06
~~~~~~~~~~~~~~~~~~

First PyPI release as ``pythonic-fp.fptools``

- dropping dtools namespace name because there is a repo by that name.

2.0.0 - 2025-05-22
~~~~~~~~~~~~~~~~~~

- Moved dtools.fp.err_handling to the dtools.containers PyPI project

  - Moved class MayBe -> module dtools.containers.maybe
  - Moved class Xor -> module dtools.containers.xor
  - dropped lazy methods

    - will import dtools.fp.lazy directly for this functionality

1.7.0 - 2025-04-22
~~~~~~~~~~~~~~~~~~

Last PyPI release as dtools.fp

- API changes along the lines of dtools.ca 3.12
- typing improvements
- docstring changes
- pyproject.toml standardization

1.6.1.0 - 2025-04-17
~~~~~~~~~~~~~~~~~~~~

- MB.sequence and XOR.sequence now return a wrapped iterator

  - to get a MB or XOR of the container

    - MB.sequence(list_of_mb).map(list)
    - XOR.sequence(ca_of_mb).map(CA)

  - eliminates runtime polymorphism
  - TODO: don't force a full evaluation

- Also noticed MB and XOR still have camelCase APIs

1.6.0 - 2025-04-07
~~~~~~~~~~~~~~~~~~

- typing improvements

1.4.0 - 2025-03-16
~~~~~~~~~~~~~~~~~~

- added two state changing methods to dtools.err_handling.MB

  - added put method to MB class

    - if MB is empty, injects a value into it
    - otherwise, do nothing

  - added pop method to MB class

    - if MB is not empty, remove the value and return it
    - otherwise, raise ValueError

  - found both methods useful to treat a MB just as a container

    - avoid using these methods in pure code

1.3.1 - 2025-02-05
~~~~~~~~~~~~~~~~~~

- added class method sequence to class State

1.3.0 - 2025-01-17
~~~~~~~~~~~~~~~~~~

First release as dtools.fp

Repo name changes.

- GitHub: fp -> dtools-fp
- PyPI: grscheller.fp -> dtools.fp

1.2.0 - 2025-01-04
~~~~~~~~~~~~~~~~~~

- added modules lazy and state
- renamed flatmap methods to bind
- minor MB and XOR updates/corrections

1.1.0 - 2024-11-18
~~~~~~~~~~~~~~~~~~

Added fp.function module.

- combine and partially apply functions as first class objects
- some tests may be lacking

1.0.2.0 - 2024-10-20
~~~~~~~~~~~~~~~~~~~~

Development environment only.

- breaking API changes, next PyPI release will be 1.1.0.
- renamed module ``nothingness`` to ``singletons``
 
  - split class NoValue into class NoValue and Sentinel
   
    - ``noValue`` represents a missing value
    - ``_sentinel`` is intended to provide a "private" sentinel value
     
      - frees up ``None`` and ``()`` for application use
      - avoids name collisions with user code
      - will be used in grscheller.datastructures
       
- will redo docs in docs repo

1.0.1 - 2024-10-20
~~~~~~~~~~~~~~~~~~

- removed docs from repo
- docs for all grscheller namespace projects maintained here
 
  - https://grscheller.github.io/grscheller-pypi-namespace-docs/

1.0.0 - 2024-10-18
~~~~~~~~~~~~~~~~~~

Decided to make this release first stable release.

- renamed module fp.woException to fp.err_handling
 
  - better captures module's use case
   
- pytest improvements based on pytest documentation

0.4.0 - 2024-10-03
~~~~~~~~~~~~~~~~~~

Long overdue PyPI release.

0.3.5.1 - 2024-10-03
~~~~~~~~~~~~~~~~~~~~

Development environment only.

- New module ``grscheller.fp.nothingness`` for

  - Singleton ``noValue`` representing a missing value

    - similar to ``None`` but while

      - ``None`` represent "returned no values"
      - ``noValue: _NoValue = _NoValue()`` represents an absent value

    - mostly used as an implementation detail

      - allows client code to use ``None`` as a sentinel value

    - prefer class ``MB`` to represent a missing value in client code

0.3.3 - 2024-08-25
~~~~~~~~~~~~~~~~~~

- removed woException ``XOR`` method

  - ``getDefaultRight(self) -> R``:

- added methods

  - makeRight(self, right: R|Nada=nada) -> XOR\[L, R\]:
  - swapRight(self, right: R) -> XOR\[L, R\]:

0.3.0 - 2024-08-17
~~~~~~~~~~~~~~~~~~

Class Nothing re-added but renamed class Nada.

Version grscheller.untyped.nothing for more strictly typed code.

0.2.1 - 2024-07-26
~~~~~~~~~~~~~~~~~~

PyPI grscheller.fp package release v0.2.1

- forgot to update README.md on last PyPI release
- simplified README.md to help alleviate this mistake in the future

0.2.0 - 2024-07-26
~~~~~~~~~~~~~~~~~~

- from last PyPI release

  - new fp.nothing module implementing nothing: Nothing singleton

    - represents a missing value
    - better "bottom" type than either None or ()

  - renamed ``fp.wo_exception`` to ``fp.woException``

0.1.0 - 2024-07-11
~~~~~~~~~~~~~~~~~~

Initial PyPI release as grscheller.fp

Replicated functionality from grscheller.datastructures.

- ``grscheller.datastructures.fp.MB -> grscheller.fp.wo_exception.MB``
- ``grscheller.datastructures.fp.XOR -> grscheller.fp.wo_exception.XOR``
