#!/usr/bin/env python3
"""Async Media Agent MCP Server - A Model Context Protocol server for media processing with async support.

This server provides 9 async tools for media processing using threading:
1. TOS - Save content as URL
2. Video Concat - Concatenate two videos
3. Video Last Frame - Get the last frame from a video
4. Seedream - Creating images (AI model)
5. Seedance (lite & pro) - Creating videos (AI model)
6. Seededit - Maintain the main character (AI model)
7. Seed1.6 (VLM) - Do vision tasks in workflow (AI model)
8. Image Selector - Choose the best one from images
9. Video Selector - Choose the best video from videos

All tools are wrapped with threading to provide async functionality without modifying original functions.
"""

import argparse
import asyncio
import logging
from typing import List, Optional
import json
from dotenv import load_dotenv
import uvicorn
from functools import wraps

def async_retry(max_retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    result = await func(*args, **kwargs)
                    if isinstance(result, dict) and result.get('status') == 'error':
                        logger.warning(f"Attempt {attempt + 1} of {max_retries} failed for {func.__name__}. Error: {result.get('message')}. Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        continue
                    return result
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} of {max_retries} failed for {func.__name__} with exception: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
            logger.error(f"Function {func.__name__} failed after {max_retries} retries.")
            return {"status": "error", "data": None, "message": f"Function {func.__name__} failed after {max_retries} retries."}
        return wrapper
    return decorator

from mcp.server.fastmcp import FastMCP

# Import async wrappers
from media_agent_mcp.async_wrapper import (
    async_video_concat_tool, async_video_last_frame_tool, 
    async_seedream_generate_image_tool, async_seedance_generate_video_tool, 
    async_seededit_tool, async_vlm_vision_task_tool, 
    async_image_selector_tool, async_video_selector_tool, 
    async_tos_save_content_tool, cleanup_executor,
    async_openaiedit_tool
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server (will be configured in main function)
load_dotenv()
mcp = FastMCP("Media-Agent-MCP-Async")


@mcp.tool()
@async_retry()
async def video_concat_tool(video_urls: List[str]) -> dict:
    """
    Asynchronously concatenate multiple videos from URLs and upload to TOS.
    
    Args:
        video_urls: List of video URLs to concatenate
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_video_concat_tool(video_urls)
    return result


@mcp.tool()
@async_retry()
async def video_last_frame_tool(video_url: str) -> dict:
    """
    Asynchronously extract the last frame from a video file and upload to TOS.
    
    Args:
        video_url: URL of the video file
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_video_last_frame_tool(video_url)
    return result


@mcp.tool()
@async_retry()
async def seedream_generate_image_tool(prompt: str, size: str = "1024x1024") -> dict:
    """
    Asynchronously generate an image using Seedream AI model.
    
    Args:
        prompt: Text description of the image to generate
        size: Size of the image (e.g., "1024x1024")
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_seedream_generate_image_tool(prompt, size)
    return result


@mcp.tool()
@async_retry()
async def seedance_generate_video_tool(prompt: str, first_frame_image: str, 
                                            last_frame_image: str = None, duration: int = 5, 
                                            resolution: str = "720p") -> dict:
    """
    Asynchronously generate a video using Seedance AI model with first/last frame images.
    
    Args:
        prompt: Text description of the video to generate (optional for image-to-video)
        first_frame_image: URL or base64 of the first frame image
        last_frame_image: URL or base64 of the last frame image (optional)
        duration: Duration of the video in seconds (5 or 10)
        resolution: Video resolution (480p, 720p)
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_seedance_generate_video_tool(prompt, first_frame_image, last_frame_image, duration, resolution)
    return result


@mcp.tool()
@async_retry()
async def seededit_tool(image_url: str, prompt: str, charactor_keep: bool = False) -> dict:
    """
    Asynchronously edit an image using the OpenAI Images API.
    
    Args:
        image_url: Input image URL for editing
        prompt: Text prompt for image editing
        charactor_keep: Whether to keep character consistency
        
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_seededit_tool(image_url, prompt, charactor_keep)
    return result


@async_retry()
async def openaiedit_tool(image_url: str, prompt: str, size: str = "1024x1024") -> dict:
    """
    Asynchronously edit an image using the OpenAI Images API.
    
    Args:
        image_url: Input image URL for editing
        prompt: Text prompt for image editing
        size: The size of the generated images. Must be one of "256x256", "512x512", or "1024x1024".
        
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_openaiedit_tool(image_url, prompt, size)
    return result


@async_retry()
async def vlm_vision_task_tool(messages: List) -> dict:
    """
    Asynchronously perform vision-language tasks using VLM model.
    
    Args:
        messages: OpenAI-compatible messages format
        
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_vlm_vision_task_tool(messages)
    return result


@mcp.tool()
@async_retry()
async def image_selector_tool(image_paths: List[str], prompt: str) -> dict:
    """
    Asynchronously select the best image from multiple options using VLM model.
    
    Args:
        image_paths: List of paths to image files
        prompt: Selection criteria prompt
        
    Returns:
        Dictionary with status, data, and message
    """
    try:
        result = await async_image_selector_tool(image_paths, prompt)
    except Exception as e:
        logger.error(f"Error in image_selector_tool: {str(e)}")
        result = {"status": "error", "data": None, "message": str(e)}
    
    return result


@mcp.tool()
@async_retry()
async def video_selector_tool(video_paths: List[str], prompt: str) -> dict:
    """
    Asynchronously select the best video from multiple options using VLM model.
    
    Args:
        video_paths: List of paths to videos to choose from
        prompt: Selection criteria prompt
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_video_selector_tool(video_paths, prompt)
    return result


@async_retry()
async def tos_save_content_tool(content: str, file_extension: str = "txt", 
                                     object_key: Optional[str] = None) -> dict:
    """
    Asynchronously save content to TOS and return URL.
    
    Args:
        content: Content to save
        file_extension: File extension for the content (default: txt)
        object_key: Optional key to use for the object in TOS
        
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_tos_save_content_tool(content, file_extension, object_key)
    return result


# Utility function for concurrent execution
async def run_multiple_tools_concurrently(*coroutines):
    """
    Run multiple async tools concurrently.
    
    Args:
        *coroutines: Variable number of coroutines to run concurrently
        
    Returns:
        List of results from all coroutines
    """
    return await asyncio.gather(*coroutines, return_exceptions=True)


def main():
    """Main entry point for the Async MCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Async Media Agent MCP Server')
    parser.add_argument('--transport', type=str, choices=['sse', 'stdio'], default='stdio',
                        help='Transport method: sse or stdio (default: stdio)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host for SSE transport (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port for SSE transport (default: 8000)')
    parser.add_argument('--version', action='store_true',
                        help='Show version information')
    
    args = parser.parse_args()
    
    if args.version:
        print("Async Media Agent MCP Server v0.1.0")
        return
    
    logger.info("Starting Async Media Agent MCP Server...")
    logger.info(f"Transport: {args.transport}")
    if args.transport == 'sse':
        logger.info(f"SSE Server will run on {args.host}:{args.port}")
    
    logger.info("Available async tools:")
    logger.info("  1. video_last_frame_tool_async - Extract last frame from video and upload to TOS")
    logger.info("  2. video_concat_tool_async - Concatenate two videos")
    logger.info("  3. seedream_generate_image_tool_async - Generate images with AI (async)")
    logger.info("  4. seedance_generate_video_tool_async - Generate videos with AI (async)")
    logger.info("  5. seededit_tool_async - Edit images while maintaining character (async)")
    logger.info("  6. vlm_vision_task_tool_async - Perform vision tasks with OpenAI-compatible messages (async)")
    logger.info("  7. image_selector_tool_async - Select best image using VLM model (async)")
    logger.info("  8. video_selector_tool_async - Select best video using VLM model (async)")
    logger.info("")
    logger.info("All tools support concurrent execution using asyncio.gather() or run_multiple_tools_concurrently()")
    
    try:
        # Start the server with specified transport
        if args.transport == 'sse':
            logger.info(f"Starting async SSE server on {args.host}:{args.port}")
            mcp.settings.host = args.host
            mcp.settings.port = args.port
            mcp.run(transport="sse")
        else:
            # Default stdio transport
            mcp.run(transport="stdio")
    finally:
        # Clean up thread pool executor on shutdown
        logger.info("Cleaning up thread pool executor...")
        cleanup_executor()


if __name__ == "__main__":
    main()