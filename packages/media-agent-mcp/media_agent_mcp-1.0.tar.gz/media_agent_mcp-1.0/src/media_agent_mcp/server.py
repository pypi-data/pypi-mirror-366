#!/usr/bin/env python3
"""Media Agent MCP Server - A Model Context Protocol server for media processing.

This server provides 9 tools for media processing:
1. TOS - Save content as URL
2. Video Concat - Concatenate two videos
3. Video Last Frame - Get the last frame from a video
4. Seedream - Creating images (AI model)
5. Seedance (lite & pro) - Creating videos (AI model)
6. Seededit - Maintain the main character (AI model)
7. Seed1.6 (VLM) - Do vision tasks in workflow (AI model)
8. Image Selector - Choose the best one from images
9. Video Selector - Choose the best video from videos
"""

import argparse
import logging
from typing import Optional, Dict, Any
import json
from dotenv import load_dotenv
import uvicorn

from mcp.server.fastmcp import FastMCP

# Import modules
from media_agent_mcp.storage import upload_to_tos
from media_agent_mcp.video import concat_videos, extract_last_frame
from media_agent_mcp.ai_models.seedream import generate_image
from media_agent_mcp.ai_models.seedance import generate_video
from media_agent_mcp.ai_models.seededit import seededit
from media_agent_mcp.media_selectors.image_selector import select_best_image
from media_agent_mcp.media_selectors.video_selector import select_best_video
from media_agent_mcp.task_manager import record_task_operation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server (will be configured in main function)
load_dotenv()
mcp = FastMCP("Media-Agent-MCP")


