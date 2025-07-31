"""
Stamp it - Add full-screen watermark to images
Support text watermark and image watermark
"""

import os
import io
import requests
import uuid
import boto3
import os
from typing import Optional, Union, Tuple
from pathlib import Path
from fastmcp import FastMCP
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import math

# Create FastMCP instance
mcp = FastMCP("Stamp it - Add full-screen watermark to images")

# Supported image formats
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

# Cache font instances for better performance
_font_cache = {}

class WatermarkConfig:
    """Watermark configuration"""
    DEFAULT_FONT_SIZE = 36
    DEFAULT_ANGLE = 30
    SPACING_X_FACTOR = 1.1
    SPACING_Y_FACTOR = 0.9
    BRIGHTNESS_THRESHOLDS = {
        'very_bright': 180,
        'medium': 120,
        'dark': 60
    }

def is_valid_image_format(filename: str) -> bool:
    """Check if the file is in supported image format"""
    return Path(filename).suffix.lower() in SUPPORTED_FORMATS

# def get_filename_from_path(file_path: str) -> str:
#     """Get filename from file path"""
#     return os.path.basename(file_path)

def read_local_image(file_path: str) -> Optional[bytes]:
    """Read local image file"""
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except (IOError, OSError) as e:
        print(f"Failed to read local image: {e}")
        return None

def is_local_file(path: str) -> bool:
    """Check if path is a local file"""
    return os.path.isfile(path)

def is_url(path: str) -> bool:
    """Check if path is a URL"""
    return path.startswith(('http://', 'https://'))

