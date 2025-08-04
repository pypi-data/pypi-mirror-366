import cv2

def save_cropped_with_size_limit(image, output_path, max_kb=50):
    max_bytes = max_kb * 1024
    quality = 95  # Start with high quality

    # Try reducing quality until under limit
    while quality > 10:
        # Encode image to memory buffer
        result, encoded_img = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        if not result:
            raise Exception("Could not encode image")

        # Check size
        if len(encoded_img) <= max_bytes:
            # Write to file
            with open(output_path, 'wb') as f:
                f.write(encoded_img)
            return True

        quality -= 5  # Decrease quality and try again

    print(f"Could not compress image below {max_kb}KB")
    return False

def rotate_to_passport_orientation(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    # Step 1: Rotate 90° if image is landscape
    if image.shape[1] > image.shape[0]:
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # Step 2: Rotate 180° if face is in lower half
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    for (x, y, w, h) in faces:
        face_center_y = y + h // 2
        if face_center_y > image.shape[0] // 2:
            image = cv2.rotate(image, cv2.ROTATE_180)
        break  # Use the first face found

    return image

def draw_text_with_shadow(image, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.6, text_color=(220, 220, 220), shadow_color=(0, 0, 0), thickness=1):
    x, y = position

    # Draw black shadow (offset by 2px)
    cv2.putText(image, text, (x + 2, y + 2), font, font_scale, shadow_color, thickness + 2, cv2.LINE_AA)

    # Draw light text
    cv2.putText(image, text, (x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)