@mcp.tool()
def video_concat_tool(video_urls: list[str], task_id: Optional[str] = None) -> str:
    """
    Concatenate multiple videos from URLs and upload to TOS.
    
    Args:
        video_urls: List of video URLs to concatenate in order
        task_id: Optional task ID for tracking and data recording
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        # Record task operation if task_id provided
        if task_id:
            record_task_operation(task_id, "video_concat", f"Input URLs: {', '.join(video_urls)}")
        
        result = concat_videos(video_urls)
        
        # Record result if task_id provided
        if task_id and isinstance(result, dict) and result.get("status") == "success":
            record_task_operation(task_id, "video_concat", result.get("data"))
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"url": result},
                    "message": "Videos concatenated successfully"
                }
                # Record success result if task_id provided
                if task_id:
                    record_task_operation(task_id, "video_concat", success_result.get("data"))
                return json.dumps(success_result)
    except Exception as e:
        logger.error(f"Error in video_concat_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def video_last_frame_tool(video_url: str, task_id: Optional[str] = None) -> str:
    """
    Extract the last frame from a video file and upload to TOS.
    
    Args:
        video_url: URL or path to the video file
        task_id: Optional task ID for tracking and data recording
        
    Returns:
        JSON string with status, data, and message
    """
    try:
        # Record task operation if task_id provided
        if task_id:
            record_task_operation(task_id, "image_generated", f"Input URL: {video_url}")
        
        # Extract last frame and upload to TOS
        result = extract_last_frame(video_url)
        
        # Record result if task_id provided
        if task_id and isinstance(result, dict) and result.get("status") == "success":
            record_task_operation(task_id, "image_generated", result.get("data"))
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"url": result},
                    "message": "Last frame extracted successfully"
                }
                # Record success result if task_id provided
                if task_id:
                    record_task_operation(task_id, "image_generated", success_result.get("data"))
                return json.dumps(success_result)
            
    except Exception as e:
        logger.error(f"Error in video_last_frame_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def seedream_generate_image_tool(prompt: str, size: str = "1024x1024", task_id: Optional[str] = None) -> str:
    """
    Generate an image using Seedream AI model.
    
    Args:
        prompt: Text description of the image to generate
        size: Size of the image (e.g., "1024x1024")
        task_id: Optional task ID for tracking and data recording
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        # Record prompt generation if task_id provided
        if task_id:
            record_task_operation(task_id, "image_prompt", f"Prompt: {prompt}, Size: {size}")
        
        result = generate_image(prompt, size=size)
        
        # Record image generation result if task_id provided
        if task_id and isinstance(result, dict) and result.get("status") == "success":
            record_task_operation(task_id, "image_generated", result.get("data"))
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"image_url": result},
                    "message": "Image generated successfully"
                }
                # Record success result if task_id provided
                if task_id:
                    record_task_operation(task_id, "image_generated", success_result.get("data"))
                return json.dumps(success_result)
    except Exception as e:
        logger.error(f"Error in seedream_generate_image_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def seedance_generate_video_tool(prompt: str, first_frame_image: str, 
                                last_frame_image: str = None, duration: int = 5, 
                                resolution: str = "720p", task_id: Optional[str] = None) -> str:
    """
    Generate a video using Seedance AI model with first/last frame images.
    
    Args:
        prompt: Text description of the video to generate (optional for image-to-video)
        first_frame_image: URL or base64 of the first frame image
        last_frame_image: URL or base64 of the last frame image (optional)
        duration: Duration of the video in seconds (5 or 10)
        resolution: Video resolution (480p, 720p)
        task_id: Optional task ID for tracking and data recording
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        if not prompt and not first_frame_image:
            return json.dumps({
                "status": "error",
                "data": None,
                "message": "Error: Either prompt or first_frame_image must be provided"
            })
        
        # Record prompt generation if task_id provided
        if task_id:
            record_task_operation(task_id, "video_prompt", f"Prompt: {prompt}, Duration: {duration}s, Resolution: {resolution}")
        
        result = generate_video(
            prompt=prompt,
            first_frame_image=first_frame_image,
            last_frame_image=last_frame_image,
            duration=duration,
            resolution=resolution
        )
        
        # Record video generation result if task_id provided
        if task_id and isinstance(result, dict) and result.get("status") == "success":
            record_task_operation(task_id, "video_generation", result.get("data"))
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"url": result},
                    "message": "Video generated successfully"
                }
                # Record success result if task_id provided
                if task_id:
                    record_task_operation(task_id, "video_generation", success_result.get("data"))
                return json.dumps(success_result)
    except Exception as e:
        logger.error(f"Error in seedance_generate_video_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def seededit_tool(image_url: str, prompt: str, seed: int = -1, scale: float = 0.5, charactor_keep: bool = False, task_id: Optional[str] = None) -> str:
    """
    Edit a image using Seededit model.
    
    Args:
        image_url: Input image URL for editing
        prompt: Text prompt for image editing
        seed: Random seed for reproducibility (-1 for random)
        scale: Influence degree of text description (0-1)
        charactor_keep: whether to keep the main charactor in this image, if you wanna change the main charactor, please keep False
        task_id: Optional task ID for tracking and data recording
        
    Returns:
        JSON string with status, data, and message
    """
    try:
        # Record prompt generation if task_id provided
        if task_id:
            record_task_operation(task_id, "image_prompt", f"Prompt: {prompt}, Character keep: {charactor_keep}")
        
        result = seededit(
            image_url=image_url,
            prompt=prompt,
            charactor_keep=charactor_keep,
            return_url=True,
            scale=scale,
            seed=seed
        )
        
        # Record image generation result if task_id provided
        if task_id and isinstance(result, dict) and result.get("status") == "success":
            record_task_operation(task_id, "image_generated", result.get("data"))
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"image_url": result},
                    "message": "Image editing completed successfully"
                }
                # Record success result if task_id provided
                if task_id:
                    record_task_operation(task_id, "image_generated", success_result.get("data"))
                return json.dumps(success_result)
    except Exception as e:
        logger.error(f"Error in seededit_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })

@mcp.tool()
def vlm_vision_task_tool(messages: list, task_id: Optional[str] = None) -> str:
    """
    Perform vision-language tasks using VLM model.
    
    Args:
        messages: OpenAI-compatible messages format
        task_id: Optional task ID for tracking and data recording
        
    Returns:
        JSON string with status, data, and message
    """
    try:
        from media_agent_mcp.ai_models.seed16 import process_vlm_task
        
        # Record task operation if task_id provided
        if task_id:
            record_task_operation(task_id, "image_prompt", f"VLM task with {len(messages)} messages")
        
        result = process_vlm_task(messages)
        
        # Record result if task_id provided
        if task_id and isinstance(result, dict) and result.get("status") == "success":
            record_task_operation(task_id, "image_prompt", result.get("data"))
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"result": result},
                    "message": "Vision task completed successfully"
                }
                # Record success result if task_id provided
                if task_id:
                    record_task_operation(task_id, "image_prompt", success_result.get("data"))
                return json.dumps(success_result)
        
    except Exception as e:
        logger.error(f"Error in vlm_vision_task_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def image_selector_tool(image_paths: list[str], prompt: str, task_id: Optional[str] = None) -> str:
    """
    Select the best image from multiple options using VLM model.
    
    Args:
        image_paths: List of paths to image files
        prompt: Selection criteria prompt
        task_id: Optional task ID for tracking and data recording
        
    Returns:
        JSON string with status, data, and message
    """
    try:
        # Record task operation if task_id provided
        if task_id:
            record_task_operation(task_id, "image_prompt", f"Selecting from {len(image_paths)} images with prompt: {prompt}")
        
        result = select_best_image(image_paths, prompt)
        
        success_result = {
            "status": "success",
            "data": result,
            "message": "Image selection completed successfully"
        }
        
        # Record result if task_id provided
        if task_id:
            record_task_operation(task_id, "image_select", success_result.get("data"))
        
        return json.dumps(success_result)
    except Exception as e:
        error_result = {
            "status": "error",
            "data": None,
            "message": f"Image selection failed: {str(e)}"
        }
        
        # Record error if task_id provided
        if task_id:
            record_task_operation(task_id, "image_select", f"Error: {str(e)}")
        
        return json.dumps(error_result)


@mcp.tool()
def video_selector_tool(video_paths: list[str], prompt: str, task_id: Optional[str] = None) -> str:
    """
    Select the best video from multiple options using VLM model.
    
    Args:
        video_paths: List of paths to videos to choose from
        prompt: Selection criteria prompt
        task_id: Optional task ID for tracking and data recording
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        # Record task operation if task_id provided
        if task_id:
            record_task_operation(task_id, "video_prompt", f"Selecting from {len(video_paths)} videos with prompt: {prompt}")
        
        result = select_best_video(video_paths, prompt)
        
        success_result = {
            "status": "success",
            "data": result,
            "message": "Video selection completed successfully"
        }
        
        # Record result if task_id provided
        if task_id:
            record_task_operation(task_id, "video_select", success_result.get("data"))
        
        return json.dumps(success_result)
    except Exception as e:
        error_result = {
            "status": "error",
            "data": None,
            "message": f"Video selection failed: {str(e)}"
        }
        
        # Record error if task_id provided
        if task_id:
            record_task_operation(task_id, "video_select", f"Error: {str(e)}")
        
        return json.dumps(error_result)


