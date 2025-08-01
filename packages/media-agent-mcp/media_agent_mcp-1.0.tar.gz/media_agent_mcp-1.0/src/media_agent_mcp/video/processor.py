"""Video processing module.

This module provides video processing functionality including concatenation and frame extraction.
"""

import asyncio
import json
import logging
import os
import tempfile
import time
import uuid
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import cv2
import requests
from moviepy import VideoFileClip, concatenate_videoclips

from media_agent_mcp.storage.tos_client import upload_to_tos

logger = logging.getLogger(__name__)


def download_video_from_url(url: str) -> Dict[str, Any]:
    """Download video from URL to a temporary file.
    
    Args:
        url: URL of the video to download
        
    Returns:
        JSON response with status, data (file path), and message
    """
    try:
        # Parse URL to get file extension
        parsed_url = urlparse(url)
        file_extension = os.path.splitext(parsed_url.path)[1] or '.mp4'
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_path = temp_file.name
        temp_file.close()
        
        # Download the video
        logger.info(f"Downloading video from {url}...")
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        logger.info(f"Video downloaded to {temp_path}")
        return {
            "status": "success",
            "data": {"file_path": temp_path},
            "message": "Video downloaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Error downloading video from {url}: {e}")
        return {
            "status": "error",
            "data": None,
            "message": f"Error downloading video from {url}: {e}"
        }


def concat_videos(video_urls: list, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Concatenate multiple videos into one.
    
    Args:
        video_urls: List of URLs or paths to video files to concatenate in order
        output_path: Optional output path for the concatenated video
    
    Returns:
        JSON response with status, data (TOS URL), and message
    """
    temp_files = []
    video_captures = []
    
    try:
        if not video_urls or len(video_urls) == 0:
            return {
                "status": "error",
                "data": None,
                "message": "No video URLs provided"
            }
            
        if not output_path:
            output_path = f"concatenated_{int(time.time())}.mp4"
        
        # Download videos if they are URLs and prepare local paths
        video_paths = []
        for video_input in video_urls:
            if video_input.startswith(('http://', 'https://')):
                download_result = download_video_from_url(video_input)
                if download_result["status"] == "error":
                    return download_result
                video_path = download_result["data"]["file_path"]
                temp_files.append(video_path)
                video_paths.append(video_path)
            elif os.path.exists(video_input):
                video_paths.append(video_input)
            else:
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Video file {video_input} not found"
                }
        
        # Use moviepy to concatenate videos
        logger.info("Concatenating videos with moviepy...")
        clips = [VideoFileClip(vp) for vp in video_paths]
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", bitrate="8000k")

        # Close the clips
        for clip in clips:
            clip.close()
        
        logger.info(f"Videos concatenated successfully: {output_path}")
        
        # Upload concatenated video to TOS
        try:
            tos_url = upload_to_tos(output_path)
            logger.info(f"Video uploaded to TOS: {tos_url}")
            
            # Clean up local concatenated file
            try:
                os.unlink(output_path)
                logger.info(f"Cleaned up local concatenated file: {output_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up local file {output_path}: {e}")
            
            return {
                "status": "success",
                "data": {"tos_url": tos_url},
                "message": "Videos concatenated and uploaded successfully"
            }
        except Exception as e:
            logger.error(f"Error uploading to TOS: {e}")
            return {
                "status": "error",
                "data": None,
                "message": f"Error uploading to TOS: {str(e)}"
            }
        
    except Exception as e:
        logger.error(f"Error concatenating videos: {e}")
        return {
            "status": "error",
            "data": None,
            "message": f"Error concatenating videos: {str(e)}"
        }
    finally:
        # Release any remaining video captures
        for cap in video_captures:
            if cap.isOpened():
                cap.release()
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    logger.info(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file}: {e}")


def extract_last_frame(video_input: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Extract the last frame from a video as an image and upload to TOS.
    
    Args:
        video_input: URL or path to the video file
        output_path: Optional output path for the extracted frame
    
    Returns:
        JSON response with status, data (TOS URL), and message
    """
    temp_video_file = None
    
    try:
        # Handle URL or local file path
        if video_input.startswith(('http://', 'https://')):
            # Download video from URL
            download_result = download_video_from_url(video_input)
            if download_result["status"] == "error":
                return download_result
            video_path = download_result["data"]["file_path"]
            temp_video_file = video_path
        elif os.path.exists(video_input):
            video_path = video_input
        else:
            return {
                "status": "error",
                "data": None,
                "message": f"Video file {video_input} not found"
            }
        
        if not output_path:
            output_path = f"last_frame_{uuid.uuid4().hex}.jpg"
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {
                "status": "error",
                "data": None,
                "message": f"Could not open video {video_path}"
            }
        
        # Get total number of frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames <= 0:
            cap.release()
            return {
                "status": "error",
                "data": None,
                "message": "Video has no frames"
            }
        
        # Set position to last frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
        
        # Read the last frame
        ret, frame = cap.read()
        
        if ret:
            # Save the frame
            cv2.imwrite(output_path, frame)
            cap.release()
            logger.info(f"Last frame extracted: {output_path}")
            
            # Upload frame to TOS
            try:
                tos_url = upload_to_tos(output_path)
                logger.info(f"Frame uploaded to TOS: {tos_url}")
                
                # Clean up local frame file
                try:
                    os.unlink(output_path)
                    logger.info(f"Cleaned up local frame file: {output_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up local file {output_path}: {e}")
                
                return {
                    "status": "success",
                    "data": {"tos_url": tos_url},
                    "message": "Last frame extracted and uploaded successfully"
                }
            except Exception as e:
                logger.error(f"Error uploading frame to TOS: {e}")
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Error uploading to TOS: {str(e)}"
                }
        else:
            cap.release()
            return {
                "status": "error",
                "data": None,
                "message": "Could not read the last frame"
            }
            
    except Exception as e:
        logger.error(f"Error extracting last frame: {e}")
        return {
            "status": "error",
            "data": None,
            "message": f"Error extracting last frame: {str(e)}"
        }
    finally:
        # Clean up temporary video file if downloaded
        if temp_video_file and os.path.exists(temp_video_file):
            try:
                os.unlink(temp_video_file)
                logger.info(f"Cleaned up temporary video file: {temp_video_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary video file {temp_video_file}: {e}")


if __name__ == '__main__':
    # Example usage
    video_urls = [
        "https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205870921200000000000000000000ffffc0a85094bda733.mp4",
        "https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205817458400000000000000000000ffffc0a850948120ae.mp4"
    ]

    concatenated_video = concat_videos(video_urls)
    print(f"Concatenated video URL: {concatenated_video}")

    last_frame_url = extract_last_frame(video_urls[0])
    print(f"Last frame URL: {last_frame_url}")