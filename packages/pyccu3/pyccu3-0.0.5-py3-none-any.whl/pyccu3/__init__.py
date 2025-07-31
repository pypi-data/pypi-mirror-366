import importlib.metadata
import json
import re
import xmlrpc.client
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin

import json_fix as _  # type: ignore # noqa: F401
import requests
import urllib3
import xmltodict

from pyccu3.constants import ALLOWED_PARAMSET_DESCRIPTION_TYPES, ALLOWED_PARAMSET_TYPES
from pyccu3.objects.legacy import HomeMaticRPCDevice
from pyccu3.objects.xml_api import (
    HomeMaticDeviceList,
    HomeMaticFunctionList,
    HomeMaticProgramList,
    HomeMaticRoomList,
    HomeMaticStateList,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


try:
    # This will read version from pyproject.toml
    __version__ = importlib.metadata.version(__name__)
except Exception:
    __version__ = "develop"


class PyCCU3:
    def __init__(self, host: str, session_id: str, verify: bool = True) -> None:
        self.url = f"https://{host}/addons/xmlapi/"
        self.session_id = session_id
        self.verify = verify
        self.session = self._init_session()

    def _init_session(self):
        session = requests.Session()
        session.params["sid"] = self.session_id
        session.verify = self.verify
        return session

    def __enter__(self):
        self.session = self._init_session()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        del self.session

    def path(self, path):
        """
        builds up the complete URL

        Args:
            :path (str): Ressource extension
            :path (list): list of separated Ressource extensions

        Returns:
            :url (str): '<self.url/path>'
        """

        return urljoin(self.url, path)

    def get(
        self,
        path: str,
        params: Optional[Dict[str, str]] = None,
        default: Union[dict, list] = [],
    ):
        response = self.session.get(self.path(path), params=params)
        if response.status_code != 200:
            return default
        return xmltodict.parse(
            response.content,
            force_list=("datapoint", "channel", "deviceType", "form", "room"),
            attr_prefix="",
        )

    def statelist(
        self,
        ise_id: Optional[int] = None,
        show_internal: bool = False,
        show_remote: bool = False,
    ):
        params = {
            **({"ise_id": str(ise_id)} if ise_id else {}),
            **({"show_internal": "1"} if show_internal else {}),
            **({"show_remote": "1"} if show_remote else {}),
        }
        return HomeMaticStateList.from_dict(self.get("statelist.cgi", params=params))

    def roomlist(self):
        return HomeMaticRoomList.from_dict(self.get("roomlist.cgi"))

    def devicelist(
        self,
        device_id: Optional[int] = None,
        show_internal: bool = False,
        show_remote: bool = False,
    ) -> HomeMaticDeviceList:
        params = {
            **({"device_id": str(device_id)} if device_id else {}),
            **({"show_internal": "1"} if show_internal else {}),
            **({"show_remote": "1"} if show_remote else {}),
        }
        return HomeMaticDeviceList.from_dict(self.get("devicelist.cgi", params=params))

    def programlist(self) -> HomeMaticProgramList:
        return HomeMaticProgramList.from_dict(self.get("programlist.cgi"))

    def functionlist(self) -> HomeMaticFunctionList:
        return HomeMaticFunctionList.from_dict(self.get("functionlist.cgi"))

    @property
    def api_version(self):
        return self.get("version.cgi").get("version", "unknown")


class PyCCU3Legacy:
    scripting_regex = re.compile(r"<xml><exec>\/scriptkiddy\.exe<\/exec>.*?<\/xml>")

    def __init__(
        self,
        host: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 2010,
    ):
        self.auth = None
        self.host = host
        self.url = f"http://{host}:{port}"
        self.script_url = f"http://{host}:8181/scriptkiddy.exe"
        if username and password:
            self.auth = (username, password)
            self.url = f"http://{self.auth[0]}:{self.auth[1]}@{host}:{port}"
            self.script_url = (
                f"http://{self.auth[0]}:{self.auth[1]}@{host}:8181/scriptkiddy.exe"
            )
        self.proxy = self._create_proxy()

    def _create_proxy(self):
        transport = xmlrpc.client.Transport()
        connection = transport.make_connection(self.host)
        connection.timeout = 5
        return xmlrpc.client.ServerProxy(self.url, transport=transport)

    def __enter__(self):
        self.proxy = self._create_proxy()
        return self

    def _script_executor(self, script: str, jsonify=False):
        response = requests.post(self.script_url, auth=self.auth, data=script)
        if response.status_code != 200:
            return []
        if not jsonify:
            return response.text
        output = self.scripting_regex.sub("", response.text, 1)
        return json.loads(output)

    def __exit__(self, exception_type, exception_value, exception_traceback):
        del self.proxy

    @property
    def devices(self) -> List[HomeMaticRPCDevice]:
        return [
            HomeMaticRPCDevice.from_dict(entry) for entry in self.proxy.listDevices()
        ]

    def paramset_description(self, address: str, paramset_type: str):
        """
        paramset_type: ['MASTER', 'VALUES', 'SERVICE', 'LINK']
        """
        assert (
            paramset_type in ALLOWED_PARAMSET_DESCRIPTION_TYPES
        ), f"{paramset_type} not in {ALLOWED_PARAMSET_DESCRIPTION_TYPES}"
        return self.proxy.getParamsetDescription(address, paramset_type)

    def paramset(self, address: str, paramset_type: str):
        """
        paramset_type: ['MASTER', 'VALUES']
        """
        assert (
            paramset_type in ALLOWED_PARAMSET_TYPES
        ), f"{paramset_type} not in {ALLOWED_PARAMSET_TYPES}"
        return self.proxy.getParamset(address, paramset_type)

    def device_description(self, address: str):
        return self.proxy.getDeviceDescription(address)

    def device_names(self):
        script = """
            string id;
            Write("[");
            var first = true;
            foreach(id, root.Devices().EnumIDs()) {
                var device=dom.GetObject(id);
                if (device.ReadyConfig()==true && device.Name()!='Gateway') {
                    if (! first) {
                        Write(",")
                    }
                    if (first) {
                        first = false;
                    }
                    Write("{\\\"type\\\": \\\"device\\\", \\\"address\\\": \\\"" # device.Address() # "\\\" ,\\\"name\\\": \\\"" # device.Name() # "\\\" ,\\\"id\\\": " # id # "}");
                    if (device.Type()==OT_DEVICE) {
                        string channelId;
                        foreach(channelId, device.Channels()) {
                            var channel=dom.GetObject(channelId);
                            Write(",{\\\"type\\\": \\\"channel\\\", \\\"address\\\": \\\"" # channel.Address() # "\\\" ,\\\"name\\\": \\\"" # channel.Name() # "\\\" ,\\\"id\\\": " # channelId # "}");
                        }
                    }
                }
            }
            Write("]")
            """
        return self._script_executor(script, jsonify=True)