@mcp.tool()
def tos_save_content_tool(content: str, file_extension: str = "txt", 
                         object_key: Optional[str] = None, task_id: Optional[str] = None) -> str:
    """
    Save content to TOS and return URL.
    
    Args:
        content: Content to save
        file_extension: File extension for the content (default: txt)
        object_key: Optional key to use for the object in TOS
        task_id: Optional task ID for tracking and data recording
        
    Returns:
        JSON string with status, data, and message
    """
    import tempfile
    import os
    
    try:
        # Record task operation if task_id provided
        if task_id:
            record_task_operation(task_id, "image_generated", f"Saving content ({len(content)} chars) as {file_extension}")
        
        # Create temporary file with content
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{file_extension}', delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Upload to TOS
            result = upload_to_tos(temp_file_path, object_key)
            
            # Record result if task_id provided
            if task_id and isinstance(result, dict) and result.get("status") == "success":
                record_task_operation(task_id, "image_generated", result.get("data"))
            
            return json.dumps(result)
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Error in tos_save_content_tool: {str(e)}")
        error_result = {
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        }
        
        # Record error if task_id provided
        if task_id:
            record_task_operation(task_id, "image_generated", f"Error: {str(e)}")
        
        return json.dumps(error_result)


def main():
    """Main entry point for the MCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Media Agent MCP Server')
    parser.add_argument('--transport', type=str, choices=['sse', 'stdio'], default='sse',
                        help='Transport method: sse or stdio (default: stdio)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host for SSE transport (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port for SSE transport (default: 8000)')

    parser.add_argument('--version', action='store_true',
                        help='Show version information')
    
    args = parser.parse_args()
    
    if args.version:
        print("Media Agent MCP Server v0.1.0")
        return
    
    logger.info("Starting Media Agent MCP Server...")
    logger.info(f"Transport: {args.transport}")
    if args.transport == 'sse':
        logger.info(f"SSE Server will run on {args.host}:{args.port}")
    
    logger.info("Available tools:")
    logger.info("  1. video_last_frame_tool - Extract last frame from video and upload to TOS")
    logger.info("  2. video_concat_tool - Concatenate two videos")
    logger.info("  3. seedream_generate_image_tool - Generate images with AI (direct URL return)")
    logger.info("  4. seedance_generate_video_tool - Generate videos with AI (async with polling)")
    logger.info("  5. seededit_maintain_character_tool - Edit images while maintaining character")
    logger.info("  6. vlm_vision_task_tool - Perform vision tasks with OpenAI-compatible messages")
    logger.info("  7. image_selector_tool - Select best image using VLM model")
    logger.info("  8. video_selector_tool - Select best video using VLM model")
    logger.info("  9. tos_save_content_tool - Save content to TOS and return URL")
    
    # Start the server with specified transport
    if args.transport == 'sse':
        logger.info(f"Starting SSE server on {args.host}:{args.port}")
        mcp.settings.host = args.host
        mcp.settings.port = args.port

        mcp.run(transport="sse")

    else:
        # Default stdio transport
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()