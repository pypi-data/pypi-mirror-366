# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/30/2025 3:22 PM
@Description: Description
@File: translation_package.py
"""

from dataclasses import dataclass
from typing import List, Optional

from edetek_words.dto.base_dto import BaseDTO


@dataclass
class ContentItem(BaseDTO):
    text: str
    needAI: bool
    translateText: str = None


@dataclass
class SourceDoc(BaseDTO):
    name: str
    path: str
    dstPath: str


@dataclass
class TranslationPackage(BaseDTO):
    language: str
    contents: List[ContentItem]
    sourceDoc: SourceDoc

    def find_content_item_by_name(self, name: str) -> Optional[ContentItem]:
        if not self.contents:
            raise Exception("The contents list is empty or None.")
        for content in self.contents:
            if content.text == name:
                return content
        # raise Exception(f"ContentItem with text '{name}' not found in contents.")
        return None
