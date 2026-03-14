from src.extractor import ContractExtractor
ext = ContractExtractor('Red_Team_NDA_Pack.pdf')
text = ext.extract_text()

with open('pdf_content.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved to pdf_content.txt")
print("\n" + "="*70)
print("FULL NDA TEXT:")
print("="*70)
print(text)
