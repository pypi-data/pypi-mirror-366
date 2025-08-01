import io
import logging
import os
import zipfile
from pathlib import Path

from PIL import Image

logger = logging.getLogger("root")


def create_output_folder(organization_name: str) -> str:
    """Create output folder for the organization."""
    output_folder = os.path.join("output", organization_name)
    os.makedirs(output_folder, exist_ok=True)
    return output_folder


def get_output_folder(organization_name: str) -> str:
    """Get output folder for the organization."""
    output_folder = os.path.join("output", organization_name)
    return output_folder


def compress_img(image_path: str):
    """Compress image using pillow."""

    try:
        abs_image_path = os.path.abspath(image_path)
        img = Image.open(abs_image_path)
        img = img.convert("RGB")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        optimized = Image.open(buffer)
        output_path_webp = f"{os.path.splitext(abs_image_path)[0]}.webp"
        optimized.save(output_path_webp, "WEBP", lossless=True, quality=100)
        output_path_png = f"{os.path.splitext(abs_image_path)[0]}.png"
        im = Image.open(output_path_webp).convert("RGB")
        im.save(output_path_png, "png")
        logger.info(f"Image compressed successfully: {output_path_png}")
        os.remove(output_path_webp)
        return output_path_png

    except Exception as e:
        logger.error(f"Error compressing image: {e}")
        return image_path


def compress_output_files(organization_name: str):
    """Compress HTML, CSV, and JSON output files into a zip archive."""
    output_folder = Path(get_output_folder(organization_name))
    zip_filename = os.path.join(output_folder, f"{organization_name}_report.zip".replace(" ", "_"))

    total_size = 0
    compressed_size = 0

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in output_folder.rglob("*"):
            if file_path.suffix in (".html", ".csv", ".json", ".docx", ".pdf"):
                arcname = file_path.relative_to(output_folder)
                zipf.write(file_path, arcname)

                total_size += file_path.stat().st_size
                compressed_info = zipf.getinfo(str(arcname))
                compressed_size += compressed_info.compress_size

                logger.debug(f"Added {arcname} to zip (Original: {file_path.stat().st_size} bytes, Compressed: {compressed_info.compress_size} bytes)")

    compression_ratio = (1 - compressed_size / total_size) * 100 if total_size > 0 else 0
    logger.info(f"Compressed output created: {zip_filename}")
    logger.info(f"Total size: {total_size} bytes, Compressed size: {compressed_size} bytes")
    logger.info(f"Compression ratio: {compression_ratio:.2f}%")

    return zip_filename


def perform_cleanup(output_folder: str, namespaces: list[str]):
    """Perform cleanup by removing the temporary files in output folder."""
    resume_file = os.path.join(output_folder, ".resume")
    if os.path.exists(resume_file):
        os.remove(resume_file)
    for namespace in namespaces:
        namespace_folder = os.path.join(output_folder, namespace)
        if os.path.exists(namespace_folder):
            for file_path in os.listdir(namespace_folder):
                os.remove(os.path.join(namespace_folder, file_path))
            os.rmdir(namespace_folder)
    logger.info("Cleanup completed.")
