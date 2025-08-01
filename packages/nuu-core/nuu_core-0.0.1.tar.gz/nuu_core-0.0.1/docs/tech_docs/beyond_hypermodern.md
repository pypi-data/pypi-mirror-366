CHRIS ARDERNE
Home
Blog
Books
Photos
Beyond Hypermodern: Python is easy now
19 Jul 2024

📢 Update: since writing this, I’ve released a new project called Una that makes Python monorepos easy. It’s still alpha quality and currently only works with uv, but it’s improving and growing.

\_📢 Update 2: uv is nearing feature-parity with Rye, so at some point soon I’ll update this post to use that instead. It’ll be an almost drop-in replacement.

📢 Update 3: I’ve now updated this to use uv.

It feels like eons, but it was actually just four years ago that Hypermodern Python did the rounds, going over the latest Best Practises™ for Python tooling. I remember reading it with a feeling of panic: I need to install like 20 packages, configure 30 more and do all this stuff just to write some Python.

But now it’s 2024, and it’s finally all easy! A bunch of people saw how easy all this stuff was in Go and Rust, and did some amazing work to drag the Python ecosystem forward. It’s no longer clever or special to do this stuff; everyone should be doing it.

If you just want the template, it’s coming below in the TLDR. Otherwise hang in, I’m going to follow much the same structure as the original Hypermodern posts, as follows:

Setup
Linting
Typing
Testing
Documentation
CI/CD
Monorepo (bonus section!)
If you’re already using uv, much of this won’t be new to you. But the monorepo section is where things get more interesting and there might be some new ideas there!

TLDR Here’s the template repository: carderne/postmodern-python. Start from there, and the README will give you all the commands you need to know.

#Setup
Out with pyenv and Poetry, in with Rye. No out with Rye, in with uv! Rye was created by Armin Ronacher (creator of Flask and much more), adopted by Astral, and more or less replaced with uv. Despite the VC-backed vibes of Astral, it’s actually really well-thought-through and entirely based on the new Python packaging standards. Unlike Poetry, which did what was necessary before those standards existed, but is now just a bit weird and unnecessarily different.

uv will also install Python for you, creating and respecting a .python-version in the process. Then it helps you manage your pyproject.toml dependencies in a standard way (or leaves you to do it yourself), creates lock files (but normal ones that pip can understand, not Poetry-specific ones) and mostly gets out of the way. And because it’s all written in Rust (duh), it’s fast.

Convinced? Let’s start. First off, install uv:

# if you don't like doing this, go to their website and find another way

curl -LsSf https://astral.sh/uv/install.sh | sh
Then we can start a new project

So let’s start a new project.

uv init postmodern
cd postmodern
uv sync # create lockfiles, install Python deps
uv will create some structure and setup files for you.

$ tree -a .

.
├── .git # uv init'd a git repo
├── .gitignore # along with some standard ignores
├── .python-version # and a Python version
├── .venv
│ └── ... # deps will be installed here
├── README.md
├── hello.py # we'll move this shortly
├── pyproject.toml # manage dependencies and config
└── uv.lock # lockfile
By default, uv creates an “app” with a bare hello.py. If you run uv init --lib it’ll do something a bit different. The only really interesting thing here is the pyproject.toml. A quick history lesson: Python used to use a setup.py script for installing libraries, which everyone agreed was crazy. There was a brief dalliance with setup.cfg but then PEP-518 /PEP-621/PEP-631 came along and saved the day by standardising around pyproject.toml. Poetry started in the middle of all this, so it had to invent its own system. But now we have standards, so let’s have a look:

[project]
name = "postmodern"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"

# Public libraries should be more lenient.

# Internal stuff shoulduse 3.13!

requires-python = ">= 3.13"

# Your empty (for now) dependency table

dependencies = []
Now you can install dependencies by running for example uv add pydantic which will add it to your dependency table. Note that uv defaults to >= rather than ~=, but you should probably use the latter (the difference is explained here). It’ll prevent you from getting accidentally upgraded to Pydantic v3! Let’s also add Ruff: uv add --dev ruff.

dependencies = [
"pydantic>=2.10.4",
]

[dependency-groups]
dev = [
"ruff>=0.8.5",
]
You can also just edit these dependencies manually (this is what I usually do), and just run uv sync whenever you do, to update your uv.lock (you shouldn’t edit these manually) and your venv. Speaking of lockfiles, feel free to have a look.

