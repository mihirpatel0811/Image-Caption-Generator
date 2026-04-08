import os
import json
from google import genai
from google.genai import types
from PIL import Image

PLATFORM_CONFIGS = {
    "general": {
        "name": "General",
        "prompt_extra": "",
        "style": "versatile, balanced tone, moderate hashtags",
    },
    "instagram": {
        "name": "Instagram",
        "prompt_extra": (
            "For 'social', craft an Instagram-style caption: conversational, "
            "emoji-rich, with 15-20 trending and niche hashtags placed at the end. "
            "Keep it under 2200 characters. Use line breaks for readability. "
            "Include a call-to-action (e.g., 'Double tap if you agree!', 'Tag someone who needs to see this')."
        ),
        "style": "visual-first, emoji-rich, hashtag-heavy, CTA-driven",
    },
    "linkedin": {
        "name": "LinkedIn",
        "prompt_extra": (
            "For 'social', craft a LinkedIn-style caption: professional, insightful, "
            "story-driven. Use 3-5 relevant professional hashtags at the end. "
            "Keep it between 150-300 words. Start with a hook line. "
            "Include a professional takeaway or thought-provoking question."
        ),
        "style": "professional, thought-leadership, storytelling",
    },
    "facebook": {
        "name": "Facebook",
        "prompt_extra": (
            "For 'social', craft a Facebook-style caption: warm, conversational, "
            "and community-oriented. Keep it between 100-250 characters for best engagement. "
            "Use 1-3 relevant hashtags sparingly. Ask a question to drive comments."
        ),
        "style": "conversational, community-driven, question-based",
    },
    "twitter": {
        "name": "Twitter / X",
        "prompt_extra": (
            "For 'social', craft a Twitter/X-style caption: concise, punchy, and witty. "
            "MUST be under 280 characters total including hashtags. "
            "Use 1-3 relevant hashtags woven naturally into the text. "
            "Use a bold hook or hot take format."
        ),
        "style": "concise, witty, punchy, thread-worthy",
    },
    "youtube": {
        "name": "YouTube",
        "prompt_extra": (
            "For 'social', craft a YouTube video description: engaging first 2 lines "
            "(above the fold), then a detailed description. Include 5-10 relevant "
            "hashtags at the end. Add a call-to-action (subscribe, like, comment). "
            "Total length 200-500 characters."
        ),
        "style": "descriptive, SEO-friendly, CTA-driven, timestamp-friendly",
    },
    "pinterest": {
        "name": "Pinterest",
        "prompt_extra": (
            "For 'social', craft a Pinterest-style description: keyword-rich, "
            "descriptive, and searchable. 100-200 characters. Use 2-4 relevant "
            "hashtags. Focus on what makes the image useful or inspiring. "
            "Write in a way that helps pinners find this content."
        ),
        "style": "keyword-rich, searchable, inspirational",
    },
}


def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not set. "
            "Please add it to your .env file."
        )
    return genai.Client(api_key=api_key)


def generate_captions(image_path: str, platform: str = "general", caption_hint: str = "", caption_type: str = "all") -> dict:
    """
    Analyzes an image and generates captions using Gemini 2.5 Flash.
    Supports platform-specific caption styles and caption type selection.
    """
    try:
        client = get_gemini_client()
        img = Image.open(image_path)

        config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS["general"])
        platform_extra = config["prompt_extra"]

        # Build prompt based on caption_type
        if caption_type == "all":
            prompt = (
                "Analyze this image carefully and return a JSON object with exactly three keys:\n"
                "1. 'descriptive': A highly detailed, literal description of everything visible in the image "
                "(objects, people, colors, composition, setting, mood, lighting).\n"
                "2. 'social': An engaging caption optimized for the target platform. "
                f"{platform_extra}\n"
                "3. 'accessibility': Concise, screen-reader-friendly alt-text (max 125 chars) "
                "that conveys the essential content and purpose of the image.\n\n"
                "Return ONLY the raw JSON object. Do not include markdown code blocks, "
                "backticks, or any formatting wrapper."
            )
        elif caption_type == "descriptive":
            prompt = (
                "Analyze this image carefully and return a JSON object with exactly one key:\n"
                "1. 'descriptive': A highly detailed, literal description of everything visible in the image "
                "(objects, people, colors, composition, setting, mood, lighting)"
            )
            if caption_hint:
                prompt += f". The user wants you to focus on: {caption_hint}"
            prompt += ".\n\nReturn ONLY the raw JSON object."
        elif caption_type == "social":
            prompt = (
                "Analyze this image carefully and return a JSON object with exactly one key:\n"
                "1. 'social': An engaging caption optimized for the target platform. "
                f"{platform_extra}"
            )
            if caption_hint:
                prompt += f" The user wants you to focus on: {caption_hint}"
            prompt += "\n\nReturn ONLY the raw JSON object."
        elif caption_type == "accessibility":
            prompt = (
                "Analyze this image carefully and return a JSON object with exactly one key:\n"
                "1. 'accessibility': Concise, screen-reader-friendly alt-text (max 125 chars) "
                "that conveys the essential content and purpose of the image"
            )
            if caption_hint:
                prompt += f". The user wants you to focus on: {caption_hint}"
            prompt += ".\n\nReturn ONLY the raw JSON object."

        # Add caption hint to the prompt if provided
        if caption_hint and caption_type == "all":
            hint_prompt = f"\n\nUser hint for more focused captions: {caption_hint}"
            prompt = prompt.replace(
                "Return ONLY the raw JSON object.",
                hint_prompt + "\n\nReturn ONLY the raw JSON object."
            )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, img],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        try:
            result = json.loads(response.text)
            return {
                "descriptive": result.get("descriptive", "No descriptive caption generated."),
                "social": result.get("social", "No social caption generated."),
                "accessibility": result.get("accessibility", "No alt-text generated."),
                "platform": platform,
                "platform_name": config["name"],
            }
        except json.JSONDecodeError:
            print("Failed to parse JSON from Gemini. Raw response:", response.text)
            return {"error": "Invalid response format from AI. Could not parse JSON."}

    except Exception as e:
        print(f"Error in vision engine: {e}")
        return {"error": str(e)}


