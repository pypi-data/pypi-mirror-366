[![license](https://img.shields.io/github/license/plus3it/trellix-agent-formula.svg)](./LICENSE)
[![Travis-CI Build Status](https://travis-ci.org/plus3it/trellix-agent-formula.svg)](https://travis-ci.org/plus3it/trellix-agent-formula)
[![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/github/plus3it/trellix-agent-formula?branch=master&svg=true)](https://ci.appveyor.com/project/plus3it/trellix-agent-formula)

# trellix-agent-formula

This salt formula will install Trellix Agent, for use with a Trellix ePolicy
Orchestrator (ePO) server. The formula supports both Linux and Windows.

On Windows, the formula depends on the Salt Windows Package Manager (`winrepo`),
and a `winrepo` package definition must be present for the Trellix Agent.
Configuring `winrepo` is not handled by this formula.

The formula currently supports no configuration of the Trellix Agent itself; it
is assumed all configuration is handled by the ePO server. However, the formula
does use pillar to define the name of the trellix package, and the version to
install.

## Available States

-   [trellix-agent](#trellix-agent)

### trellix-agent

Installs the Trellix Agent.

## Windows Configuration

This formula supports configuration via pillar for the name of the winrepo
package and the version of the package to install. All settings must be
located within the `trellix-agent:lookup` pillar dictionary.

### `trellix-agent:lookup:package`

The `package` parameter is the name of the package as defined in the winrepo
package definition.

>**Required**: `False`
>
>**Default**: `trellix-agent`

**Example**:

```yaml
trellix-agent:
  lookup:
    package: trellix-agent
```

### `trellix-agent:lookup:version`

The `version` parameter is the version of the package as defined in the
winrepo package definition.

>**Required**: `False`
>
>**Default**: `''`

**Example**:

```yaml
trellix-agent:
  lookup:
    version: '4.8.2003'
```

## Linux Configuration

The only _required_ configuration setting for Linux systems is the source URL
to the Trellix Agent installer. There are a few other optional settings
described below, as well. All settings must be located within the
`trellix-agent:lookup` pillar dictionary.

### `trellix-agent:lookup:source`

The `source` parameter is the URL to the Trellix Agent installer.

>**Required**: `True`
>
>**Default**: `None`

**Example**:

```yaml
trellix-agent:
  lookup:
    source: https://S3BUCKET.F.Q.D.N/trellix/linux/trellix-agent/dev/install.sh
```

### `trellix-agent:lookup:source_hash`

The `source_hash` parameter is the URL to hash of the Trellix Agent installer.

>**Required**: `True`
>
>**Default**: `None`

**Example**:

```yaml
trellix-agent:
  lookup:
    source_hash: https://S3BUCKET.F.Q.D.N/trellix/linux/trellix-agent/dev/install.sh.SHA512
```

### `trellix-agent:lookup:keystore_directory`

The `keystore_directory` parameter is the directory where Trellix SSL keyfiles
are stored on the system.

>**Required**: `False`
>
>**Default**: `/opt/Trellix/cma/scratch/keystore`

**Example**:

```yaml
trellix-agent:
  lookup:
    keystore_directory: /opt/Trellix/cma/scratch/keystore
```

### `trellix-agent:lookup:key_files`

The `key_files` parameter is a list of key files to look for, in the
`keystore_directory`. If any of these files are found, the formula assumes the
Trellix Agent is already installed and the install is skipped.

>**Required**: `False`
>
>**Default**: _See example below_

**Example**:

```yaml
trellix-agent:
  lookup:
    key_files:
      - agentprvkey.bin
      - agentpubkey.bin
      - serverpubkey.bin
      - serverreqseckey.bin
```

### `trellix-agent:lookup:rpms`

The `rpms` parameter is a list of RPMs to look for. If any of these packages
are already installed, the formula skips the installation of the Trellix Agent.

>**Required**: `False`
>
>**Default**: _See example below_

**Example**:

```yaml
trellix-agent:
  lookup:
    rpms:
      - MFEcma
      - MFErt
```

### `trellix-agent:lookup:client_in_ports`

The `client_in_ports` parameter is a list of ports to enable inbound for remote
management of the Trellix Agent.

>**Required**: `False`
>
>**Default**: _See example below_

**Example**:

```yaml
trellix-agent:
  lookup:
    client_in_ports:
      - 8591
```

### `trellix-agent:lookup:client_in_sources`

The `client_in_sources` parameter is a list of CIDRs to enable inbound for remote
management of the Trellix Agent.

>**Required**: `False`
>
>**Default**: _See example below_

**Example**:

```yaml
trellix-agent:
  lookup:
    client_in_sources:
      - 0.0.0.0/0
```