Before we move on, there’s something core to uv’s philosophy that’s worth putting here in bold: we don’t “activate” virtual envs any more! It’s not necessary, and makes everyone’s life more complicated. Just use uv run. Want a Python REPL based on your current venv: uv run python. Want to run Ruff: uv run ruff. Or a Python script: uv run ./hello.py. You get the picture.

Make it runnable
First of all, let’s move our code into a folder and turn it into a package:

mkdir postmodern
touch postmodern/**init**.py
mv hello.py postmodern/
There are a few different kinds of project you could be building, and that affects the kinds of things you’ll want to add to the above. If you’re building an a CLI tool or similar, there are two things you might want to add, depending on how you’re expecting people to use it. The one is a **main**.py next to your **init**.py. This lets people run your code using python -m postmodern which is vary handy if they don’t want to mess with their $PATH.

# postmodern/**init**.py

def main() -> None:
print("Hello!")

# postmodern/**main**.py

from postmodern import main
main()
The next is to add a script in the standard Python way. The example below will mean that, after installing your library/app with pip, it will be added to their $PATH and they can run it as postmodern from the command line.

# add these to your pyproject.toml

[uv.tool]

# tell uv we're building a package

# (i.e. something we can distribute for others to use)

package = true

[project.scripts]

# running `postmodern` will run the `postmodern.main` function

postmodern = "postmodern.hello:main"
Public projects
Of course if your code will only ever be imported, you don’t need an entrypoint. But if you’re building a public package (i.e., you’ll publish it to pypi), you should decide how many Python versions you want to support, and set the requires-python value appropriately. Python 3.9 is is with us for 10 more months so I think it’s fair to support >= 3.9. If you think your users are more cutting-edge you can nudge higher. The only downside of supporting older versions is missing out on the many improved things in 3.10, 3.11, 3.12 and 3.13.

If it’s an internal library or app (eg at your company), you should use a single version of Python across your libraries (and it should be Python 3.13) and you should ideally manage a global lockfile (more on that below.)

#Linting
(And formatting). The original Hypermodern series has testing next, but I think linting, formatting, and typing naturally come before testing. This section will be very short. Throw out black and isort and flake8 and all the rest, because Ruff now does everything they did.

We already installed it back in the setup section. So all you need to do is:

uv run ruff format # format (what black used to do)
uv run ruff check --fix # lint (what flake8 used to do)
And that’s basically it! Except you obviously want a bit of control over how this works, so you can add the following to your pyproject (and fiddle with it as you like). This isn’t necessary, but it’s worth knowing about.

[tool.ruff]

# if this is a library, enter the _minimum_ version you

# want to support, otherwise do py313

target-version = "py313"
line-length = 120 # use whatever number makes you happy

[tool.ruff.lint]

# you can see the looong list of rules here:

# https://docs.astral.sh/ruff/rules/

# here's a couple to start with

select = [
"A", # warn about shadowing built-ins
"E", # style stuff, whitespaces
"F", # important pyflakes lints
"I", # import sorting
"N", # naming
"T100", # breakpoints (probably don't want these in prod!)
]

# if you're feeling confident you can do:

# select = ["ALL"]

# and then manually ignore annoying ones:

# ignore = [...]

[tool.ruff.lint.isort]

# so it knows to group first-party stuff last

known-first-party = ["postmodern"]
Anyway, that’s all you need to know for linting (and formatting). Obviously you should get these integrated into your editor, but I’m not going to tell you how to do that.

#Typing
Types! Some people don’t like types (except he has since recanted) but writing maintainable, multi-contributor software in 2024 without types is some kind of black magic (i.e. you should avoid it). Many pixels have been spilled about the pros and cons of Python’s approach to typing. It’s great that you can ignore types for quick scripts and experiments. But if you’re starting something you except to care about in a few weeks, start with strict mode from day one. Don’t wait until the debt builds.

Hypermodern Python recommended mypy, but that’s hard to do anymore except in specific cases. Pyright is faster and generally a bit more useful, and plays much better with your LSP (editor), which is where instant type feedback is most useful. The downside is it runs on Node and needs to download the rest of the universe to work, but until someone rewrites it in Rust, that’s where we are.

So first install it:

uv add --dev pyright

# Then you can check your work

cat pyproject.toml | grep pyright -B1

# dev = [

# "pyright~=1.1.391",

Then configure it in your pyproject as below. Note we enable strict checking, which is really the most useful for a multi-contributor project. You can always add type: ignore[errorCodeHere] to lines you can’t fix, or disable specific rules that annoy you.

[tool.pyright]
venvPath = "." # uv installs the venv in the current dir
venv = ".venv" # in a folder called `.venv`
strict = ["**/*.py"] # use 'strict' checking on all files
pythonVersion = "3.13" # if library, specify the _lowest_ you support
And now you can run it with uv run pyright. And, as with the formatters/linters, you should get it integrated with your editor.

