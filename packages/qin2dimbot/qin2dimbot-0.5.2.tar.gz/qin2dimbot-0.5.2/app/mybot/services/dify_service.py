# -*- coding: utf-8 -*-
"""
@Time    : 2025/7/12 10:00
@Author  : QIN2DIM
@GitHub  : https://github.com/QIN2DIM
@Desc    : Service for interacting with Dify LLM workflows.
"""
import json
from contextlib import suppress
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, List, Optional

from loguru import logger

from dify.workflow_tool import run_blocking_dify_workflow, run_streaming_dify_workflow
from settings import settings


async def invoke_model_blocking(
    bot_username: str,
    message_context: str,
    from_user: str,
    photo_paths: Optional[List[Path]],
    **kwargs,
) -> str:
    if settings.ENABLE_DEV_MODE:
        return settings.DEV_MODE_MOCKED_TEMPLATE

    """调用 Dify 并以阻塞方式获取结果。"""
    result = await run_blocking_dify_workflow(
        bot_username=bot_username,
        message_context=message_context,
        from_user=from_user,
        with_files=photo_paths,
        **kwargs,
    )
    result_text = result.data.outputs.answer

    with suppress(Exception):
        if settings.ENABLE_TEST_MODE:
            outputs_json = json.dumps(
                result.data.outputs.model_dump(mode="json"), indent=2, ensure_ascii=False
            )
            logger.debug(f"LLM Result: \n{outputs_json}")

    return result_text


async def invoke_model_streaming(
    bot_username: str,
    message_context: str,
    from_user: str,
    photo_paths: Optional[List[Path]],
    **kwargs,
) -> AsyncGenerator[Dict[str, Any], None]:
    """以流式方式调用 Dify 并返回事件块。"""
    streaming_generator = await run_streaming_dify_workflow(
        bot_username=bot_username,
        message_context=message_context,
        from_user=from_user,
        with_files=photo_paths,
        **kwargs,
    )
    async for chunk in streaming_generator:
        yield chunk