CAPTION_TYPE_PROMPTS = {
    "promotional": (
        "Write a promotional/marketing caption that sells or highlights a product, service, or brand. "
        "Use persuasive language, highlight benefits, and include a strong call-to-action."
    ),
    "inspirational": (
        "Write an inspirational/motivational caption that uplifts and empowers the reader. "
        "Use powerful words, metaphors, and an emotionally resonant tone."
    ),
    "informative": (
        "Write an informative/educational caption that teaches or explains something valuable. "
        "Be clear, factual, and provide useful insights or tips."
    ),
    "humorous": (
        "Write a humorous/witty caption that makes the reader smile or laugh. "
        "Use wordplay, puns, relatable humor, or clever observations."
    ),
    "storytelling": (
        "Write a storytelling/narrative caption that tells a brief, compelling story. "
        "Use vivid imagery, a clear arc, and an emotional hook."
    ),
    "question": (
        "Write a question-based engagement caption that sparks curiosity and invites responses. "
        "Ask thought-provoking questions that encourage comments and discussion."
    ),
    "cta": (
        "Write a call-to-action caption that directly asks the reader to take a specific action. "
        "Be clear, direct, and motivating (e.g., 'Sign up now', 'Share with a friend', 'Drop a comment')."
    ),
    "seasonal": (
        "Write a seasonal/trending topic caption tied to current events, holidays, or cultural moments. "
        "Be timely, relevant, and tap into what people are talking about right now."
    ),
}

CAPTION_TONE_GUIDE = {
    "formal": "Use formal, polished language. Avoid slang and contractions. Professional tone throughout.",
    "casual": "Use casual, friendly language. Contractions are fine. Conversational and relaxed tone.",
    "professional": "Use professional but approachable language. Clear, confident, and industry-appropriate.",
    "playful": "Use playful, fun language. Emojis, exclamations, and lighthearted expressions are encouraged.",
}

PLATFORM_LIMITS = {
    "general": {"min": 50, "max": 500, "ideal": "100-300 characters"},
    "instagram": {"min": 50, "max": 2200, "ideal": "138-150 characters"},
    "linkedin": {"min": 150, "max": 3000, "ideal": "150-300 words"},
    "facebook": {"min": 40, "max": 63206, "ideal": "100-250 characters"},
    "twitter": {"min": 20, "max": 280, "ideal": "71-100 characters"},
    "tiktok": {"min": 20, "max": 150, "ideal": "under 150 characters"},
    "youtube": {"min": 100, "max": 5000, "ideal": "200-500 characters"},
    "pinterest": {"min": 50, "max": 500, "ideal": "100-200 characters"},
}


def generate_captions_from_text(
    description: str,
    platform: str = "general",
    caption_type: str = "promotional",
    tone: str = "casual",
    count: int = 3,
) -> dict:
    """
    Generates multiple caption variations from a text description.
    """
    try:
        client = get_gemini_client()

        config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS["general"])
        platform_extra = config["prompt_extra"]
        type_prompt = CAPTION_TYPE_PROMPTS.get(caption_type, CAPTION_TYPE_PROMPTS["promotional"])
        tone_guide = CAPTION_TONE_GUIDE.get(tone, CAPTION_TONE_GUIDE["casual"])
        limits = PLATFORM_LIMITS.get(platform, PLATFORM_LIMITS["general"])

        prompt = (
            f"You are an expert social media copywriter. The user has provided the following description or context:\n\n"
            f'"{description}"\n\n'
            f"Caption type: {caption_type} — {type_prompt}\n"
            f"Tone: {tone} — {tone_guide}\n"
            f"Platform: {platform} ({config['name']}) — {platform_extra}\n"
            f"Character range: aim for {limits['ideal']}, max {limits['max']} characters.\n\n"
            f"Generate exactly {count} distinct caption variations. Each should be a unique take on the same concept.\n"
            f"Return a JSON object with a single key 'captions' containing an array of {count} strings. "
            f"Each string is one complete caption.\n"
            f"Return ONLY the raw JSON object. No markdown, no backticks, no formatting wrapper."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        try:
            result = json.loads(response.text)
            captions_list = result.get("captions", [])
            if not captions_list:
                return {"error": "No captions were generated. Try a different description."}
            return {
                "success": True,
                "captions": captions_list,
                "platform": platform,
                "platform_name": config["name"],
                "caption_type": caption_type,
                "tone": tone,
                "count": len(captions_list),
                "limits": limits,
            }
        except json.JSONDecodeError:
            print("Failed to parse JSON from Gemini. Raw response:", response.text)
            return {"error": "Invalid response format from AI. Could not parse JSON."}

    except Exception as e:
        print(f"Error generating text captions: {e}")
        return {"error": str(e)}
