from PIL import Image, ExifTags
from PIL.ImageQt import ImageQt
from PyQt6.QtGui import QPixmap
import pathlib
from typing import Iterable


def pil2qt(img):
    qim = ImageQt(img)
    qpm = QPixmap.fromImage(qim)
    return qpm


def clip(x, x_min, x_max):
    if x < x_min:
        return x_min
    if x >= x_max:
        return x_max - 1
    return x


def get_image_fnames(
    directory: pathlib.Path | str, extensions: Iterable[str] = ("jpg", "jpeg"), case_sensitive: bool = False
):
    directory = pathlib.Path(directory)
    fnames: list[pathlib.Path] = []
    for ext in extensions:
        fnames.extend(directory.glob(f"*{ext}", case_sensitive=case_sensitive))
    return sorted(fnames)


def get_subimage(img: Image.Image, frac_pos, resolution):
    width, height = img.size
    width_out, height_out = resolution

    center_x, center_y = int(frac_pos[0] * width), int(frac_pos[1] * height)
    corner_x = clip(center_x - width_out // 2, 0, width - width_out)
    corner_y = clip(center_y - height_out // 2, 0, height - height_out)

    crop_box = (corner_x, corner_y, corner_x + width_out, corner_y + height_out)
    sub_img = img.crop(crop_box).copy()
    return sub_img


def load_image_with_exif(fname):
    img = Image.open(fname)
    img.load()
    try:
        # Get the EXIF data from the image
        exif = img._getexif()

        if exif is not None:
            # Find the orientation tag
            orientation_tag = None
            for tag, tag_value in ExifTags.TAGS.items():
                if tag_value == "Orientation":
                    orientation_tag = tag
                    break

            if orientation_tag and orientation_tag in exif:
                orientation = exif[orientation_tag]

                # Apply rotation based on EXIF orientation
                if orientation == 2:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    img = img.transpose(Image.ROTATE_180)
                elif orientation == 4:
                    img = img.transpose(Image.FLIP_TOP_BOTTOM)
                elif orientation == 5:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
                elif orientation == 6:
                    img = img.transpose(Image.ROTATE_270)
                elif orientation == 7:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
                elif orientation == 8:
                    img = img.transpose(Image.ROTATE_90)
    except (AttributeError, KeyError, IndexError):
        # Handle cases where EXIF data is not available or not formatted as expected
        pass
    return img


def resize_img_with_padding(img: Image.Image, target_res: tuple[int, int]):
    """
    Resize an image to target resolution while maintaining aspect ratio by adding black padding.

    Args:
        img: PIL Image object to resize
        target_res: Tuple of (width, height) for the target resolution

    Returns:
        PIL Image object resized to target_res with black padding if necessary
    """
    target_width, target_height = target_res

    # Get original aspect ratio
    orig_width, orig_height = img.size
    orig_aspect = orig_width / orig_height
    target_aspect = target_width / target_height

    new_img = Image.new("RGB", target_res, color="black")

    # Calculate dimensions to maintain aspect ratio
    if orig_aspect > target_aspect:
        # Original is wider, scale by width
        new_width = target_width
        new_height = int(new_width / orig_aspect)
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        # Center vertically
        y_offset = (target_height - new_height) // 2
        new_img.paste(resized_img, (0, y_offset))
    else:
        # Original is taller, scale by height
        new_height = target_height
        new_width = int(new_height * orig_aspect)
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        # Center horizontally
        x_offset = (target_width - new_width) // 2
        new_img.paste(resized_img, (x_offset, 0))

    return new_img