#Testing
Good old pytest has yet to be disrupted. How and where and why to write your tests is a whole thing that I’m not going to wade into now. Linting and strict type-checking will get you far in life, but a good set of fast tests will do wonders to keep your code working and, if they’re reasonably concise, well-documented too.

From a nuts-and-bolts perspective all we need to do is install pytest:

uv add --dev pytest
I’ll leave the testing to you, but let’s start with a failing test so we know pytest is doing something:

# tests/test_nothing.py

from postmodern.hello import main
def test_hello():
main("what?") # main doesn't accept any args 😉
And then:

uv run pytest

...
FAILED tests/test_import.py::test_hello -
TypeError: main() takes 0 positional arguments but 1 was given
I’ll leave fixing the test as an exercise for the reader.

#Task runner
Now that we have a couple of tools setup, we may as well make it a bit easier to remember how to run them. You could always use a Makefile but it’s overly complex for just a task runner. If you can convince your team to add extra tools, mise is fantastic.

Unfortunately, Rye had nice support for running little tasks/scripts, but uv hasn’t added that feature yet. Until it does, Poe the Poet works pretty well (despite being made for Poetry!).

Let’s install it with uv add --dev poethepoet and set it up right at the top of the pyproject.toml:

[tool.poe.tasks]

# run with eg `uv run poe fmt`

fmt = "ruff format"
lint = "ruff check --fix"
check = "pyright"
test = "pytest"

# run all the above

all = [ {ref="fmt"}, {ref="lint"}, {ref="check"}, {ref="test"} ]
Then any time you’ve made some changes or are preparing to commit, you can run uv run poe test or just run uv run poe all and the full suite of tools will get to work for you!

You can always still run uv run ruff format or whatever, but you’ll appreciate these reminders of what tools you have available, and even more as your tasks get more complex.

My predecessor recommended setting up nox for automated testing in multiple Python environments. If you don’t know what this means, or haven’t heard of nox, then you probably don’t need it. Unless you’re writing a public library targetting multiple versions of Python, you don’t need it. Even then, depending on the complexity of your project, you can probably get away with CI/CD alone (more below). And the simpler parts of nox (chaining linting, typechecking, testing) are already handled above by five lines of pyproject config.

#Documentation
We’re getting slightly away from tooling and into the weeds here, but in general my advice would be to focus on getting as much information as possible into function/class names and type signatures.

For example:

# instead of

def filter_stuff(accounts, include_closed):
...

# or even

def filter_accounts(
accounts: list[dict],
include_closed: boolean
) -> list[dict]:
...

# why not try try

class Status(Enum):
CLOSED = 0
OPEN = 1

@dataclass
class Account:
id: str
status: Status

def filter_account(
accounts: Sequence[Account],
include: Sequence[Status],
) -> list[Account]:
...
And then add docstrings to your functions and classes. Your code is fully typed, so you might not need to explain too much what goes into each parameter or what functions return. One thing you should definitely do is explain what types of Exceptions a function can raise! Maybe one day the language will have a built-in way of expressing that…

def filter_accounts(...) -> list[Account]:
"""
Filters accounts based and returns a copy.
Be careful if calling with Accounts that bla bla...
Raises:
AccountBalanceException: an Account was found that foo bar...
"""
The next thing you should do is write tests! I know, we covered that. But the clearest way to show what a bit of code does, is to show what that bit of code does! And also to show what it doesn’t (or isn’t supposed to) do. You may need some super complex multi-stage tests to validate all sorts of stateful conditions, but if you can start with a few very simple, easy to understand tests, future you and your users will have a much easier time understanding how something works. And if they’re wondering how filter_accounts works, they can grep for test_filter_accounts and maybe find the answer.

