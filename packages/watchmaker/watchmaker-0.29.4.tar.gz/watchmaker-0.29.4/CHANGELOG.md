# Changelog

## [0.29.4](https://github.com/plus3it/watchmaker/releases/tag/0.29.4)

**Released**: 2025.08.01

**Summary**:

*   Updates dist constraints to allow watchmaker to execute on Amazon Linux 2023
*   Adjusts default config to invoke correct scap profiles for Rocky Linux and Alma Linux
*   Adds mappings for EL10 and AL2023 to default config (no support yet in ash-linux, however)
*   ash-linux
    -   Removes content related to EL7
*   scap-formula
    -   Updates openscap content to 0.1.77
    -   Adds SCAP content and salt mappings for EL10, Rocky Linux, and Amazon Linux 2023

## [0.29.3](https://github.com/plus3it/watchmaker/releases/tag/0.29.3)

**Released**: 2025.07.02

**Summary**:

*   Uses SaltStack 3007.2 in Watchmaker default config
*   Updates default config to use Salt repos compatible with Broadcom hosting
*   Switches to GitHub Actions for all test and release workflows, removing Travis-CI
    and Azure DevOps Pipelines
*   Lints all python code using black
*   scap-formula
    -   Updates openscap content to 0.1.76
    -   Includes SCAP Content for Almalinux 9, including Red Hat "stig" profile


## [0.29.2](https://github.com/plus3it/watchmaker/releases/tag/0.29.2)

**Released**: 2025.01.21

**Summary**:

*   Removes vendored get-pip submodule, which has not been used since the switch
    to the salt pip.install module in https://github.com/plus3it/watchmaker/pull/2716.
    This saves almost 60MB in package size.

## [0.29.1](https://github.com/plus3it/watchmaker/releases/tag/0.29.1)

**Released**: 2025.01.21

**Summary**:

*   Fixes deployment tooling with travis-ci since argument inputs have changed
*   No functional changes, just bumping the patch version to trigger a deployment

## [0.29.0](https://github.com/plus3it/watchmaker/releases/tag/0.29.0)

**Released**: 2025.01.21

**Summary**:

*   Adds support for Red Hat 9, CentOS Stream 9, Rocky Linux 9, Alma Linux 9, and
    Oracle Linux 9
*   Adds support for Windows Server 2022
*   Removes support for Red Hat 7 and CentOS 7
*   Removes suport for Windows Server 2016
*   ash-linux-formula
    -   Updated to support EL9 platforms
*   ash-windows-formula
    -   Updated to support Windows Server 2022 and Windows 11
*   forescout-secure-connector-formula
    -   Manages unit file for systemd service
*   domain-join-formula
    -   (Linux) Ensures FIPS crypto policies include AD suport on EL9
*   scap-formula
    -   Adds content for Windows 11 and Windows 2022
    -   Adds mappings for EL9 platforms
    -   Updates openscap content to 0.1.75

## [0.28.5](https://github.com/plus3it/watchmaker/releases/tag/0.28.5)

**Released**: 2024.06.06

**Summary**:

*   Provides several new FAQs to address recent changes and SCAP findings
*   Provides update on discontinuation of CentOS Stream 8 and possible work-around
*   ash-linux-formula
    -   Addresses findings related to UEFI-enabled systems
    -   Removes remote log entry injected by scap content
*   name-computer-formula
    -   Provides options to skip either the forward or reverse nsupdate
*   scap-formula
    -   Updates openscap content to 0.1.72

## [0.28.4](https://github.com/plus3it/watchmaker/releases/tag/0.28.4)

**Released**: 2024.03.07

**Summary**:

*   ash-linux-formula
    -   (EL8) Populates fapolicyd default rules so system remains functional after
        applying new stig controls
*   ash-linux-formula
    -   (EL8) Updates systemd boot.mount options for compatibility with UEFI
*   scap-formula
    -   (Linux) Updates openscap content to v0.1.71
    -   Updates DISA content to latest as of Jan 2024

## [0.28.3](https://github.com/plus3it/watchmaker/releases/tag/0.28.3)

**Released**: 2024.02.28

**Summary**:

*   join-domain-formula
    -   (Linux) Adds a `clean` state to simplify removing a system from the domain
*   name-computer-formula
    -   (Linux) Creates DNS records using nsupdate when `nameserver` and `dns_domain`
        are provided
*   scap-formula
    -   (Linux) Updates ComplianceAsCode scap content to v0.1.70

## [0.28.2](https://github.com/plus3it/watchmaker/releases/tag/0.28.2)

**Released**: 2023.10.31

**Summary**:

*   Updates Watchmaker default config to use Salt 3006.4
*   Documents invalid finding in EL8 for remote access monitoring methods
*   ash-linux-formula
    -   Addresses several EL8 Cat2 findings from recent SCAP scans
*   join-domain-formula
    -   (Linux) Adds cron config that refreshes AD computer object attributes

## [0.28.1](https://github.com/plus3it/watchmaker/releases/tag/0.28.1)

**Released**: 2023.10.05

**Summary**:

*   Fixes clobbering of `computer-name` grain when `computer-name-pattern` is also
    provided. This prevented the `name-computer-formula` from setting the name
    specified by the user
*   Updates FAQ to include vendor guidance for EL8.8+
*   Adds guidance on OpenSSH key signing requirements for EL8
*   ash-linux-formula
    -   Adds handler to address pam faillock findings on EL8


## [0.28.0](https://github.com/plus3it/watchmaker/releases/tag/0.28.0)

**Released**: 2023.09.14

**Summary**:

*   Add watchmaker config argument `computer_name_pattern`, and exit with error
    if provided `computer_name` does not match. Also writes grain for use with
    name-computer-formula
*   Updates default watchmaker config to use salt 3006.2
*   Documents customization options for the watchmaker salt content
*   Documents workarounds for known "gotchas" when applying EL7 and EL8 STIG controls
*   ash-linux-formula
    -   Supports customization for mapping users to different SELinux contexts
    -   Removes el7 and EL8 STIG handlers that are now provided by SCAP remediation
        content
    -   Consolidates all separate EL8 PAM handlers to states based on new authselect
        capabilities
*   join-domain-formula
    -   Adds support for `tries` option that retries a failed join domain action
    -   Integrates with ash-linux PAM handlers to apply STIG controls, if available
*   trellix-agent-formula
    -   Refactors firewalld states around newer salt functionality
*   name-computer-formula
    -   Supports reading pattern from salt grain

## [0.27.5](https://github.com/plus3it/watchmaker/releases/tag/0.27.5)

**Released**: 2023.08.07

**Summary**:

*   Adds doc section on troubleshooting Watchmaker, to include common errors, issues,
    and relevant log files
*   Updates AWS provider to support EC2 instances configured for only IMDSv2
*   ash-linux-formula
    -   Addresses additional STIG findings for EL7 and EL8
*   join-domain-formula
    -   Resolves issue with collision detection when deploying a new system
        with a hostname that already exists in the domain
    -   Corrects usage of StartTLS when searching for a computer object in the
        domain
    -   Provides several new options for controlling whether TLS is used when
        searching for a computer object in the domain, and whether an error will
        be treated as fatal or not

## [0.27.4](https://github.com/plus3it/watchmaker/releases/tag/0.27.4)

**Released**: 2023.06.28

**Summary**:

*   Updates guidance on Linux STIG findings relating to SELinux context and sudo
    privilege escalation
*   ash-linux-formula
    -   Adds additional guidance on pillar content usage
    -   Adds additional EL7 STIG handlers
    -   Removes duplicate EL7 STIG handlers for audit rules
*   forescout-secure-connector-formula
    -   Adds state to ensure correct directory ownership
*   join-domain-formula
    -   Updates sssd to support a variety of conf parameters
*   scap-formula
    -   Updates DISA SCAP content

## [0.27.3](https://github.com/plus3it/watchmaker/releases/tag/0.27.3)

**Released**: 2023.05.25

**Summary**:

*   Fixes issue with standalone binary on FIPS-enabled EL8 systems, by packaging
    libcrypto and libssl libraries in the binary

## [0.27.2](https://github.com/plus3it/watchmaker/releases/tag/0.27.2)

**Released**: 2023.05.18

**Summary**:

*   Adds support for salt 3006
*   Builds standalone executable using Python 3.10
*   Documents additional expected findings for EL8 systems
*   Uses Python 3.10 in all documentation references
*   Updates default config to use salt 3006.1
*   Uses SCC 5.7.1 in default salt content
*   ash-linux-formula
    -   Simplifies logic for managing faillock.conf
*   ash-windows-formula
    -   Updates custom modules for compatibility with Salt 3006 while remaining
        backwards compatible with salt 3005 and earlier
*   splunkforwarder-formula
    -   Sets splunk user/group on files and directories, eliminating "Changes"
        when re-executing the formula

