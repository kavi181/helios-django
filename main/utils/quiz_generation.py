# main/utils/quiz_generation.py

from transformers import pipeline

# Load Flan-T5 once
qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

def generate_question_from_caption(caption):
    prompt = (
        "Create a multiple choice question with 4 options based on this comic description:\n\n"
        f"{caption}\n\n"
        "Format:\nQuestion?\nA. ...\nB. ...\nC. ...\nD. ...\nAnswer: ..."
    )
    try:
        result = qa_pipeline(prompt, max_length=256, do_sample=True, temperature=0.9)
        return result[0]['generated_text']
    except Exception as e:
        print("❌ Question generation failed:", e)
        return ""