An even better solution, and something that has been done to great effect in the Rust ecosystem, is to add tests to your docstrings as in the example below. Not only are these super useful to the users of your code, pytest will ensure that they stay up-to-date by failing your test suite if the tests fail!

# postmodern/adder.py

# you can ignore the fancy Python 3.12 generic syntax if you like

def add_two[T: (int, float)](num: T) -> T:
"""
Adds two to the given `num`

    >>> res = add_two(0.5)
    >>> assert res == 2.5

    >>> res = add_two(1)
    >>> assert res == 4    # note this is wrong!
    """
    return num + 2

To get pytest in on this, add the following to your config:

# pyproject.toml

[tool.pytest.ini_options]
addopts = "--doctest-modules"
Then when you run uv run poe test, you’ll get an error something like below, so can can fix the test and get it green again.

****\_**** [doctest] postmodern.adder.add_two ****\_****
005 >>> res = add_two(0.5)
006 >>> assert res == 2.5
007
008 >>> res = add_two(1)
009 >>> assert res == 4
UNEXPECTED EXCEPTION: AssertionError()
And if you’re writing a public library, you’ll likely want public documentation at some point. You can probably get quite far with a GitHub readme and good docstrings, since modern editors make it so easy to goto-definition on source files. Mkdocs (or Sphinx) is the next step. You’ll know when you need them, and they’re not worth the trouble until then.

#CI/CD
We’re nearly there! Sharp-eyed readers will notice I didn’t include pre-commit anywhere above. This depends on your team and preferences, but there are cases where pre-commit becomes a bit of a configuration burden, doesn’t play well with polyglot codebases (eg you also want to pre-commit your TypeScript code) and can just be annoying. So I’ve excluded it by default, and we’ll instead rely on our CI. That means it’s each developers responsibility to ensure everything is linted and formatted before pushing. And if it’s not, the CI won’t let them merge to main.

Integration
What you definitely do need, whether you use pre-commit or not, is enforced no-commit-to-main on your repository and then a good CI pipeline running on your PRs that must be green before code is merged to main.

Here’s a simple example that runs all of our tools above on Github Actions. I’ve kept this as brief as possible, but you can see the fully-featured version at the repository. This will ensure, more strictly than pre-commit can, that everything that hits main is sparkling clean.

# .github/workflows/pr.yml

name: pr
on:
pull_request:
types: [opened, reopened, synchronize]
jobs:
test:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v4 - uses: astral-sh/setup-uv@v5
with:
version: "0.5.14" - run: | # abort if the lockfile changes
uv sync --all-extras --dev
[[-n $(git diff --stat requirements.lock)]] && exit 1 - run: uv run poe ci:fmt # check formatting is correct - run: uv run poe ci:lint # and linting - run: uv run poe check # typecheck too - run: uv run poe test # then run your tests!

And since I recommended against using nox (until you know you need it), this is also the spot to setup your multi-version/multi-platform testing. Github Actions allows you to define matrix strategies, where you can test a matrix of versions, platforms, etc. To add a strategy, we make these two additions to our pr.yml workflow:

    # after runs-on: ubuntu-latest
    strategy:
      matrix:
        py: ['3.10', '3.11', '3.12']

    # replace the uv setup step
      - uses: astral-sh/setup-uv@v5
        with:
          version: "0.5.14"
          python-version: $

And that’s it! Now your code will get tested against two additional Python versions.

Deployment
If you’re building a library, you might be done once your code is merged. If it’s a public library, you must tag and release a version, and push it to PyPI. You’ll also need to set a version. You can either set one manually:

[project]
name = "postmodern"
version = "0.1.0"
...
Or do it dynamically:

[project]
name = "postmodern"
dynamic = ["version"]
...

[tool.hatch.version]
source = "vcs"
The latter approach will get the version from the git tag, and saves having to manually bump stuff all over the place. Also note that you don’t need to set a **version** = "0.1.0" anywhere in your code. Interested parties can get it with:

from importlib.metadata import version
version("postmodern")
With that done, you need to actually publish it. The Github Actions workflow below shows how you can do that. For this to work, you’ll need to set up “Trusted Publisher” with PyPI. This allows you to publish without needing to copy-paste keys around (see, no keys in the workflow below!).

