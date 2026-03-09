import cv2

def analyze_image(image_path):

    img = cv2.imread(image_path)

    h, w, _ = img.shape

    description = f"Image with resolution {w}x{h}"

    return description