## [0.27.1](https://github.com/plus3it/watchmaker/releases/tag/0.27.1)

**Released**: 2023.05.08

**Summary**:

*   Fixes typo in upload of Windows standalone binary to GitHub Releases
*   Documents known/spurious EL8 findings that scanning utilities may flag
    erroneously
*   Fixes the check that skips reinstalling salt when the correct version is
    already installed
*   Publishes EL8 scap scans as a release artifact to `watchmaker.cloudarmor.io`,
    alongside the standalone binaries
*   Updates scap pillar in default salt content to run scans properly on CentOS
    Stream and scap version 1.3
*   ash-linux-formula
    -   Fixes oscap remediation on CentOS Stream 8 and Oracle Linux 8
    -   Addresses numerous additional STIG findings on EL8 systems that were not
        addressed with oscap remediation
    -   Attempts to address EL8 issue with aws-cli, where fapolicyd blocks execution
*   forescout-secure-connector-formula
    -   Establishes symlink so logs are written to `/var/log` partition
*   scap-formula
    -   Updates openscap content to v0.1.67, using scap 1.3 datastreams. This also
        addresses issues with expiry on passwordless local users

## [0.27.0](https://github.com/plus3it/watchmaker/releases/tag/0.27.0)

**Released**: 2023.03.31

**Summary**:

*   Releases support for EL8 platforms, to include Red Hat 8, CentOS 8 Stream, and
    Oracle Linux 8. Future work may also add support for Rocky Linux 8 and Alma
    Linux 8
    -   CAVEAT: With this release, on FIPS-enabled EL8 systems, please use the
        [PyPi install or the source install methods](https://watchmaker.cloudarmor.io/en/stable/installation.html).
        Currently, the standalone method for EL8 **does not** work when the system
        is FIPS-enabled. The problem is not yet entirely understood. Further investigation
        is needed before this issue can be resolved
    -   UPDATE: The issue with FIPS-enabled EL8 and the standalone binary is fixed
        in Watchmaker 0.27.3
*   Updates salt worker to avoid re-installing salt when `salt-call --version`
    matches the `salt_version` in the Watchmaker config
*   Updates EL7 findings documentation to line up with latest stig version
*   Installs `dnspython` package when using default Watchmaker config, to support
    the join-domain `nsupdate` state
*   ash-linux-formula
    -   Adds handlers to address findings in latest stig versions and increase coverage
*   mcafee-agent-formula
    -   Adds a `trellix-agent` salt state to support the new name for the software
*   join-domain-formula
    -   Linux: Adds an `nsupdate` salt state that will register forward and reverse
        dns records
    -   Windows: Updates collision handling and join actions to use the same domain
        controller
    -   Windows: Supports collision handling where an existing computer object
        was created by a different service account than is now specified for the
        join action
*   winrepo: Adds a `trellix-agent` package definition


## [0.26.5](https://github.com/plus3it/watchmaker/releases/tag/0.26.5)

**Released**: 2023.03.10

**Summary**:

*   join-domain-formula
    -   Linux: Output journald logs on join-domain failures
    -   Linux: Re-order sssd conf file Salt states and explicitly set replace setting to false
    -   Linux: Patch find-collision.sh script to fix computer-object search

## [0.26.4](https://github.com/plus3it/watchmaker/releases/tag/0.26.4)

**Released**: 2023.03.03

**Summary**:

*   Attempts to fix the release automation so the Windows standalone is published
    to GitHub Releases
*   Validates functionality with salt 3005.1 and updates default config to use
    salt 3005.1
*   join-domain-formula
    -   Windows: Provides pillar options to configure DNS registration settings,
        to support registration of reverse DNS records

## [0.26.3](https://github.com/plus3it/watchmaker/releases/tag/0.26.3)

**Released**: 2023.02.27

**Summary**:

*   Skips provider detection when provider requirements are not installed
*   Updates watchmaker salt log config to avoid capturing senstive data in salt log
*   forescout-secure-connector-formula
    - Adds support for EL8 when FIPS is enabled
*   name-computer-formula
    - Sets hostname as fqdn when `dns_domain` is provided
*   join-domain-formula
    - Runs fix-collision script when using sssd
    - Updates fix-collision to avoid capturing sensitive values in salt log
    - Updates sssd method to set extra os attributes only when requested
    - Updates windows join script to avoid capturing sensitive values in salt log

## [0.26.2](https://github.com/plus3it/watchmaker/releases/tag/0.26.2)

**Released**: 2023.02.13

**Summary**:

*   Fixes publishing of Windows standalone to GitHub Releases
*   docs
    - Provides guidance on using S3 URL feature in config references
    - Describes prerequisites for using AWS and Azure features
    - Removes references to EL6 and Python 2.6
    - Removes references to deprecated `--s3-url` argument
*   join-domain-formula
    - Adds support for EL8, using `sssd` to perform the domain-join

## [0.26.1](https://github.com/plus3it/watchmaker/releases/tag/0.26.1)

**Released**: 2023.02.08

**Summary**:

*   Uses pyinstaller directly to build standalone packages, eliminating dependency
    on gravitybee
*   Uses new python apis to reference package metadata and resources, improving
    support for alternative packaging methods, like in-memory runtimes (pyoxidizer)
    or ziparchives
*   Adds PEP517 package metadata
*   [Alpha] Allows watchmaker to run on Red Hat Enterprise Linux 8, Centos 8 Stream,
    Oracle Linux 8, Alma Linux 8, and Rocky Linux 8. Currently on the ash-linux
    hardening formula will work; none of the other salt formulas have yet been
    updated for EL8 support
*   ash-windows
    - Fixes warning in `lgpo` module about using `is` instead of `==` to compare
      string-literal values

## 0.26.0

**Commit Delta**: [Change from 0.25.0 release](https://github.com/plus3it/watchmaker/compare/0.25.0...0.26.0)

**Released**: 2022.12.21

**Summary**:

*   Adds support for posting to a status provider. Initial capability supports
    AWS and will post the Watchmaker status to an EC2 instance tag. Status values
    include "Running", "Completed", or "Failed". For more information on this feature,
    see <https://watchmaker.cloudarmor.io/en/stable/configuration.html#status>.
*   [Alpha] Support posting status to Azure as a Virtual Machine tag
*   [Alpha] Support for EL8 platforms is improving but still in development. Targeted
    platforms include: Red Hat Enterprise Linux 8, Centos 8 Stream, Oracle Linux 8,
    Alma Linux 8, and Rocky Linux 8
*   ash-linux-formula
    - Supports EL8 platforms
*   join-domain-formula
    - Fixes hostname logic so automatic renaming works correctly
*   scap-formula
    - Supports EL8 platforms

## 0.25.0

**Commit Delta**: [Change from 0.24.3 release](https://github.com/plus3it/watchmaker/compare/0.24.3...0.25.0)

**Released**: 2022.10.05

**Summary**:

*   [Alpha] Begins initial preparation to support running watchmaker on EL8 platforms
*   forescout-secure-connector-formula
    - First release that packages a formula for ForeScout Secure Connector

## 0.24.3

**Commit Delta**: [Change from 0.24.2 release](https://github.com/plus3it/watchmaker/compare/0.24.2...0.24.3)

**Released**: 2022.09.16

**Summary**:

*   ash-linux-formula
    - Adds check to ensure root account password is set to not expire
*   join-domain-formula
    - Removes PAM Lsass login re-configuration

## 0.24.2

**Commit Delta**: [Change from 0.24.1 release](https://github.com/plus3it/watchmaker/compare/0.24.1...0.24.2)

**Released**: 2022.08.16

**Summary**:

*   scap-formula
    - Updates OpenSCAP and DISA STIG content
    - Linux: Adds EL8 content
*   watchmaker-salt-content
    - Windows: Re-adds scap scan using public distributable SCC 5.5

## 0.24.1

**Commit Delta**: [Change from 0.24.0 release](https://github.com/plus3it/watchmaker/compare/0.24.0...0.24.1)

**Released**: 2022.07.27

**Summary**:

*   Builds Linux standalone with python 3.8
*   Updates default config to use Salt 3004.2
*   Updates Windows usage docs with requirement to enforce modern TLS versions
*   join-domain-formula
    - Windows: Quotes path when running scripts to configure local admin group
*   ash-linux-formula
    - Tests if grub.cfg exists before attempting to modify it

## 0.24.0

**Commit Delta**: [Change from 0.23.4 release](https://github.com/plus3it/watchmaker/compare/0.23.4...0.24.0)

**Released**: 2022.03.09

**Summary**:

*   Updates default config to use Salt 3004
*   scap-formula
    - Fixes invalid requisite reference for scap.scan

## 0.23.4

**Commit Delta**: [Change from 0.23.3 release](https://github.com/plus3it/watchmaker/compare/0.23.3...0.23.4)

**Released**: 2021.12.20

**Summary**:

*   ash-windows: Adds baseline `ash-windows.cis_1_3_0`
*   Builds python 3.8 into standalone binary instead of python 3.6
*   Uses SERVER_AUTH for ssl context, fixing bug resulting from incorrect use of CLIENT_AUTH previously

## 0.23.3

**Commit Delta**: [Change from 0.23.2 release](https://github.com/plus3it/watchmaker/compare/0.23.2...0.23.3)

**Released**: 2021.09.28

**Summary**:

*   Added publishing of SCAP reports for Linux systems with each release
*   Fixed CLI behavior when passing 'none' value, e.g. `--salt-states none`
*   Updated default config to use Salt 3003.3
*   mcafee-agent-formula
    - (Linux) Refactored to allow install over an existing installation

## 0.23.2

**Commit Delta**: [Change from 0.23.1 release](https://github.com/plus3it/watchmaker/compare/0.23.1...0.23.2)

**Released**: 2021.08.11

**Summary**:

*   Patched Salt worker to be case-sensitive when processsing Salt states
*   Refactored Salt states handling between CLI and config.yaml
*   Standalone packages are now based on EL7 and are no longer compatible with EL6 (EL6 hasn't been supported for a while now)

## 0.23.1

**Commit Delta**: [Change from 0.23.0 release](https://github.com/plus3it/watchmaker/compare/0.23.0...0.23.1)

**Released**: 2021.07.15

**Summary**:

*   ash-linux-formula
    - Supports managing FIPS when / and /boot are on the same partition
    - Allows `oscap remediate` to exit non-zero on valid errors
*   Supports parsing extra_arguments when passed using `=` as the separator
    - E.g. `--user-formulas='{"foo-formula": "https://url-to/foo-formula.zip"}'`

## 0.23.0

**Commit Delta**: [Change from 0.22.2 release](https://github.com/plus3it/watchmaker/compare/0.22.2...0.23.0)

**Released**: 2021.07.08

**Summary**:

*   Adds capability to run extra states after highstate
    - E.g. from cli, `--salt-states highstate,foo,bar`
    - E.g. in config file, `salt_states: highstate,foo,bar`
*   Adds capability to pass complex worker arguments on the cli as JSON or YAML
    - E.g. `--user-formulas '{"foo-formula": "https://url-to/foo-formula.zip"}'`

## 0.22.2

**Commit Delta**: [Change from 0.22.1 release](https://github.com/plus3it/watchmaker/compare/0.22.1...0.22.2)

**Released**: 2021.06.17

**Summary**:

*   ash-linux-formula
    - Patches RHEL-07-040810 to apply to only iptables-services RPM and not core-package iptables RPM

## 0.22.1

**Commit Delta**: [Change from 0.22.0 release](https://github.com/plus3it/watchmaker/compare/0.22.0...0.22.1)

**Released**: 2021.05.11

**Summary**:

*   ash-linux-formula/nessus-agent-formula
    - Patches maxdepth parameter to use integer type to support Jinja rendering in Salt 3003

## 0.22.0

**Commit Delta**: [Change from 0.21.9 release](https://github.com/plus3it/watchmaker/compare/0.21.9...0.22.0)

**Released**: 2021.05.07

**Summary**:

*   Updates default config.yaml to use Salt 3003
*   ash-linux-formula
    - Adds ability to selectively skip extra EL7 STIG handlers
*   nessus-agent-formula
    - (Linux) Updates nessus-agent to call install and configure states

## 0.21.9

**Commit Delta**: [Change from 0.21.8 release](https://github.com/plus3it/watchmaker/compare/0.21.8...0.21.9)

**Released**: 2021.04.26

**Summary**:

*   Provides support for Salt 3003
*   ash-linux-formula
    - Updates syntax to support Salt 3003
    - RHEL-07-040160 - Ensure no (competing) attempts to set TMOUT
    - RHEL-07-040860 - Adds ability to handle lack of /etc/sysct.conf file
*   nessus-agent-formula
    - Separate agent install and configuration to support baked-in Nessus agent installations
*   join-domain-formula
    - (Windows) Add double-quotes to Members parameter in order for startup task state to work with Salt 3003

## 0.21.8

**Commit Delta**: [Change from 0.21.7 release](https://github.com/plus3it/watchmaker/compare/0.21.7...0.21.8)

**Released**: 2021.03.11

**Summary**:

*   Updated CI configs to set the correct version for the Windows standalone package.
    Effectively, this version is the same as 0.21.7.

## 0.21.7

**Commit Delta**: [Change from 0.21.6 release](https://github.com/plus3it/watchmaker/compare/0.21.6...0.21.7)

**Released**: 2021.03.10

**Summary**:

*   ash-linux-formula
    - Coordinates `sshd` service restarts across all states that modify `/etc/sshd_config`,
      so the service restarts only once. This avoids systemd failures when the
      service restarts too frequently. See [ash-linux-formula PR #303](https://github.com/plus3it/ash-linux-formula/pull/303).

## 0.21.6

**Commit Delta**: [Change from 0.21.5 release](https://github.com/plus3it/watchmaker/compare/0.21.5...0.21.6)

**Released**: 2021.03.03

**Summary**:

*   ash-linux-formula
    - Adds patch to re-enable NOPASSWD sudo for users in /etc/sudoers.d/ after oscap remediation.

## 0.21.5

**Commit Delta**: [Change from 0.21.4 release](https://github.com/plus3it/watchmaker/compare/0.21.4...0.21.5)

**Released**: 2021.02.25

**Summary**:

*   ash-linux-formula
    - Replace `watch` with `listen` to restart the `sshd` service a single time
    - Make state RHEL-07-040560 more resilient when the yum group info is missing
*   scap-formula
    - Updates SCAP content from DISA (as of February 2021) and OpenSCAP (v0.1.54)
*   Update watchmaker default `config.yaml` to use salt v2019.2.8
*   Ability to browse [Watchmaker Cloudarmor repo](https://watchmaker.cloudarmor.io/list.html)

## 0.21.4

**Commit Delta**: [Change from 0.21.3 release](https://github.com/plus3it/watchmaker/compare/0.21.3...0.21.4)

**Released**: 2020.12.04

**Summary**:

*   nessus-agent-formula
    - (Linux) Switch to using Salt service state to ensure Nessus agent service is running

## 0.21.3

**Commit Delta**: [Change from 0.21.2 release](https://github.com/plus3it/watchmaker/compare/0.21.2...0.21.3)

**Released**: 2020.10.26

**Summary**:

*   watchmaker-salt-content
    - (Linux) Updates scap-formula pillar to use alternative stig profile parameter for Red Hat

## 0.21.2

**Commit Delta**: [Change from 0.21.1 release](https://github.com/plus3it/watchmaker/compare/0.21.1...0.21.2)

**Released**: 2020.10.05

**Summary**:

*   (Windows) Removes winrepo.genrepo usage in Salt worker since it's no longer required

## 0.21.1

**Commit Delta**: [Change from 0.21.0 release](https://github.com/plus3it/watchmaker/compare/0.21.0...0.21.1)

**Released**: 2020.08.20

**Summary**:

*   splunkforwarder-formula
    - (Linux) Patches splunkforwarder state to work with Splunk Universal Forwarder v7.3.6

## 0.21.0

**Commit Delta**: [Change from 0.20.5 release](https://github.com/plus3it/watchmaker/compare/0.20.5...0.21.0)

**Released**: 2020.08.12

**Summary**:

*   Updates default watchmaker config.yaml to use salt 2019.2.5

## 0.20.5

**Commit Delta**: [Change from 0.20.4 release](https://github.com/plus3it/watchmaker/compare/0.20.4...0.20.5)

**Released**: 2020.07.16

**Summary**:

*   splunkforwarder-formula
    - (Linux) Patches splunkforwarder state to work with salt 2019.2.5

## 0.20.4

**Commit Delta**: [Change from 0.20.3 release](https://github.com/plus3it/watchmaker/compare/0.20.3...0.20.4)

**Released**: 2020.07.15

**Summary**:

*   splunkforwarder-formula
    - (Windows) Patches splunkforwarder state to work with salt 2019.2.5

## 0.20.3

**Commit Delta**: [Change from 0.20.2 release](https://github.com/plus3it/watchmaker/compare/0.20.2...0.20.3)

**Released**: 2020.07.07

**Summary**:

*   join-domain-formula
    - (Linux) Fixes issue with admin users not being able to sudo

## 0.20.2

**Commit Delta**: [Change from 0.20.1 release](https://github.com/plus3it/watchmaker/compare/0.20.1...0.20.2)

**Released**: 2020.07.01

**Summary**:

*   scap-formula
    - Updates SCAP content from DISA (as of June 2020) and OpenSCAP (v0.1.50)

## 0.20.1

**Commit Delta**: [Change from 0.20.0 release](https://github.com/plus3it/watchmaker/compare/0.20.0...0.20.1)

**Released**: 2020.05.19

**Summary**:

*   ash-linux-formula
    - Fixes issue with Postfix occasionally failing to start

## 0.20.0

**Commit Delta**: [Change from 0.19.0 release](https://github.com/plus3it/watchmaker/compare/0.19.0...0.20.0)

**Released**: 2020.05.06

**Summary**:

*   Adds capability to install Python packages using Pip in Salt's Python interpreter

## 0.19.0

**Commit Delta**: [Change from 0.18.2 release](https://github.com/plus3it/watchmaker/compare/0.18.2...0.19.0)

**Released**: 2020.05.01

**Summary**:

*   Updates Watchmaker file permissions and makes them more restrictive
*   Adds new SaltWorker optional argument `--salt-content-path` that allows specifying glob pattern for
    salt files located within salt archive file

## 0.18.2

**Commit Delta**: [Change from 0.18.1 release](https://github.com/plus3it/watchmaker/compare/0.18.1...0.18.2)

**Released**: 2020.04.02

**Summary**:

*   vault-auth-formula
    - Rename state to vault-auth
    - Add url keyword argument to read_secret execution module

## 0.18.1

**Commit Delta**: [Change from 0.18.0 release](https://github.com/plus3it/watchmaker/compare/0.18.0...0.18.1)

**Released**: 2020.03.23

**Summary**:

*   Updates version constraint in default config to allow newer versions

## 0.18.0

**Commit Delta**: [Change from 0.17.5 release](https://github.com/plus3it/watchmaker/compare/0.17.5...0.18.0)

**Released**: 2020.03.23

**Summary**:

*   Removes deprecated `emet-formula` and `dotnet4-formula` submodules
*   Adds new `vault-auth-formula` submodule
*   ash-windows-formula
    -   Replaces usage of Apply_LGPO_Delta.exe with native python and salt functionality
    -   Addresses additional findings for domain-joined systems
    -   Removes deprecated baselines from Windows Server 2008 R2, 8.1, and IE 8, 9, and 10

## 0.17.5

**Commit Delta**: [Change from 0.17.4 release](https://github.com/plus3it/watchmaker/compare/0.17.4...0.17.5)

**Released**: 2020.03.13

**Summary**:

*   join-domain-formula
    -   Allow use of password with Linux join domain capability

## 0.17.4

**Commit Delta**: [Change from 0.17.3 release](https://github.com/plus3it/watchmaker/compare/0.17.3...0.17.4)

**Released**: 2020.02.28

**Summary**:

*   ash-linux-formula
    -   Updates custom STIGbyID baseline to address several scan findings.
*   Add content for RHEL-07-040530/SV-86899

## 0.17.3

**Commit Delta**: [Change from 0.17.2 release](https://github.com/plus3it/watchmaker/compare/0.17.2...0.17.3)

**Released**: 2020.02.26

**Summary**:

*   dotnet4-formula
    -   Fix compatibility with Windows Server 2019 by using 2019 hotfixes
*   ash-linux-formula
    -   Improvements for STIGv2r6
    -   Fix collisions caused by cat2 IDs and DISA numbering change
    -   Use Salt Stack version 2019.2-2

## 0.17.2

**Commit Delta**: [Change from 0.17.1 release](https://github.com/plus3it/watchmaker/compare/0.17.1...0.17.2)

**Released**: 2020.02.25

**Summary**:

*   Documents configuration vs cli argument handling and precedence
*   Provides a table mapping common scan findings to an associated Finding ID
*   Restores propagation of the `None` value on the cli to the workers
*   ash-linux-formula
    -   Ensures aide configuration complies with FIPS requirements
*   ash-windows-formula
    -   Adds missing sls to restore support for Windows 10
*   join-domain-formula
    -   Suppresses join-domain command in salt log output
    -   (Windows) Supports using salt-native pillar security for the `password` value
*   nessus-agent-formula
    -   (Linux) Suppresses gpg verification so the pkg can be installed from a URL

## 0.17.1

**Commit Delta**: [Change from 0.17.0 release](https://github.com/plus3it/watchmaker/compare/0.17.0...0.17.1)

**Released**: 2020.01.28

**Summary**:

*   Fixes release date in changelog for 0.17.0
*   Removes salt worker special handling for `salt_states` since it is now handled
    properly in the `Arguments()` class
*   pshelp-formula
    -   Updates PowerShell help content, including Windows Server 2019

## 0.17.0

**Commit Delta**: [Change from 0.16.7 release](https://github.com/plus3it/watchmaker/compare/0.16.7...0.17.0)

**Released**: 2020.01.21

**Summary**:

*   Add support for Windows Server 2019
*   Use native markdown processing for PyPI long description
*   Deprecate use of 'None' (string) in `config.yaml`
*   Add optional `watchmaker_version` node to configuration
*   Use Salt 2018.3.4 in default configuration

## 0.16.7

**Commit Delta**: [Change from 0.16.6 release](https://github.com/plus3it/watchmaker/compare/0.16.6...0.16.7)

**Released**: 2020.01.06

**Summary**:

*   Pins `PyYAML` dependency when running on Python 3.4 or earlier

## 0.16.6

**Commit Delta**: [Change from 0.16.5 release](https://github.com/plus3it/watchmaker/compare/0.16.5...0.16.6)

**Released**: 2019.12.04

**Summary**:

*   Uses CDN URLs for watchmaker config and content, instead of direct S3 URLs
*   Pins `backoff` dependency when running on Python 3.4 or earlier

## 0.16.5

**Commit Delta**: [Change from 0.16.4 release](https://github.com/plus3it/watchmaker/compare/0.16.4...0.16.5)

**Released**: 2019.09.23

**Summary**:

*   join-domain-formula
    -   Add support for restricting Active Directory sites that will be consulted if the `ad_site_name` key-value is set in the pillar
*   ash-linux-formula
    -   Fix issue with log spamming by `systemd` related to file permissions
*   ash-windows-formula
    -   Update STIG baselines for 2019-07 SCAP content
*   scap-formula
    -   Rename DISA content files to reflect SCAP version
    -   Update DISA SCAP content to July 2019 release
*   salt-content
    -   Update SCAP pillar to match filename changes in SCAP formula

## 0.16.4

**Commit Delta**: [Change from 0.16.3 release](https://github.com/plus3it/watchmaker/compare/0.16.3...0.16.4)

**Released**: 2019.08.23

**Summary**:

*   Updates documentation on pip usage in Linux to always use `python3 -m pip...`
*   dotnet4-formula
    -   Adds .NET Framework 4.8 version and associated KB to lookup tables
*   fup-formula
    -   New salt formula to install packages via URL
*   scap-formula
    -   (Windows) Adds configuration to allow scan results to be generated when using SCC v5.0.2 and higher
*   watchmaker-salt-content
    -   (Windows) Adds .NET Framework 4.8 info to dotnet winrepo package content

## 0.16.3

**Commit Delta**: [Change from 0.16.2 release](https://github.com/plus3it/watchmaker/compare/0.16.2...0.16.3)

**Released**: 2019.08.7

**Summary**:

*   join-domain-formula
    -   (Linux) Modifies method used to retrieve hostname to avoid issues with `hostname -f`
    -   (Linux) Improves error messaging if tooling dependencies are not installed
    -   (Linux) Modifies domain controller search mechanism to preserve compatibility with EL6
    -   (Linux) Logs the computer name in the domain-join output
*   mcafee-agent-formula
    -   (Linux) Adds a pillar option to pass args to the mcafee agent installer
    -   (Linux) Fixes match on OS version to ensure firewall ports are opened
*   name-computer-formula
    -   (Linux) Updates /etc/hosts with hostname fqdn, when the domain name is provided

## 0.16.2

**Commit Delta**: [Change from 0.16.1 release](https://github.com/plus3it/watchmaker/compare/0.16.1...0.16.2)

**Released**: 2019.07.11

**Summary**:

*   join-domain-formula
    -   Fixes detection of running system's join state, searches for shortname, and retries joins
    -   Improves compatibility with strict Bash
    -   Adds option to skip GPG check
*   amazon-inspector-formula
    -   Adds option to skip GPG check
*   splunkforwarder-formula
    -   Redirects splunk log folder with symlink
    -   Adds option to skip GPG check

## 0.16.1

**Commit Delta**: [Change from 0.16.0 release](https://github.com/plus3it/watchmaker/compare/0.16.0...0.16.1)

**Released**: 2019.06.21

**Summary**:

*   join-domain-formula
    -   Updates find-collision.sh ldap search to include uppercase and lowercase versions of provided hostname
*   scap-formula
    -   Adds script to build OSCAP content with 'stig' profile included for CentOS
    -   Updates OSCAP content to v0.1.44
*   watchmaker-salt-content
    -   Switches Linux scap profile pillar settings to 'stig'

## 0.16.0

**Commit Delta**: [Change from 0.15.2 release](https://github.com/plus3it/watchmaker/compare/0.15.2...0.16.0)

**Released**: 2019.05.10

**Summary**:

*   Adds salt content locally as a submodule to better support Watchmaker standalone packages
*   dotnet4-formula
    -   Updates formula to support the use of Python3 versions of Salt
*   join-domain-formula
    -   Adds additional enhancements and logic to better handle the domin-join process in Linux

## 0.15.2

**Commit Delta**: [Change from 0.15.1 release](https://github.com/plus3it/watchmaker/compare/0.15.1...0.15.2)

**Released**: 2019.04.12

**Summary**:

*   ash-linux-formula
    -   Removes outdated and conflicting states to allow setting of custom banner text
*   join-domain-formula
    -   Fixes issue with improper handling of admin names with spaces in Windows

## 0.15.1

**Commit Delta**: [Change from 0.15.0 release](https://github.com/plus3it/watchmaker/compare/0.15.0...0.15.1)

**Released**: 2019.04.05

**Summary**:

*   join-domain-formula
    -   (Linux) Avoids `unique` jinja filter to preserve compatibility for older
        versions of salt

## 0.15.0

**Commit Delta**: [Change from 0.14.2 release](https://github.com/plus3it/watchmaker/compare/0.14.2...0.15.0)

**Released**: 2019.04.04

**Summary**:

*   Updates documentation to install pip using `ensurepip` module instead of external
    `get-pip.py`
*   ash-linux-formula
    -   Adds pillar option to set content for `/etc/issue` login banner
*   join-domain-formula
    -   (Linux) Adds pillar option to pass a list of domains to add to the trust
        list

## 0.14.2

**Commit Delta**: [Change from 0.14.1 release](https://github.com/plus3it/watchmaker/compare/0.14.1...0.14.2)

**Released**: 2019.03.26

**Summary**:

*   join-domain-formula
    -   Corrects regression on Windows to support adding admin groups that have
        spaces in the name

## 0.14.1

**Commit Delta**: [Change from 0.14.0 release](https://github.com/plus3it/watchmaker/compare/0.14.0...0.14.1)

**Released**: 2019.03.18

**Summary**:

*   Fixes Python 2.6 incompatibility introduced by new version of PyYAML
*   join-domain-formula
    -   Fixes issue adding admin groups/users to Windows systems with recent versions of Salt

## 0.14.0

**Commit Delta**: [Change from 0.13.0 release](https://github.com/plus3it/watchmaker/compare/0.13.0...0.14.0)

**Released**: 2019.03.06

**Summary**:

*   Adds additional documentation to answer common EL7 security scan findings
*   ash-linux-formula
    -   Implements additional Salt states to address security scan issues
        -   Capability to manage GRUB password configuration
        -   IgnoreRhosts setting in SSH daemon configuration
        -   CIS remediation handlers ( CIS 5.2.3, CIS 5.2.5)
    -   Adds Salt state to update audit-rule changes without a system reboot
*   scap-formula
    -   Updates SCAP Security Guide content to v0.1.41

## 0.13.0

**Commit Delta**: [Change from 0.12.1 release](https://github.com/plus3it/watchmaker/compare/0.12.1...0.13.0)

**Released**: 2019.01.29

**Summary**:

*   amazon-inspector-formula
    - New salt formula distributed with watchmaker
    - Installs amazon-inspector agent
*   Refactor watchmaker
    - Change naming mechanism from LinuxManager to LinuxPlatformManager
    - Change naming mechanism from WindowsManager to WindowsPlatformManager
    - Change naming mechanism from Manager to PlatformManager
    - Added abstract class WorkerBase for Workers to inherit from
*   ash-linux-formula
    - Change ipv6 check to use if_inet6 file
    - Import correct source of fopen function
    - Configure Postfix to only use ipv4 when ipv6 is disabled

## 0.12.1

**Commit Delta**: [Change from 0.12.0 release](https://github.com/plus3it/watchmaker/compare/0.12.0...0.12.1)

**Released**: 2018.12.17

**Summary**:

*   ash-windows-formula
    -   Corrects yaml syntax error in win2016 DC baseline

## 0.12.0

**Commit Delta**: [Change from 0.11.0 release](https://github.com/plus3it/watchmaker/compare/0.11.0...0.12.0)

**Released**: 2018.12.13

**Summary**:

*   Adds `valid_environments` option to config to allow for the restriction of environment selection

## 0.11.0

**Commit Delta**: [Change from 0.10.3 release](https://github.com/plus3it/watchmaker/compare/0.10.3...0.11.0)

**Released**: 2018.11.08

**Summary**:

*   Adds enhancement to ensure `--admin-groups` parameters are lowercase on Linux systems
*   Adds additional information to the `--version` flag
*   Default values are now shown in help output
*   scap-formula
    -   Incorporates content from latest DISA SCAP benchmarks
        -   Microsoft .Net Framework 4 STIG Benchmark - Ver 1, Rel 5
        -   Microsoft Windows 2008 R2 DC STIG Benchmark - Ver 1, Rel 5
        -   Microsoft Windows 2008 R2 MS STIG Benchmark - Ver 1, Rel 30
        -   Microsoft Windows Server 2016 STIG Benchmark - Ver 1, Rel 31
        -   Red Hat 6 STIG Benchmark - Ver 1, Rel 21
        -   Red Hat 7 STIG Benchmark - Ver 2, Rel 1

## 0.10.3

**Commit Delta**: [Change from 0.10.2 release](https://github.com/plus3it/watchmaker/compare/0.10.2...0.10.3)

**Released**: 2018.10.18

**Summary**:

*   ash-windows-formula
    -   Updates Formula to Support Salt 2017.7.x and 2018.3.x
    -   Removed admin account rename from delta state

## 0.10.2

**Commit Delta**: [Change from 0.10.1 release](https://github.com/plus3it/watchmaker/compare/0.10.1...0.10.2)

**Released**: 2018.09.27

**Summary**:

*   Adds a gitlab-ci pages config to build Watchmaker docs
*   Uses new hosting location to retrieve Salt packages
*   Restricts click version on py2.6
*   ash-windows-forumula
    -   New hosting location being used for all packages
*   pshelp-formula
    -   Removed byte-order-mark unicode character at beginning of init.sls file

## 0.10.1

**Commit Delta**: [Change from 0.10.0 release](https://github.com/plus3it/watchmaker/compare/0.10.0...0.10.1)

**Released**: 2018.08.09

**Summary**:

*   No functional changes; just patches the CI/release configuration

## 0.10.0

**Commit Delta**: [Change from 0.9.6 release](https://github.com/plus3it/watchmaker/compare/0.9.6...0.10.0)

**Released**: 2018.08.08

**Summary**:

*   Provides standalone packages that bundle the Python runtime together with
    Watchmaker and its dependencies
    - See <https://watchmaker.cloudarmor.io/en/stable/installation.html>
*   ash-linux-formula
    -   (el7) Ensures packages are up-to-date
    -   (el7) Ensures firewalld is installed and running
*   splunk-forwarder-formula
    -   (linux) Uses a symlink to ensure logs are in the /var/log partition
*   dotnet4-formula
    -   Adds support for .NET 4.7.2
*   nessus-agent-formula
    -   New salt formula distributed with Watchmaker

## 0.9.6

**Commit Delta**: [Change from 0.9.5 release](https://github.com/plus3it/watchmaker/compare/0.9.5...0.9.6)

**Released**: 2018.05.16

**Summary**:

*   windows-update-agent-formula
    -   Supports new windows update settings, `AlwaysAutoRebootAtScheduledTime`
        and `AlwaysAutoRebootAtScheduledTimeMinutes`
*   scap-formula
    -   Incorporates content from OpenSCAP Security Guide v0.1.39-1

## 0.9.5

**Commit Delta**: [Change from 0.9.4 release](https://github.com/plus3it/watchmaker/compare/0.9.4...0.9.5)

**Released**: 2018.04.11

**Summary**:

*   [[PR #574][574]] Updates Windows userdata example to execute pip using
    `python -m` when upgrading pip
*   windows-update-agent-formula
    -   Uses newer arguments for reg state, `vname` and `vdata`
    -   Reduces duplication in windows update data model
    -   Nests the windows update pillar options under the standard `lookup` key

[574]: https://github.com/plus3it/watchmaker/pull/574

## 0.9.4

**Commit Delta**: [Change from 0.9.3 release](https://github.com/plus3it/watchmaker/compare/0.9.3...0.9.4)

**Released**: 2018.04.09

**Summary**:

*   ash-windows-formula
    -   Updates STIG baselines to address all findings in latest SCAP
        benchmarks

## 0.9.3

**Commit Delta**: [Change from 0.9.2 release](https://github.com/plus3it/watchmaker/compare/0.9.2...0.9.3)

**Released**: 2018.03.08

**Summary**:

*   scap-formula
    -   Incorporates content from OpenSCAP Security Guide v0.1.38-1
    -   Incorporates content from latest DISA SCAP benchmarks
        -   Microsoft Internet Explorer 11 STIG Benchmark - Ver 1, Rel 11
        -   Microsoft Windows 10 STIG Benchmark - Ver 1, Rel 10
        -   Microsoft Windows 2008 R2 DC STIG Benchmark - Ver 1, Rel 27
        -   Microsoft Windows 2008 R2 MS STIG Benchmark - Ver 1, Rel 28
        -   Microsoft Windows 2012 and 2012 R2 DC STIG Benchmark - Ver 2, Rel 11
        -   Microsoft Windows 2012 and 2012 R2 MS STIG Benchmark - Ver 2, Rel 11
        -   Microsoft Windows 8/8.1 STIG Benchmark - Ver 1, Rel 21
        -   Microsoft Windows Server 2016 STIG Benchmark - Ver 1, Rel 4
        -   Red Hat 6 STIG Benchmark - Ver 1, Rel 18
        -   Red Hat 7 STIG Benchmark - Ver 1, Rel 2
*   dotnet4-formula
    -   Skips dotnet4 hotfix install if a newer version is already installed
    -   Creates per-OS maps for hotfix updates, since the hotfix id varies per
        OS

## 0.9.2

**Commit Delta**: [Change from 0.9.1 release](https://github.com/plus3it/watchmaker/compare/0.9.1...0.9.2)

**Released**: 2018.02.20

**Summary**:

*   dotnet4-formula
    -   Passes version correctly to module.run

## 0.9.1

**Commit Delta**: [Change from 0.9.0 release](https://github.com/plus3it/watchmaker/compare/0.9.0...0.9.1)

**Released**: 2018.02.17

**Summary**:

*   This version was effectively a no-op, as the submodule was not updated as
    intended
*   ~dotnet4-formula~
    -   ~Passes version correctly to module.run~

## 0.9.0

**Commit Delta**: [Change from 0.8.0 release](https://github.com/plus3it/watchmaker/compare/0.8.0...0.9.0)

**Released**: 2018.02.12

**Summary**:

*   [[Issue #499][499]][[PR #513][513]] Includes additional details about the
    platform and python version in the watchmaker log
*   [[Issue #500][500]][[PR #512][512]] Retries file retrieval up to 5 times
*   [[Issue #501][501]][[PR #507][507]] Uses urllib handlers to retrieve all
    files
    -   Deprecates the argument `--s3-source`; to retrieve a file from an S3
        bucket use the syntax: `s3://<bucket>/<key>`
    -   Local files may be specified as absolute or relative paths, and may or
        may not be prefixed with `file://`
*   [[PR #496][496]] Moves CloudFormation and Terraform templates to their own
    project, [terraform-aws-watchmaker][terraform-aws-watchmaker]
*   [[PR #491][491]] Improves compatibility of the watchmaker bootstrap.ps1
    script when executed by an Azure custom script extension
*   [[Issue #430][430]][[PR #487][487]] Writes watchmaker salt config to a
    custom path:
    -   Windows: `C:\Watchmaker\Salt\conf`
    -   Linux: `/opt/watchmaker/salt`
*   scap-formula
    -   Incorporates content from OpenSCAP Security Guide v0.1.37-1

[430]: https://github.com/plus3it/watchmaker/issues/430
[499]: https://github.com/plus3it/watchmaker/issues/499
[500]: https://github.com/plus3it/watchmaker/issues/500
[501]: https://github.com/plus3it/watchmaker/issues/501
[487]: https://github.com/plus3it/watchmaker/pull/487
[491]: https://github.com/plus3it/watchmaker/pull/491
[496]: https://github.com/plus3it/watchmaker/pull/496
[507]: https://github.com/plus3it/watchmaker/pull/507
[512]: https://github.com/plus3it/watchmaker/pull/512
[513]: https://github.com/plus3it/watchmaker/pull/513
[terraform-aws-watchmaker]: https://github.com/plus3it/terraform-aws-watchmaker

## 0.8.0

**Commit Delta**: [Change from 0.7.2 release](https://github.com/plus3it/watchmaker/compare/0.7.2...0.8.0)

**Released**: 2018.01.02

**Summary**:

*   [[Issue #415][415]][[PR #458][458]] Forwards watchmaker log entries from the
    Windows Event Log to the EC2 System Log (Windows-only)
*   [[PR #425][425]] Adds a log handler that writes watchmaker log entries to
    the Windows Event Log (Windows-only)
*   [[Issue #434][434]][[PR #457][457]] Updates doc build to replace
    `recommonmark` functionality entirely with `m2r`
*   [[PR #437][437]] Modfies CloudFormation templates to use aws cli utility to
    retrieve the appscript rather than use the functionality built-in to the
    cfn bootstrap
*   [[PR #467][467]] Sets environment variables for aws cli when executing the
    appscript option in the watchmaker CloudFormation templates

[415]: https://github.com/plus3it/watchmaker/issues/415
[434]: https://github.com/plus3it/watchmaker/issues/434
[425]: https://github.com/plus3it/watchmaker/pull/425
[437]: https://github.com/plus3it/watchmaker/pull/437
[457]: https://github.com/plus3it/watchmaker/pull/457
[458]: https://github.com/plus3it/watchmaker/pull/458
[467]: https://github.com/plus3it/watchmaker/pull/467

## 0.7.2

**Commit Delta**: [Change from 0.7.1 release](https://github.com/plus3it/watchmaker/compare/0.7.1...0.7.2)

**Released**: 2017.12.13

**Summary**:

*   Installs `futures` only on Python 2 -- no functional changes

## 0.7.1

**Commit Delta**: [Change from 0.7.0 release](https://github.com/plus3it/watchmaker/compare/0.7.0...0.7.1)

**Released**: 2017.12.04

**Summary**:

*   Fixes readthedocs build -- no functional changes

## 0.7.0

**Commit Delta**: [Change from 0.6.6 release](https://github.com/plus3it/watchmaker/compare/0.6.6...0.7.0)

**Released**: 2017.11.21

**Summary**:

*   [[PR #409][409]] Provides terraform modules that deploy the watchmaker
    CloudFormation templates
*   [[Issue #418][418]][[PR #419][419]] Adds an `exclude-states` argument to
    the SaltWorker; specified states will be excluded from the salt state
    execution
*   ash-windows-formula
    *   Incorporates security settings from the DISA October quarterly release
*   join-domain-formula
    *   (Windows) Adds WMI method to set DNS search suffix
    *   (Windows) Tests for the EC2Config XML settings file before modifying it
*   scap-formula
    *   (Linux) Distributes scap content from SCAP Security Guide v0.1.36-1
    *   Distributes scap content from the DISA October quarterly release
*   splunkforwarder-formula
    *   Supports configuration of splunk log sources from pillar and grains
        inputs

[409]: https://github.com/plus3it/watchmaker/pull/409
[419]: https://github.com/plus3it/watchmaker/pull/419
[418]: https://github.com/plus3it/watchmaker/issues/418

## 0.6.6

**Commit Delta**: [Change from 0.6.5 release](https://github.com/plus3it/watchmaker/compare/0.6.5...0.6.6)

**Released**: 2017.10.18

**Summary**:

*   ash-linux-formula
    *   (el7) Fixes typos in the firewalld "safety" scripts that resulted in a
        failure when firewalld was reloaded
*   mcafee-agent-formula
    *   (el7) Adds required inbound ports to all firewalld zones, to support
        the event where the default zone is modified from "public"
*   splunkforwarder-formula
    *   (el7) Adds required outbound ports to the OUTPUT chain; previously,
        they were mistakenly being added as inbound rules

## 0.6.5

**Commit Delta**: [Change from 0.6.4 release](https://github.com/plus3it/watchmaker/compare/0.6.4...0.6.5)

**Released**: 2017.09.29

**Summary**:

*   [[PR #391][391]] Updates CloudFormation templates with a parameter that
    exposes the option to use the S3 API and the instance role to retrieve the
    Watchmaker content archive
*   ash-linux-formula
    *   (el7) Updates firewalld "safety" state so that firewalld remains in the
        active state; the prior approach left firewalld dead/inactive, until
        the service was restarted or the system was rebooted

[391]: https://github.com/plus3it/watchmaker/pull/391

## 0.6.4

**Commit Delta**: [Change from 0.6.3 release](https://github.com/plus3it/watchmaker/compare/0.6.3...0.6.4)

**Released**: 2017.09.22

**Summary**:

*   [[PR #381][381]] Restricts `wheel` version on Python 2.6 to be less than or
    equal to 0.29.0, as `wheel` 0.30.0 removed support for py26.

[381]: https://github.com/plus3it/watchmaker/pull/381

## 0.6.3

**Commit Delta**: [Change from 0.6.2 release](https://github.com/plus3it/watchmaker/compare/0.6.2...0.6.3)

**Released**: 2017.08.11

**Summary**:

*   ash-linux-formula
    *   (el7) Includes a "safety" state for firewalld that ensures SSH inbound
        access will remain available, in the event the default zone is set to
        "drop"

## 0.6.2

**Commit Delta**: [Change from 0.6.1 release](https://github.com/plus3it/watchmaker/compare/0.6.1...0.6.2)

**Released**: 2017.08.07

**Summary**:

*   ash-linux-formula
    *   (el6) Improve the method of disabling the sysctl option `ip_forward`,
        to account for the behavior of the `aws-vpc-nat` rpm
*   scap-formula
    *   (elX) Updates openscap security guide content to version 0.1.34-1

## 0.6.1

**Commit Delta**: [Change from 0.6.0 release](https://github.com/plus3it/watchmaker/compare/0.6.0...0.6.1)

**Released**: 2017.08.01

**Summary**:

*   ash-linux-formula
    *   Modified the FIPS custom execution module to discover the boot
        partition and add the `boot=` line to the grub configuration

## 0.6.0

**Commit Delta**: [Change from 0.5.1 release](https://github.com/plus3it/watchmaker/compare/0.5.1...0.6.0)

**Released**: 2017.07.25

**Summary**:

*   ash-linux-formula
    *   Updates the EL7 stig baseline to manage the FIPS state. The state
        defaults to `enabled` but can be overridden via a pillar or grain,
        `ash-linux:lookup:fips-state`. The grain takes precedence over the
        pillar. Valid values are `enabled` or `disabled`
*   ash-windows-formula
    *   Updates the STIG baselines for Windows Server 2016 member servers and
        domain controllers with SCAP content from the DISA v1r1 SCAP benchmark
        release
*   join-domain-formula
    *   Fixes an issue when joining Windows 2016 servers to a domain, where the
        Set-DnsSearchSuffix.ps1 helper would fail because the builtin
        PowerShell version does not work when `$null` is used in a ValidateSet.
        The equivalent value must now be passed as the string, `"null"`
*   scap-formula
    *   Adds SCAP content for the Window Server 2016 SCAP v1r1 Benchmark

## 0.5.1

**Commit Delta**: [Change from 0.5.0 release](https://github.com/plus3it/watchmaker/compare/0.5.0...0.5.1)

**Released**: 2017.07.08

**Summary**:

*   [[Issue #341][341]][[PR #342][342]] Manages selinux around salt state
    execution. In some non-interactive execution scenarios, if selinux is
    enforcing it can interfere with the execution of privileged commands (that
    otherwise work fine when executed interactively). Watchmaker now detects if
    selinux is enforcing and temporarily sets it to permissive for the duration
    of the salt state execution

[342]: https://github.com/plus3it/watchmaker/pull/342
[341]: https://github.com/plus3it/watchmaker/issues/341

## 0.5.0

**Commit Delta**: [Change from 0.4.4 release](https://github.com/plus3it/watchmaker/compare/0.4.4...0.5.0)

**Released**: 2017.06.27

**Summary**:

*   [[Issue #331][331]][[PR #332][332]] Writes the `role` grain to the key
    expected by the ash-windows formula. Fixes usage of the `--ash-role` option
    in the salt worker
*   [[Issue #329][329]][[PR #330][330]] Outputs watchmaker version at the debug
    log level
*   [[Issue #322][322]][[PR #323][323]][[PR #324][324]] Fixes py2/py3
    compatibility bug in how the yum worker handles file opening to check the
    Linux distro
*   [[Issue #316][316]][[PR #320][320]] Improves logging when salt state
    execution fails due to failed a state. The salt output is now returned to
    the salt worker, which processes the output, identifies the failed state,
    and raises an exception with the state failure
*   join-domain-formula
    *   (Linux) Reworks the pbis config states to make the logged output more
        readable

[332]: https://github.com/plus3it/watchmaker/pull/332
[331]: https://github.com/plus3it/watchmaker/issues/331
[330]: https://github.com/plus3it/watchmaker/pull/330
[329]: https://github.com/plus3it/watchmaker/issues/329
[324]: https://github.com/plus3it/watchmaker/pull/324
[323]: https://github.com/plus3it/watchmaker/pull/323
[322]: https://github.com/plus3it/watchmaker/issues/322
[320]: https://github.com/plus3it/watchmaker/pull/320
[316]: https://github.com/plus3it/watchmaker/issues/316

## 0.4.4

**Commit Delta**: [Change from 0.4.3 release](https://github.com/plus3it/watchmaker/compare/0.4.3...0.4.4)

**Released**: 2017.05.30

**Summary**:

*   join-domain-formula
    *   (Linux) Ignores a bad exit code from pbis config utility. The utility
        will return exit code 5 when modifying the NssEnumerationEnabled
        setting, but still sets the requested value. This exit code is now
        ignored

## 0.4.3

**Commit Delta**: [Change from 0.4.2 release](https://github.com/plus3it/watchmaker/compare/0.4.2...0.4.3)

**Released**: 2017.05.25

**Summary**:

*   name-computer-formula
    *   (Linux) Uses an alternate method of working around a bad code-path in
        salt that does not handle quoted values in /etc/sysconfig/network.

## 0.4.2

**Commit Delta**: [Change from 0.4.1 release](https://github.com/plus3it/watchmaker/compare/0.4.1...0.4.2)

**Released**: 2017.05.19

**Summary**:

*   [[PR #301][301]] Sets the grains for admin_groups and admin_users so the
    keys are named as expected by the join-domain formula
*   ash-linux-formula
    *   Adds a custom module that lists users from the shadow file
    *   Gets local users from the shadow file rather than `user.list_users`.
        Prevents a domain-joined system from attempting to iterate over all
        domain users (and potentially deadlocking on especially large domains)
*   join-domain-formula
    *   Modifies PBIS install method to use RPMs directly, rather than the
        SHAR installer
    *   Updates approaches to checking for collisions and current join status
        to better handle various scenarios: not joined, no collision; not
        joined, collision; joined, computer object present; joined, computer
        object missing
    *   Disables NSS enumeration to prevent PBIS from querying user info from
        the domain for every call to getent (or equivalents); domain-based
        user authentication still works fine
*   name-computer-formula
    *   (Linux) Does not attempt to retain network settings, to avoid a bug in
        salt; will be revisited when a patched salt version has been released

[301]: https://github.com/plus3it/watchmaker/pull/301

## 0.4.1

**Commit Delta**: [Change from 0.4.0 release](https://github.com/plus3it/watchmaker/compare/0.4.0...0.4.1)

**Released**: 2017.05.09

**Summary**:

*   (EL7) Running _watchmaker_ against EL7 systems will now pin the resulting
    configuration to the watchmaker version. See the updates to the two
    formulas in this version. Previously, _ash-linux_ always used the content
    from the `scap-security-guide` rpm, which was updated out-of-sync with
    _watchmaker_, and so the resulting configuration could not be pinned by
    pinning the _watchmaker_ version. With this version, _ash-linux_ uses
    content distributed by _watchmaker_, via _scap-formula_, and so the
    resulting configuration will always be same on EL7 for a given version of
    _watchmaker_ (as has always been the case for the other supported
    operating systems).
*   ash-linux-formula
    *   Supports getting scap content locations from pillar
*   scap-formula
    *   Updates stig content with latest benchmark versions
    *   Adds openscap ds.xml content, used to support remediate actions

## 0.4.0

**Commit Delta**: [Change from 0.3.1 release](https://github.com/plus3it/watchmaker/compare/0.3.1...0.4.0)

**Released**: 2017.05.06

**Summary**:

*   [[PR #286 ][286]] Sets the computername grain with the correct key expected
    by the formula
*   [[PR #284 ][284]] Converts cli argument parsing from `argparse` to `click`.
    This modifies the `watchmaker` depedencies, which warranted a 0.x.0 version
    bump. Cli and API arguments remain the same, so the change should be
    backwards-compatible.
*   name-computer-formula
    *   Adds support for getting the computername from pillar
    *   Adds support for validating the specified computername against a
        pattern
*   pshelp-formula
    *   Attempts to address occasional stack overflow exception when updating
        powershell help

[286]: https://github.com/plus3it/watchmaker/pull/286
[284]: https://github.com/plus3it/watchmaker/pull/284

## 0.3.1

**Commit Delta**: [Change from 0.3.0 release](https://github.com/plus3it/watchmaker/compare/0.3.0...0.3.1)

**Released**: 2017.05.01

**Summary**:

*   [[PR #280][280]] Modifies the dynamic import of boto3 to use only absolute
    imports, as the previous approach (attempt absolute and relative import)
    was deprecated in Python 3.3
*   ntp-client-windows-formula:
    *   Stops using deprecated arguments on reg.present states, which cleans up
        extraneous log messages in watchmaker runs under some configurations
*   join-domain-formula:
    *   (Windows) Sets the DNS search suffix when joining the domain, including
        a new pillar config option, `ec2config` to enable/disable the EC2Config
        option that also modifies the DNS suffix list.

[280]: https://github.com/plus3it/watchmaker/pull/280

## 0.3.0

**Commit Delta**: [Change from 0.2.4 release](https://github.com/plus3it/watchmaker/compare/0.2.4...0.3.0)

**Released**: 2017.04.24

**Summary**:

*   [[Issue #270][270]] Defaults to a platform-specific log directory when
    call from the CLI:
    *   Windows: `${Env:SystemDrive}\Watchmaker\Logs`
    *   Linux: `/var/log/watchmaker`
*   [[PR #271][271]] Modifies CLI arguments to use explicit log-levels rather
    than a verbosity count. Arguments have been adjusted to better accommodate
    the semantics of this approach:
    *   Uses `-l|--log-level` instead of `-v|--verbose`
    *   `-v` and `-V` are now both used for `--version`
    *   `-d` is now used for `--log-dir`

[271]: https://github.com/plus3it/watchmaker/pull/271
[270]: https://github.com/plus3it/watchmaker/issues/270

## 0.2.4

**Commit Delta**: [Change from 0.2.3 release](https://github.com/plus3it/watchmaker/compare/0.2.3...0.2.4)

**Released**: 2017.04.20

**Summary**:

*   Fixes a bad version string

## 0.2.3

**Commit Delta**: [Change from 0.2.2 release](https://github.com/plus3it/watchmaker/compare/0.2.2...0.2.3)

**Released**: 2017.04.20

**Summary**:

*   [[Issue #262][262]] Merges lists in pillar files, rather than overwriting
    them
*   [[Issue #261][261]] Manages the enabled/disabled state of the salt-minion
    service, before and after the install
*   splunkforwarder-formula
    *   (Windows) Ignores false bad exits from Splunk clone-prep-clear-config

[262]: https://github.com/plus3it/watchmaker/issues/262
[261]: https://github.com/plus3it/watchmaker/issues/261

## 0.2.2

**Commit Delta**: [Change from 0.2.1 release](https://github.com/plus3it/watchmaker/compare/0.2.1...0.2.2)

**Released**: 2017.04.15

**Summary**:

*   [[PR #251][251]] Adds CloudFormation templates that integrate Watchmaker
    with an EC2 instance or Autoscale Group
*   join-domain-formula
    *   (Linux) Corrects tests that determine whether the instance is already
        joined to the domain

[251]: https://github.com/plus3it/watchmaker/pull/251

## 0.2.1

**Commit Delta**: [Change from 0.2.0 release](https://github.com/plus3it/watchmaker/compare/0.2.0...0.2.1)

**Released**: 2017.04.10

**Summary**:

*   ash-linux-formula
    *   Reduces spurious stderr output
    *   Removes notify script flagged by McAfee scans
*   splunkforwarder-formula
    *   (Windows) Clears system name entries from local Splunk config files

## 0.2.0

**Commit Delta**: [Change from 0.1.7 release](https://github.com/plus3it/watchmaker/compare/0.1.7...0.2.0)

**Released**: 2017.04.06

**Summary**:

*   [[Issue #238][238]] Captures all unhandled exceptions and logs them
*   [[Issue #234][234]] Stops the salt service prior to managing salt formulas,
    to ensure that the filesystem does not throw any errors about the files
    being locked
*   [[Issue #72][72]] Manages salt service so the service state after
    watchmaker completes is the same as it was prior to running watchmaker. If
    the service was running beforehand, it remains running afterwards. If the
    service was stopped (or non-existent) beforehad, the service remains
    stopped afterwards
*   [[Issue #163][163]] Modifies the `user_formulas` config option to support
    a map of `<formula_name>:<formula_url>`
*   [[PR #235][235]] Extracts salt content to the same target `srv` location
    for both Window and Linux. Previously, the salt content was extracted to
    different points in the filesystem hierarchy, which required different
    content for Windows and Linux. Now the same salt content archive can be
    used for both
*   [[PR #242][242]] Renames salt worker param `content_source` to
    `salt_content`
*   systemprep-formula
    *   Deprecated and removed. Replaced by new salt content structure that
        uses native salt capabilities to map states to a system
*   scc-formula
    *   Deprecated and removed. Replaced by scap-formula
*   scap-formula
    *   New bundled salt formula. Provides SCAP scans using either `openscap`
        or `scc`
*   pshelp-formula
    *   New bundled salt formula. Installs updated PowerShell help content to
        Windows systems

[242]: https://github.com/plus3it/watchmaker/pull/242
[235]: https://github.com/plus3it/watchmaker/pull/235
[163]: https://github.com/plus3it/watchmaker/issues/163
[72]: https://github.com/plus3it/watchmaker/issues/72
[234]: https://github.com/plus3it/watchmaker/issues/234
[238]: https://github.com/plus3it/watchmaker/issues/238

## 0.1.7

**Commit Delta**: [Change from 0.1.6 release](https://github.com/plus3it/watchmaker/compare/0.1.6...0.1.7)

**Released**: 2017.03.23

**Summary**:

*   Uses threads to stream stdout and stderr to the watchmaker log when
    executing a command via subproces
*   [[Issue #226][226]] Minimizes salt output of successful states, to
    make it easier to identify failed states
*   join-domain-formula
    *   (Linux) Exits with stateful failure on a bad decryption error
*   mcafee-agent-formula
    *   (Linux) Avoids attempting to diff a binary file
    *   (Linux) Installs `ed` as a dependency of the McAfee VSEL agent
*   scc-formula
    *   Retries scan up to 5 times if scc exits with an error

[226]: https://github.com/plus3it/watchmaker/issues/226

## 0.1.6

**Commit Delta**: [Change from 0.1.5 release](https://github.com/plus3it/watchmaker/compare/0.1.5...0.1.6)

**Released**: 2017.03.16

**Summary**:

*   ash-linux-formula
    *   Provides same baseline states for both EL6 and EL7

## 0.1.5

**Commit Delta**: [Change from 0.1.4 release](https://github.com/plus3it/watchmaker/compare/0.1.4...0.1.5)

**Released**: 2017.03.15

**Summary**:

*   ash-linux-formula
    *   Adds policies to disable insecure Ciphers and MACs in sshd_config
*   ash-windows-formula
    *   Adds `scm` and `stig` baselines for Windows 10
    *   Adds `scm` baseline for Windows Server 2016 (Alpha)
    *   Updates all `scm` and `stig` baselines with latest content
*   mcafee-agent-formula
    *   Uses firewalld on EL7 rather than iptables
*   scc-formula
    *   Skips verification of GPG key when install SCC RPM
*   splunkforwarder-formula
    *   Uses firewalld on EL7 rather than iptables

## 0.1.4

**Commit Delta**: [Change from 0.1.3 release](https://github.com/plus3it/watchmaker/compare/0.1.3...0.1.4)

**Released**: 2017.03.09

**Summary**:

*   [[Issue #180][180]] Fixes bug where file_roots did not contain formula paths

[180]: https://github.com/plus3it/watchmaker/issues/180

## 0.1.3

**Commit Delta**: [Change from 0.1.2 release](https://github.com/plus3it/watchmaker/compare/0.1.2...0.1.3)

**Released**: 2017.03.08

**Summary**:

*   [[Issue #164][164]] Aligns cli syntax for extra_arguments with other cli opts
*   [[Issue #165][165]] Removes ash_role from default config file
*   [[Issue #173][173]] Fixes exception when re-running watchmaker

[173]: https://github.com/plus3it/watchmaker/issues/173
[164]: https://github.com/plus3it/watchmaker/issues/164
[165]: https://github.com/plus3it/watchmaker/issues/165

## 0.1.2

**Commit Delta**: [Change from 0.1.1 release](https://github.com/plus3it/watchmaker/compare/0.1.1...0.1.2)

**Released**: 2017.03.07

**Summary**:

*   Adds a FAQ page to the docs
*   Moves salt formulas to the correct location on the local filesystem
*   join-domain-formula:
    *   (Linux) Modifies decryption routine for FIPS compliance
*   ash-linux-formula:
    *   Removes several error exits in favor of warnings
    *   (EL7-alpha) Various patches to improve support for EL7
*   dotnet4-formula:
    *   Adds support for .NET 4.6.2
    *   Adds support for Windows Server 2016
*   emet-formula:
    *   Adds support for EMET 5.52

## 0.1.1

**Commit Delta**: [Change from 0.1.0 release](https://github.com/plus3it/watchmaker/compare/0.1.0...0.1.1)

**Released**: 2017.02.28

**Summary**:

*   Adds more logging messages when downloading files

## 0.1.0

**Commit Delta**: N/A

**Released**: 2017.02.22

**Summary**:

*   Initial release!