name: release
on:
release:
types: [published]
jobs:
publish:
environment: release # needed for PyPI OIDC
runs-on: ubuntu-latest
permissions:
id-token: write
steps: - uses: actions/checkout@v4 - uses: astral-sh/setup-uv@v5
with:
version: "0.5.14" - run: uv build - uses: pypa/gh-action-pypi-publish@release/v1
So that’s libraries. But if you’re building an App, and if that app needs to run somewhere, you probably want a Dockerfile. The Dockerfile below shows how simple this can be.

# always nice to pin as precisely as possible

FROM python:3.13.1-slim-bookworm

ENV PYTHONUNBUFFERED=True
WORKDIR /app

# "Install" uv

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# First we copy just the project definition files

# so these layers can be cached

COPY pyproject.toml uv.lock ./

# install dependencies

RUN uv sync --frozen

# now copy in all the rest as late as possible

# and depending on how we're running this, we don't even need

# to install it, just copy-paste and run

COPY . /app

# if you DO want to install it, do that here

# or however else you bootstrap your app

CMD ["/app/.venv/bin/python", "/app/postmodern/server.py"]
You’ll need to also create a .dockerignore file to prevent Docker from copying your dev virtual environment into the image:

.venv
I’ll wait while you go compare that to the Poetry approach, and I’ll wait for you to figure out how to set up a multi-stage build so you don’t have a pile of unneeded Poetry stuff left lying around in your final Docker image.

You can go read the uv docs on Docker to find some useful optimisations for your images.

#Monorepo
TLDR: Just go look at the one I put together at carderne/postmodern-mono.

This is the bonus section! If you’re building a library or a one-off, you might already be done. But if you’re building something in a big team, and you don’t have a monolith, you’re likely to have multiple apps and libraries intermingling. Python’s monorepo support isn’t great, but it works, and it is far better than the alternative repo-per-thingie approach that many teams take. The only place where separate repos make much sense is if you have teams with very different code contribution patterns. For example, a data science team that uses GitHub to collaborate on Jupyter notebooks: minimal tests or CI, potentially meaningless commit messages. Apart from that, even with multiple languages and deployment patterns, you’ll be far better off with a single repo than the repo-per-thing approach.

So, how do you monorepo with Python? If you’re in a bigger organisation, you might already have Bazel or similar (Pants, maybe?) set up for building your graph of libraries and dependencies. Although Python doesn’t need to be “built” per se, a bunch of stuff does need to be installed and copied around and having these dependencies and connections properly controlled is valuable.

If your needs aren’t that complex, you can get quite far with the standard modern tooling. uv has borrowed from Go/Rust the concept of a “workspace” that contains multiple packages that share a root. Notably, they share a lockfile (uv.lock in this case). You need to decide how coupled you want your teams to be, but it’s very likely that larger teams will need multiple workspaces in the single monorepo. This is because you can easily end up with incompatible versions, where, for example, Team A is using a library that enforces pydantic<1.0 while Team B is desperate to use another library that requires pydantic>=2.0.

It’s an organisational choice the degree to which you want to keep everyone in lockstep versus giving the flexibility to use different versions. But definitely the number of separate lockfiles should be kept as low as possible. Regardless, you’ll end up with something that looks like this:

> tree
> .
> ├── pyproject.toml # root pyproject defines the workspace
> ├── uv.lock
> ├── libs
> │ └── greeter
> │ ├── pyproject.toml # package dependencies here
> │ └── postmodern # all packages are namespaced
> │ └── greeter
> │ └── **init**.py
> └── apps

    └── server
        ├── pyproject.toml      # this one depends on libs/greeter
        ├── Dockerfile          # this one gets a Dockerfile
        └── postmodern
            └── server
                └── __init__.py

The best place to start is to have a glance at the uv Workspace docs. Then I recommend checking out the example carderne/postmodern-mono that I put together. It follows everything discussed in the post, just with the extra workspace support.

That’s that. Hopefully that was useful! Things have come a long way since Hypermodern Python was published, and writing maintainable Python has never been easier.

Update: since writing this, I’ve released a new project called Una that makes working with monorepos with uv much easier. Basically it figures out all the co-dependencies for you at build-time so your Dockerfile can be as simple as RUN pip install my_app.whl. It’s still in early development but it’s growing!
