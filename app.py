import re
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import whisper

app = FastAPI(title="AGLE Auto-Transcription Engine")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Whisper model (uses 'base' by default; change to 'small' or 'medium' for higher accuracy)
model = whisper.load_model("base")

class GuidelineEngine:
    @staticmethod
    def apply_rules(text: str, is_verbatim: bool = False) -> str:
        # 1. Clean up fillers if NOT verbatim (per General Guidelines)
        if not is_verbatim:
            fillers = r'\b(um|uh|like|you know|mhmm|ah|er)\b'
            text = re.sub(fillers, '', text, flags=re.IGNORECASE)
            text = re.sub(r'\s+', ' ', text).strip()

        # 2. Convert numbers 0-9 to words unless formatting rules dictate otherwise
        num_map = {
            ' 0 ': ' zero ', ' 1 ': ' one ', ' 2 ': ' two ', ' 3 ': ' three ',
            ' 4 ': ' four ', ' 5 ': ' five ', ' 6 ': ' six ', ' 7 ': ' seven ',
            ' 8 ': ' eight ', ' 9 ': ' nine '
        }
        for num, word in num_map.items():
            text = re.sub(rf'\b{num.strip()}\b', word.strip(), text)

        # 3. Currency symbol formatting ($15, €27, £189)
        text = re.sub(r'\b(\d+)\s*(dollars|usd|\$)', r'$\1', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(\d+)\s*(euros|eur|€)', r'€\1', text, flags=re.IGNORECASE)

        # 4. Capitalization of sentences
        sentences = text.split('. ')
        sentences = [s.strip().capitalize() for s in sentences if s]
        text = '. '.join(sentences)

        return text

class TaskPayload(BaseModel):
    task_id: str
    audio_path: str
    is_verbatim: bool = False

@app.post("/api/process-task")
async def process_task(payload: TaskPayload):
    try:
        result = model.transcribe(payload.audio_path)
        raw_text = result.get("text", "")
        formatted_text = GuidelineEngine.apply_rules(raw_text, payload.is_verbatim)
        final_output = f"[00:00:00] Speaker 1: {formatted_text}"

        return {
            "status": "success",
            "task_id": payload.task_id,
            "raw_text": raw_text,
            "formatted_transcript": final_output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/start-bot")
async def start_bot_service():
    return {"status": "started", "message": "Automation worker triggered successfully."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
