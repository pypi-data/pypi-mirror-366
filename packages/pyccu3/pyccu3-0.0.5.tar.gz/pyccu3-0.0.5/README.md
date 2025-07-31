# PyCCU3

This project has two clients for the CCU2/3.
It is recommended to install the [xml-api external](https://github.com/homematic-community/XML-API) software into your ccu.
The current tested version is `2.3`.

You could also leverage the old xml-rpc client which is also available in this package.
It is not recommended using it as it does not have any encryption and passwords are transmitted in clear-text.

## XML-API

Supported endpoints

* `statelist.cgi`
* `devicelist.cgi`
* `version.cgi`
* `roomlist.cgi`
* `programlist.cgi`
* `functionlist.cgi`
