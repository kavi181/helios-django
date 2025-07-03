import os
import traceback
from main.utils.ml_captioning import describe_image
from main.utils.quiz_generation import generate_question_from_caption

# Image path
img_path = os.path.join("main", "static", "book_pages", "denutra", "page1.jpg")

# Step 1: Caption
caption = describe_image(img_path)
print("📝 Caption:", caption)

# Step 2: Quiz generation
if caption:
    try:
        question = generate_question_from_caption(caption)
        print("❓ Question:", question)
    except Exception as e:
        print("❌ Error while generating question:")
        traceback.print_exc()
else:
    print("❌ Caption generation failed.")
