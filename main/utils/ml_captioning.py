# main/utils/ml_captioning.py

from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Load BLIP model once
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def describe_image(img_path):
    try:
        image = Image.open(img_path).convert('RGB')
        inputs = processor(images=image, return_tensors="pt")
        output = model.generate(**inputs)
        caption = processor.decode(output[0], skip_special_tokens=True)
        return caption
    except Exception as e:
        print(f"⚠️ Failed to process image {img_path}: {e}")
        return ""
