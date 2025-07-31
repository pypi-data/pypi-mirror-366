from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Any, Dict, Optional, Union

import dacite

from pyccu3.enums import (
    BOOLEAN,
    AESState,
    DataPointType,
    DataPointUnit,
    Direction,
    FirmwareUpdateState,
    RFInterface,
    RxMode,
    XMLDirection,
)
from pyccu3.types import PartyDate


@dataclass
class Base:
    @staticmethod
    def manipulate_keys(
        data: Union[list, dict, str, bool, int],
        lowercase: Optional[bool] = None,
        is_key: bool = True,
    ):
        match data:
            case dict():
                return {
                    Base.manipulate_keys(
                        key, lowercase=lowercase, is_key=True
                    ): Base.manipulate_keys(value, lowercase=lowercase, is_key=False)
                    for key, value in data.items()
                }
            case str() if is_key:
                match lowercase:
                    case None:
                        return data
                    case True:
                        return data.lower()
                    case False:
                        return data.upper()
            case _:
                return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        raise NotImplementedError("from_dict needs implementation")

    @staticmethod
    def to_serializable(value) -> Union[int, str]:
        match value:
            case Enum():
                return Base.to_serializable(value.value)
            case IPv4Address() | IPv6Address() | PartyDate() | str():
                return str(value)
            case bool():
                return bool(value)
            case int():
                return int(value)
            case _:
                return value

    @staticmethod
    def to_complex_serializable(data) -> Union[list, dict, int, str]:
        match data:
            case list() | set():
                return [Base.to_complex_serializable(item) for item in data]
            case dict():
                return {
                    Base.to_serializable(key): Base.to_complex_serializable(val)
                    for key, val in data.items()
                }
            case _:
                return Base.to_serializable(data)

    @staticmethod
    def dict_factory(data) -> dict[Union[str, int], Union[list, dict, int, bool, str]]:
        return {
            Base.to_serializable(field): Base.to_complex_serializable(value)
            for field, value in data
        }

    def as_dict(self):
        raise NotImplementedError("as_dict needs implementation")

    def __json__(self):
        return self.as_dict()


@dataclass
class XMLAPIBaseSerializer(Base):
    @staticmethod
    def floatify(value):
        match value:
            case "" | 0 | 0.0:
                return float(0.0)
        return float(value)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return dacite.from_dict(
            data_class=cls,
            data=Base.manipulate_keys(data, lowercase=None),
            config=dacite.Config(
                cast=[
                    RFInterface,
                    DataPointType,
                    DataPointUnit,
                    XMLDirection,
                    FirmwareUpdateState,
                    IPv4Address,
                    IPv6Address,
                    PartyDate,
                    bool,
                    int,
                ],
                check_types=True,
                strict=True,
                strict_unions_match=True,
                type_hooks={
                    float: XMLAPIBaseSerializer.floatify,
                    BOOLEAN: BOOLEAN,
                    IPv4Address: ip_address,
                    IPv6Address: ip_address,
                },
            ),
        )

    def as_dict(self):
        return BaseSerializer.manipulate_keys(
            asdict(self, dict_factory=BaseSerializer.dict_factory), lowercase=None
        )


@dataclass
class BaseSerializer(Base):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return dacite.from_dict(
            data_class=cls,
            data=Base.manipulate_keys(data, lowercase=True),
            config=dacite.Config(
                cast=[
                    int,
                    bool,
                    AESState,
                    RxMode,
                    Direction,
                    RFInterface,
                    FirmwareUpdateState,
                ],
                check_types=True,
                strict=True,
                strict_unions_match=True,
            ),
        )

    def as_dict(self):
        return BaseSerializer.manipulate_keys(
            asdict(self, dict_factory=BaseSerializer.dict_factory), lowercase=False
        )
