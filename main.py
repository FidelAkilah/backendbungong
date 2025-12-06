import os
import random
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

app = FastAPI()

# --- KONFIGURASI CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SETUP OPENAI ---
client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY") 
)

@app.api_route("/api/bungong", methods=["GET", "POST"])
async def give_score():
    try:
        # 1. SCORE LOGIC (FIXED 15 ITEMS) -- UPDATED RANGE 5-7%
        # Mengubah range random menjadi 5 sampai 7
        scores_array = [random.randint(90, 100) for _ in range(15)]
        
        average_score = round(sum(scores_array) / 15, 1)

        # 2. FEEDBACK LOGIC (Random 5-7 items)
        feedback_num = random.randint(5, 7)
        
        # Sub Num mengikuti jumlah feedback
        sub_num_array = [random.randint(3, 15) for _ in range(feedback_num)]

        # 3. Prompt Engineering (Tari Lenggang Nyai)
        prompt_text = (
            f"Berikan {feedback_num} poin evaluasi teknis singkat (1-2 kalimat per poin) "
            "untuk penari Tari Lenggang Nyai (Betawi) berdasarkan deteksi pose tubuh (tanpa wajah). "
            "Setiap poin mewakili penilaian untuk satu segmen gerakan. "
            "Fokus pada: keluwesan pinggul, kewer tangan, kuda-kuda (mendak), dan power hentakan kaki. "
            "Output: Hanya daftar kalimat dipisahkan baris baru."
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "Kamu adalah juri tari Betawi yang memberikan catatan teknis per segmen gerakan."
                },
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7,
        )

        # 4. Parsing hasil OpenAI
        raw_content = response.choices[0].message.content.strip()
        
        feedback_list = []
        for line in raw_content.split('\n'):
            clean_line = line.strip()
            if clean_line:
                if clean_line[0].isdigit():
                    clean_line = clean_line.split('.', 1)[-1].strip()
                if clean_line.startswith('- '):
                    clean_line = clean_line[2:]
                feedback_list.append(clean_line)

        # 5. Sinkronisasi Data Feedback & Sub Num
        selected_feedback = feedback_list[:feedback_num]
        
        # Jaga-jaga jika AI generate feedback kurang dari request
        actual_len = len(selected_feedback)
        if actual_len < feedback_num:
            feedback_num = actual_len
            sub_num_array = sub_num_array[:actual_len] 

        return {
            "feedback_num": feedback_num,
            "feedback": selected_feedback,  # Array strings
            "sub_num": sub_num_array,       # Array int
            "score": scores_array,          # Array int (FIXED 15 ITEMS, Range 5-7)
            "average_score": average_score  # Float
        }

    except Exception as e:
        print(f"Error: {e}")
        # Fallback Logic
        fallback_feedback = [
            "Gerakan pinggul kurang lepas saat goyang.",
            "Posisi tangan kewer masih kaku di pergelangan.",
            "Kuda-kuda mendak perlu lebih rendah lagi.",
            "Koordinasi kaki terlambat dengan tempo musik.",
            "Bahu sering terangkat, harusnya rileks."
        ]
        
        # Fallback Score tetap 15, Range disesuaikan juga jadi 5-7
        fallback_scores = [random.randint(5, 7) for _ in range(15)]
        fallback_avg = round(sum(fallback_scores) / 15, 1)
        
        # Fallback Sub Num
        fallback_sub_num = [random.randint(3, 15) for _ in range(5)]

        return {
            "feedback_num": 5,
            "feedback": fallback_feedback,
            "sub_num": fallback_sub_num,
            "score": fallback_scores,
            "average_score": fallback_avg
        }

@app.get("/")
def read_root():
    return {"status": "API Updated: Score fixed to 15 items with range 5-7."}