# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/28/2025 2:11 PM
@Description: Description
@File: run_extractor.py
"""
from pathlib import Path
from typing import List

from edetek_words.common.docx_utils import accept_all_revisions
from edetek_words.common.json_utils import save_json
from edetek_words.common.path import docs_path
from edetek_words.core.prepare import prepare_translation
from edetek_words.core.word_extractor import WordExtractor
from edetek_words.dto.segment_dto import SegmentDTO

if __name__ == '__main__':
    work_dir = Path(r"D:\melen\docs\Temp-own\20250728_translate\workdir")
    filename = "CRN04894-13_GC Dosing Diary_v3.0_Final Draft.docx"
    # filename = "CRN04894-13_Menstrual Cycle Diary_V1.0_final draft.docx"
    target_language = "ja_JP"
    target_language_name = "Japanese"
    src_path, dst_path = prepare_translation(work_dir, filename, target_language_name)
    accept_all_revisions(dst_path)
    segment_dtos: List[SegmentDTO] = WordExtractor(dst_path).extract()
    save_json(str(docs_path("raw_text.json")), [segment_dto.original_text for segment_dto in segment_dtos],
              ensure_ascii=False)
