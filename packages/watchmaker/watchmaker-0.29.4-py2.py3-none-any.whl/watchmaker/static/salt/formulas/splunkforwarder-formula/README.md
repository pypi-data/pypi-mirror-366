[![license](https://img.shields.io/github/license/plus3it/splunkforwarder-formula.svg)](./LICENSE)
[![Travis-CI Build Status](https://travis-ci.org/plus3it/splunkforwarder-formula.svg)](https://travis-ci.org/plus3it/splunkforwarder-formula)
[![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/github/plus3it/splunkforwarder-formula?branch=master&svg=true)](https://ci.appveyor.com/project/plus3it/splunkforwarder-formula)

# splunkforwarder-formula

Salt formula to install and configure the Splunk Universal Forwarder. This
formula supports both Windows and Linux.

On Windows, the formula depends on the Salt Windows Package Manager (`winrepo`),
and a `winrepo` package definition must be present for the Splunkforwarder.
Configuring `winrepo` is not handled by this formula.

## Available States

-   [splunkforwarder](#splunkforwarder)

### splunkforwarder

Install and configure the Splunk Universal Forwarder.

## Windows Configuration

This formula requires configuration via pillar. If the required parameters are
not configured in pillar, the formula will fail.

### (Windows) splunkforwarder:lookup:deploymentclient

This parameter is a map containing the `client_name` and `target_uri` keys.
`client_name` is a string that identifies the client environment to Splunk.
`target_uri` is the fqdn:port of the Splunk collector.

>**Required**: `True`

**Example**:

```yaml
splunkforwarder:
  lookup:
    deploymentclient:
      client_name: splunk-uf-windows-srv
      target_uri: 'hostname.domainname:9098'
```

### (Windows) splunkforwarder:lookup:log_local

This parameter is a map with a `contents` key that contains the contents of the
`log-local.cfg` file. The `log-local.cfg` contains information on what logs
will be forwarded to the Splunk collector.

>**Required**: `False`
>
>**Default**: _See example below_

**Example**:

```yaml
log_local:
  contents: |
      category.StatusMgr=WARN
      category.TcpOutputProc=WARN
      category.FilesystemChangeWatcher=ERROR
```

### (Windows) splunkforwarder:lookup:inputs

This parameter is a map with a `sections` key that contains sections of the
INI-formatted `inputs.conf` file. For syntax and INI sections options, see
<http://docs.splunk.com/Documentation/Splunk/latest/Admin/Inputsconf>.

>**Required**: `False`

**Example**:

```yaml
inputs:
  sections:
    'monitor://C:\path\to\app.log': {}
```


### (Windows) splunkforwarder:lookup:package

The `package` parameter is the name of the package as defined in the winrepo
package definition.

>**Required**: `False`
>
>**Default**: `splunkforwarder`

**Example**:

```yaml
splunkforwarder:
  lookup:
    package: splunkforwarder
```

### (Windows) splunkforwarder:lookup:service

The `service` parameter is the name of the Windows service for the Splunk
Universal Forwarder.

>**Required**: `False`
>
>**Default**: `SplunkForwarder`

**Example**:

```yaml
splunkforwarder:
  lookup:
    service: SplunkForwarder
```

## Linux Configuration

This formula requires configuration via pillar. If the required parameters are
not configured in pillar, the formula will fail.

### (Linux) splunkforwarder:lookup:package_url

This parameter is the URL to the RPM package for the Splunk Universal
Forwarder. The formula will use this RPM to install the splunkforwarder.

>**Required**: `True`

**Example**:

```yaml
splunkforwarder:
  lookup:
    package_url: https://path/to/my/splunkforwarder.rpm
```

### (Linux) splunkforwarder:lookup:deploymentclient

This parameter is a map containing the `client_name` and `target_uri` keys.
`client_name` is a string that identifies the client environment to Splunk.
`target_uri` is the fqdn:port of the Splunk collector.

>**Required**: `True`

**Example**:

```yaml
splunkforwarder:
  lookup:
    deploymentclient:
      client_name: splunk-uf-windows-srv
      target_uri: 'hostname.domainname:9098'
```

### (Linux) splunkforwarder:lookup:service_opts

This parameter is a string representing the options given when starting
the Splunk service.

>**Required**: `False`
>
>**Default**: `--accept-license`

**Example**:

```yaml
service_opts: --accept-license
```

### (Linux) splunkforwarder:lookup:log_local

This parameter is a map with a `contents` key that contains the contents of the
`log-local.cfg` file. The `log-local.cfg` contains information on what logs
will be forwarded to the Splunk collector.

>**Required**: `False`
>
>**Default**: _See example below_

**Example**:

```yaml
log_local:
  contents: |
      category.StatusMgr=WARN
      category.TcpOutputProc=WARN
      category.FilesystemChangeWatcher=ERROR
```

### (Linux) splunkforwarder:lookup:inputs

This parameter is a map with a `sections` key that contains sections of the
INI-formatted `inputs.conf` file. For syntax and INI sections options, see
<http://docs.splunk.com/Documentation/Splunk/latest/Admin/Inputsconf>.

>**Required**: `False`

**Example**:

```yaml
inputs:
  sections:
    'monitor:///path/to/app.log': {}
```

### (Linux) splunkforwarder:lookup:package

The `package` parameter is the name of the package as defined in the RPM
provided to the `package_url` parameter.

>**Required**: `False`
>
>**Default**: `splunkforwarder`

**Example**:

```yaml
splunkforwarder:
  lookup:
    package: 'splunkforwarder'
```

### (Linux) splunkforwarder:lookup:service

The `service` parameter is the name of the Linux service for the Splunk
Universal Forwarder.

>**Required**: `False`
>
>**Default**: `splunk`

**Example**:

```yaml
splunkforwarder:
  lookup:
    service: splunk
```

### (Linux) splunkforwarder:lookup:user

The `user` is an object of attributes that configure the user for the Splunk
Universal Forwarder.

>**Required**: `False`
>
>**Default**:
>
>```yaml
>user:
>  name: splunk
>  fullname: Splunk Server
>  home: /opt/splunkforwarder
>  shell: /bin/bash
>```

**Example**:

```yaml
splunkforwarder:
  lookup:
    user:
      name: splunk
      fullname: Splunk Server
      home: /opt/splunkforwarder
      shell: /bin/bash
```
