splunkforwarder:

  lookup:

    ##############################################################
    # LINUX: Required parameters for the splunkforwarder-formula
    # Uncomment and set the required parameters, or the formula
    # will fail.
    ##############################################################

    # package_url is the URL to the splunkforwarder RPM.
    package_url: https://path/to/my/splunkforwarder.rpm

    # deploymentclient.conf contains the information necessary for connecting
    # to the splunk server.
    # client_name is an identifier for the client system or environment
    # target_uri is is the fqdn:port of the splunk collector
    deploymentclient:
      client_name: splunk-uf-linux-srv
      target_uri: 'hostname.domainname:9098'

    ##############################################################
    # LINUX: Optional parameters for the splunkforwarder-formula
    ##############################################################

    # log-local.cfg contains information on what logs will be forwarded to the
    # splunk server.
    #log_local:
      #contents: |
          #category.StatusMgr=WARN
          #category.TcpOutputProc=WARN
          #category.FilesystemChangeWatcher=ERROR

    # list of ports to open outbound for splunk communication
    #client_out_ports:
    #  - 8089
    #  - 9997

    # `package` is the name of the package installed by the splunkforwarder
    # RPM
    #package: splunkforwarder

    # `service` is the name of the splunkforwarder service
    #service: splunk
