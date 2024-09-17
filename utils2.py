import re
from difflib import SequenceMatcher

# Fungsi untuk menghapus tanda-tanda waqof dan tanda ayat sajdah
def normalize_text(text):
    waqof_signs = ["ۖ", "ۗ", "ۚ", "ۛ", "ۜ", "۩", "ْ"]
    for sign in waqof_signs:
        text = text.replace(sign, "")
    # Menghapus spasi kosong yang berlebihan
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Fungsi untuk mengecek apakah karakter adalah harakat
def is_harakat(char):
    harakats = "ًٌٍَُِّْ"
    return char in harakats

def compare_texts(original, transcription, accuracy_threshold=70):
    original_normalized = normalize_text(original)
    transcription_normalized = normalize_text(transcription)
    
    matcher = SequenceMatcher(None, original_normalized, transcription_normalized)
    differences = []
    
    # Menghitung akurasi terlebih dahulu
    correct_chars = sum(len(original_normalized[i1:i2]) for tag, i1, i2, j1, j2 in matcher.get_opcodes() if tag == 'equal')
    total_chars = len(original_normalized)
    accuracy = (correct_chars / total_chars) * 100
    error_rate = 100 - accuracy  # Persentase kesalahan adalah kebalikan dari akurasi

    # Jika akurasi di bawah threshold, tambahkan kesalahan 'Ayat yang dibaca berbeda' dan hentikan proses
    if accuracy < accuracy_threshold:
        differences.append({
            'type': 'Ayat yang dibaca berbeda',
            'original': original_normalized,
            'transcription': transcription_normalized
        })
    else:
        # Logika untuk perbedaan dan jenis kesalahan hanya dijalankan jika akurasi cukup tinggi
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                error_type = 'Unknown'
                if tag == 'replace':
                    if len(original_normalized[i1:i2]) == len(transcription_normalized[j1:j2]):
                        # Check if the replacement is harakat or letter
                        if all(is_harakat(c) for c in original_normalized[i1:i2] + transcription_normalized[j1:j2]):
                            error_type = 'Kesalahan Harakat'
                        else:
                            error_type = 'Kesalahan Huruf'
                    else:
                        error_type = 'Kesalahan Huruf'
                elif tag == 'delete':
                    error_type = 'Huruf yang Hilang'
                elif tag == 'insert':
                    error_type = 'Huruf Tambahan'

                differences.append({
                    'type': error_type,
                    'original': original_normalized[i1:i2],
                    'transcription': transcription_normalized[j1:j2]
                })

    return differences, accuracy, error_rate
