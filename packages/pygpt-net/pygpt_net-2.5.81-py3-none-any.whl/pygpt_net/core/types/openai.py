#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.07.30 00:00:00                  #
# ================================================== #

OPENAI_DISABLE_TOOLS = [
    "o1-mini",
    "o1-preview"
    "o4-mini-deep-research",
    "o3-deep-research",
]
OPENAI_REMOTE_TOOL_DISABLE_IMAGE = [
    "o4-mini-deep-research",
    "o3-deep-research",
    "codex-mini-latest",
]
OPENAI_REMOTE_TOOL_DISABLE_CODE_INTERPRETER = [
    "codex-mini-latest",
]
OPENAI_REMOTE_TOOL_DISABLE_WEB_SEARCH = [
    "codex-mini-latest",
]
OPENAI_REMOTE_TOOL_DISABLE_COMPUTER_USE = [
    "o4-mini-deep-research",
    "o3-deep-research",
    "codex-mini-latest",
]
OPENAI_REMOTE_TOOL_DISABLE_FILE_SEARCH = [
    "codex-mini-latest",
]
OPENAI_REMOTE_TOOL_DISABLE_MCP = [
    "codex-mini-latest",
]