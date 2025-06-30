import fitz  # PyMuPDF
import os

books = ['denutra', 'dhumator', 'obeserone', 'salmonester', 'tuberkura', 'xsacker']

for book in books:
    pdf_path = f'main/static/pdf/{book}.pdf'
    output_dir = f'main/static/book_pages/{book}'
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found for {book}: {pdf_path}")
        continue

    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)

    print(f"📖 Exporting pages for: {book}")
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)
        output_path = os.path.join(output_dir, f'page{i+1}.jpg')
        pix.save(output_path)
        print(f"✅ Saved: {output_path}")
    
    print(f"🎉 Done: {book} has {len(doc)} pages\n")