def download_image(url: str) -> Optional[bytes]:
    """Download image from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check for 403 error
        if response.status_code == 403:
            raise PermissionError(f"403 Forbidden: Cannot access URL {url}")
            
        response.raise_for_status()
        
        # Check if content is image
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type:
            raise ValueError(f"URL content is not image: {content_type}")
            
        return response.content
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to download image: {e}")
        return None

def calculate_average_brightness(image: Image.Image) -> float:
    """Calculate average brightness of image"""
    # Convert to grayscale for brightness calculation
    if image.mode != 'L':
        gray_image = image.convert('L')
    else:
        gray_image = image
    
    # Downscale image for faster calculation
    small_image = gray_image.resize((50, 50))
    pixels = list(small_image.getdata())
    return sum(pixels) / len(pixels)

def get_adaptive_watermark_color(average_brightness: float) -> Tuple[int, int, int, int]:
    """Automatically select watermark color based on image brightness"""
    if average_brightness > WatermarkConfig.BRIGHTNESS_THRESHOLDS['very_bright']:
        # Very bright image: use dark watermark
        return (20, 20, 20, 160)
    elif average_brightness > WatermarkConfig.BRIGHTNESS_THRESHOLDS['medium']:
        # Medium brightness: use medium-dark watermark
        return (32, 32, 32, 150)
    elif average_brightness > WatermarkConfig.BRIGHTNESS_THRESHOLDS['dark']:
        # Dark image: use light watermark
        return (200, 200, 200, 140)
    else:
        # Very dark image: use white watermark
        return (240, 240, 240, 130)

def get_font(font_size: int = WatermarkConfig.DEFAULT_FONT_SIZE) -> ImageFont.FreeTypeFont:
    """Get font with caching support"""
    if font_size in _font_cache:
        return _font_cache[font_size]
    
    # Font path priority list
    font_paths = [
        # macOS Chinese fonts
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        # Linux fonts
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        # Windows fonts
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "arial.ttf",
    ]
    
    font = None
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except (IOError, OSError):
            continue
    
    # Fallback to default font if all attempts failed
    if font is None:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()
    
    _font_cache[font_size] = font
    return font

def create_text_watermark_layer(
    size: Tuple[int, int], 
    text: str, 
    color: Tuple[int, int, int, int],
    angle: float = WatermarkConfig.DEFAULT_ANGLE,
    font_size: int = WatermarkConfig.DEFAULT_FONT_SIZE
) -> Image.Image:
    """Create text watermark layer"""
    width, height = size
    watermark_layer = Image.new('RGBA', size, (255, 255, 255, 0))
    
    font = get_font(font_size)
    
    # Get text dimensions
    draw = ImageDraw.Draw(watermark_layer)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Calculate watermark spacing
    diagonal_size = math.sqrt(text_width**2 + text_height**2)
    spacing_x = int(diagonal_size * WatermarkConfig.SPACING_X_FACTOR)
    spacing_y = int(diagonal_size * WatermarkConfig.SPACING_Y_FACTOR)
    
    # Calculate grid size
    cols = math.ceil(width / spacing_x) + 3
    rows = math.ceil(height / spacing_y) + 3
    
    # Start offset to ensure full coverage
    start_offset_y = -spacing_y // 2
    start_offset_x = -spacing_x // 2
    
    # Add rotated text watermark
    for row in range(rows):
        for col in range(cols):
            x = start_offset_x + col * spacing_x - (row % 2) * (spacing_x // 2)
            y = start_offset_y + row * spacing_y
            
            # Create temporary canvas for high-quality rotation
            temp_size = max(text_width + 40, text_height + 40)
            temp_img = Image.new('RGBA', (temp_size, temp_size), (255, 255, 255, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # Center the text
            text_x = (temp_size - text_width) // 2
            text_y = (temp_size - text_height) // 2
            temp_draw.text((text_x, text_y), text, font=font, fill=color)
            
            # High-quality rotation
            rotated_text = temp_img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
            
            # Paste to watermark layer
            if x < width and y < height:
                watermark_layer.paste(rotated_text, (x, y), rotated_text)
    
    return watermark_layer

def create_image_watermark_layer(
    size: Tuple[int, int],
    watermark_image_path: Union[str, io.BytesIO],
    opacity: float = 0.5,
    scale: float = 0.15,
    angle: float = WatermarkConfig.DEFAULT_ANGLE
) -> Optional[Image.Image]:
    """Create image watermark layer"""
    try:
        # Read watermark image (can be path or BytesIO)
        watermark_img = Image.open(watermark_image_path)
        
        # Convert to RGBA mode
        if watermark_img.mode != 'RGBA':
            watermark_img = watermark_img.convert('RGBA')
        
        # Calculate scaled dimensions
        width, height = size
        max_size = min(width, height) * scale
        
        # Maintain aspect ratio while scaling
        w_ratio = max_size / watermark_img.width
        h_ratio = max_size / watermark_img.height
        scale_ratio = min(w_ratio, h_ratio)
        
        new_width = int(watermark_img.width * scale_ratio)
        new_height = int(watermark_img.height * scale_ratio)
        
        # Resize watermark image
        watermark_img = watermark_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Adjust transparency
        enhancer = ImageEnhance.Brightness(watermark_img)
        watermark_img = enhancer.enhance(1.0)
        
        # Create watermark layer
        watermark_layer = Image.new('RGBA', size, (255, 255, 255, 0))
        
        # Calculate tiling spacing
        spacing_x = int(new_width * 1.5)
        spacing_y = int(new_height * 1.5)
        
        # Calculate grid
        cols = math.ceil(width / spacing_x) + 2
        rows = math.ceil(height / spacing_y) + 2
        
        # Starting offset
        start_offset_x = -spacing_x // 2
        start_offset_y = -spacing_y // 2
        
        # Tile watermark images
        for row in range(rows):
            for col in range(cols):
                x = start_offset_x + col * spacing_x - (row % 2) * (spacing_x // 2)
                y = start_offset_y + row * spacing_y
                
                # Rotate watermark image
                if angle != 0:
                    rotated_watermark = watermark_img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
                else:
                    rotated_watermark = watermark_img
                
                # Adjust transparency
                alpha = rotated_watermark.split()[-1]
                alpha = alpha.point(lambda p: int(p * opacity))
                rotated_watermark.putalpha(alpha)
                
                # Paste to watermark layer
                if x < width and y < height:
                    watermark_layer.paste(rotated_watermark, (x, y), rotated_watermark)
        
        return watermark_layer
        
    except Exception as e:
        print(f"Error: Failed to process image: {e}")
        return None

def apply_watermark_to_image(
    image: Image.Image, 
    watermark_text: Optional[str] = None,
    watermark_image_path: Optional[str] = None,
    angle: float = WatermarkConfig.DEFAULT_ANGLE
) -> Image.Image:
    """Add watermark (text or image) to the image"""
    # Record original mode to preserve image properties
    original_mode = image.mode
    
    # Convert to RGBA for processing
    if original_mode != 'RGBA':
        image_rgba = image.convert('RGBA')
    else:
        image_rgba = image.copy()
    
    watermark_layer = None
    
    if watermark_text:
        # Text watermark
        avg_brightness = calculate_average_brightness(image)
        watermark_color = get_adaptive_watermark_color(avg_brightness)
        watermark_layer = create_text_watermark_layer(
            image.size, watermark_text, watermark_color, angle
        )
    elif watermark_image_path:
        # Image watermark
        watermark_layer = create_image_watermark_layer(
            image.size, watermark_image_path, opacity=0.6, angle=angle
        )
    
    if watermark_layer:
        # Merge watermark
        watermarked = Image.alpha_composite(image_rgba, watermark_layer)
        
        # Restore original mode
        if original_mode == 'RGB':
            watermarked = watermarked.convert('RGB')
        elif original_mode == 'L':
            watermarked = watermarked.convert('L')
        elif original_mode == 'P':
            watermarked = watermarked.convert('P')
        
        return watermarked
    
    return image

def save_watermarked_image(image: Image.Image, ext: str, output_dir: str = ".") -> str:
    """Save watermarked image to local and upload to S3"""
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Generate UUID filename
    new_filename = f"{uuid.uuid4()}"
    output_path = os.path.join(output_dir, new_filename)
    
    # Handle image format based on extension
    if ext.lower() in ['jpg', 'jpeg']:
        # JPEG doesn't support transparency, convert to RGB
        if image.mode == 'RGBA':
            bg = Image.new('RGB', image.size, (255, 255, 255))
            bg.paste(image, mask=image.split()[-1])
            image = bg
        image.save(output_path, 'JPEG', quality=95, optimize=True)
    else:
        image.save(output_path, quality=95, optimize=True)
    
    # Upload to S3
    s3_url = upload_to_s3(output_path)
    os.remove(output_path)  # Remove local temp file
    
    return s3_url

def upload_to_s3(file_path: str) -> str:
    """Upload file to S3 bucket"""
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    bucket_name = 'netmind-public-files'
    object_name = os.path.basename(file_path)
    
    try:
        s3.upload_file(
            file_path,
            bucket_name,
            object_name
        )
        return f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
    except Exception as e:
        raise Exception(f"Failed to upload to S3: {str(e)}")

@mcp.tool()
def add_text_watermark(image_url: str, watermark_text: str, angle: float = 30) -> str:
    """
    Add text watermark to image
    
    Args:
        image_url: Local file path or URL of the image
        watermark_text: Watermark text content
        angle: Watermark angle (default 30 degrees)
        
    Returns:
        Path information of processed image
    """
    return _process_watermark(image_url, watermark_text=watermark_text, angle=angle)

@mcp.tool()
def add_image_watermark(image_url: str, watermark_image_url: str, angle: float = 30) -> str:
    """
    Add image watermark to image
    
    Args:
        image_url: Local file path or URL of the image
        watermark_image_url: URL or path to watermark image
        angle: Watermark angle (default 30 degrees)
        
    Returns:
        Path information of processed image
    """
    if not is_valid_image_format(watermark_image_url):
        return f"Error: Unsupported watermark image format. Supported formats: {', '.join(SUPPORTED_FORMATS)}"
    
    return _process_watermark(image_url, watermark_image_path=watermark_image_url, angle=angle)

def _process_watermark(
    image_url: str, 
    watermark_text: Optional[str] = None,
    watermark_image_path: Optional[Union[str, io.BytesIO]] = None,
    angle: float = 30
) -> str:
    """
    Common function for processing watermark
    
    Args:
        image_url: URL or path to main image
        watermark_text: Text for text watermark (optional)
        watermark_image_path: URL or path to watermark image (optional)
        angle: Rotation angle for watermark
        
    Returns:
        str: Result message with output URL or error
    """
    # Handle URL or local file for main image
    if is_url(image_url):
        image_data = download_image(image_url)
    else:
        # Check if local file exists
        if not is_local_file(image_url):
            return f"Error: File not found or inaccessible: {image_url}"
        image_data = read_local_image(image_url)
        
    if not image_data:
        return "Error: Failed to read main image file"
        
    # Handle watermark image if provided
    watermark_image = None
    if watermark_image_path:
        if is_url(watermark_image_path):
            watermark_data = download_image(watermark_image_path)
            if not watermark_data:
                return "Error: Failed to download watermark image"
            watermark_image = io.BytesIO(watermark_data)
        elif is_local_file(watermark_image_path):
            watermark_image = watermark_image_path
        else:
            return f"Error: Watermark image not found: {watermark_image_path}"
    
    try:
        # Open image
        image = Image.open(io.BytesIO(image_data))
        
        # Add watermark
        watermarked_image = apply_watermark_to_image(
            image, 
            watermark_text=watermark_text,
            watermark_image_path=watermark_image,
            angle=angle
        )
        
        output_dir = "/tmp"
        
        # Save watermarked image
        output_path = save_watermarked_image(watermarked_image, image.format, output_dir)
        
        watermark_type = "text" if watermark_text else "image"
        return f"Success! {watermark_type} watermark added, image saved to: {output_path}"
        
    except Exception as e:
        return f"Error: Failed to process image: {str(e)}"

def main():
    mcp.run()

if __name__ == "__main__":
    main()
