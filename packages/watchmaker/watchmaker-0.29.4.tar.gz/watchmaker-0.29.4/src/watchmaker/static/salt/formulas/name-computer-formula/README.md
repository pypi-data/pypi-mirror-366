[![license](https://img.shields.io/github/license/plus3it/name-computer-formula.svg)](./LICENSE)
[![Travis Build Status](https://travis-ci.org/plus3it/name-computer-formula.svg?branch=master)](https://travis-ci.org/plus3it/name-computer-formula)
[![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/github/plus3it/name-computer-formula?branch=master&svg=true)](https://ci.appveyor.com/project/plus3it/name-computer-formula)

# name-computer-formula
Cross-platform salt formula to set the computer name of a system.

## Available States

### name-computer

Set the computer name on Windows, or the hostname on Linux.

## Configuration

There are two configuration options:

*   `computername`
*   `pattern`

The `computername`, is read from a salt grain, `name-computer:computername`, or
a pillar key, `name-computer:lookup:computername`.

The `pattern` is read only from pillar, `name-computer:lookup:pattern`. The
value is a perl-compatible regular expression (PCRE). The `computername` is
tested against the pattern. The default pattern is `.*`, which matches any
value.

The logic flow is as follows:

1.  If the computername grain has a value that matches the pattern, use the
    grain value.
2.  Otherwise, if the computername pillar has a value that matches the pattern,
    use the pillar value.
3.  If neither of those conditions are met, do nothing.
