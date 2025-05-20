import base64
from io import BytesIO
from pdf2image import convert_from_path

def img_to_bytes(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def pdf_pages_to_base64(pdf_path, page_numbers, dpi=200, output_format="base64"):
    """
    Convert specific pages of a PDF to base64-encoded PNG images.

    Args:
        pdf_path (str): Path to the PDF file.
        page_numbers (list[int], optional): Page numbers to convert (0-indexed). If None, converts all.
        dpi (int): Resolution for image conversion.

    Returns:
        List[str]: List of base64-encoded PNG image strings.
    """

    # Adjust page numbers to 1-based indexing for pdf2image
    page_numbers = [int(x) + 1 for x in page_numbers]

    images = []
    for page in page_numbers:
        images.extend(convert_from_path(pdf_path, dpi=dpi, first_page=page, last_page=page))

    if output_format == "base64":
        return [
            base64.b64encode(img_to_bytes(img)).decode("utf-8")
            for img in images
        ]
    elif output_format == "PIL":
        return [image.convert("RGB") for image in images]
    else:
        raise ValueError(f"Unsupported output_format: {output_format}")
