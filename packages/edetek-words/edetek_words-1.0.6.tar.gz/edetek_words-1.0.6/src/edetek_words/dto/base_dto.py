# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/30/2025 3:25 PM
@Description: Description
@File: base_dto.py
"""
from dataclasses import fields, is_dataclass
from typing import Type, TypeVar, get_origin, get_args

T = TypeVar("T", bound="BaseDTO")


class BaseDTO:
    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        init_args = {}
        for f in fields(cls):
            value = data.get(f.name)
            if value is None:
                continue
            field_type = f.type
            origin = get_origin(field_type)
            if origin == list:
                item_type = get_args(field_type)[0]
                if is_dataclass(item_type):
                    value = [item_type.from_dict(item) for item in value]
            elif is_dataclass(field_type) and isinstance(value, dict):
                value = field_type.from_dict(value)
            init_args[f.name] = value
        return cls(**init_args)
