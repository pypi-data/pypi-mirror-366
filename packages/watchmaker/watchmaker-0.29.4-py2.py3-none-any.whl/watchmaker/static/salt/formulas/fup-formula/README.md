# fup-formula

A [salt formula](https://docs.saltstack.com/en/latest/topics/development/conventions/formulas.html) to facilitate package-installation via URL.

## History

**Why 'FUP'?**

We needed a name for the formula. We prefer project-names to be short (since who wants to type a lot) and this formula is designed to install arbitrary packages via URL. Thus, "From URLs: Packages" distills down to "FUP".

**Intent and Tested Use-Cases**

Originally, this formula was designed only with the intention to configure Enterprise Linux (RHEL, etc.) hosts' yum repositories through the installation of repository-configuration RPMs. However, the resultant SaltStack-based implementation proved notionally more flexible than that: _any_ OS package-management system that supports installation of packages via URL &mdash; and that is usable via SaltStack's `package` states/modules &mdash; _should_ work with this formula. That said, because it was only originally-targeted for use on Enterprise Linux systems, those are the only systems we have explicitly tested the formula on. Should anyone find that this works on other operating-systems, please feel free to let us know: we will update this README with a longer list of known-to-work operating systems.

## Available States

###  fup

Install standalone, pre-packaged software bundles from network-repositories specified by URL. To work, pre-packaged software-bundles must be supported by SaltStack's [`package` states](https://docs.saltstack.com/en/latest/ref/states/all/salt.states.pkg.html)

## Configuration

There is one configuration option:

*   `pkgs`

The `pkgs` option is a dictionary-structure read from a salt grain (or pillar item of the same name) under the `urly-packages:lookup` key-hierarchy. The keys/values in this dictionary are the name of an package to be installed (e.g., `epel-release`) and the URL to that package (e.g., `https://dl.fedoraproject.org/pub/epel/7/x86_64/Packages/e/epel-release-7-11.noarch.rpm`). Package names are names the operating-system's package-managemet system will register the installed software package under.


The logic flow is as follows:

1.  If the `pkgs` grain has a non-null value, attempt to use the grain value(s) to install yum repository-definition RPMs
2.  Otherwise, if the `pkgs` pillar-item has a non-null value, attempt to use the pillar value(s) install yum repository-definition RPMs
3.  If neither of those conditions are met, do nothing and perform a clean, silent exit (i.e., "exit `0`").
