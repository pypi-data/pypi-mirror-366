import google.generativeai as genai
import json
import logging
from earnings_analyzer.config import get_gemini_api_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# DO NOT configure genai at module level - move it into functions

def analyze_sentiment(transcript_text, model_name="gemini-2.5-flash"):
    """
    Analyzes the sentiment of an earnings call transcript using the Gemini API.

    Args:
        transcript_text: The full text of the earnings call transcript.
        model_name: The name of the Gemini model to use (e.g., 'gemini-2.5-flash', 'gemini-1.5-pro').

    Returns:
        A dictionary containing the sentiment analysis results, or None on failure.
    """
    if not transcript_text or transcript_text.strip() == "":
        logging.warning("Transcript text is empty. Cannot perform sentiment analysis.")
        return None

    api_key = get_gemini_api_key()
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""As a financial analyst, please analyze the following earnings call transcript.
    Based on the language, tone, and key topics discussed by the executives, provide a sentiment analysis.
    Return your analysis as a JSON object with the following four fields:
    1.  `overall_sentiment_score`: A numerical score from 1 (very negative) to 10 (very positive).
    2.  `confidence_level`: Your confidence in this sentiment score, from 0.0 to 1.0.
    3.  `key_themes`: A JSON list of the top 3-5 most important themes or topics discussed.
    4.  `qualitative_assessment`: A 2-3 sentence qualitative assessment of the executive sentiment during the earnings call, focusing on the overall tone and the implications of the key themes.

    Transcript:
    ---
    {transcript_text} # Use the full transcript
    ---
    """
            response = model.generate_content(prompt)
            cleaned_json_string = response.text.strip().replace('```json', '').replace('```', '').strip()
            analysis_result = json.loads(cleaned_json_string)
            return analysis_result
        except Exception as e:
            logging.error(f"An error occurred during sentiment analysis: {e}")
            return None
    else:
        logging.error("GEMINI_API_KEY is not set in the environment variables. Please set it to use Gemini API.")
        return None

if __name__ == '__main__':
    # Example usage: Read the transcript file and analyze its sentiment
    try:
        with open("transcript.txt", "r", encoding="utf-8") as f:
            transcript = f.read()
        
        logging.info("Analyzing transcript sentiment...")
        sentiment_data = analyze_sentiment(transcript)

        if sentiment_data:
            logging.info("\n--- Sentiment Analysis Results ---")
            logging.info(f"Overall Sentiment Score: {sentiment_data.get('overall_sentiment_score')}")
            logging.info(f"Confidence Level: {sentiment_data.get('confidence_level')}")
            logging.info("Key Themes:")
            for theme in sentiment_data.get('key_themes', []):
                logging.info(f"- {theme}")
            
            # Generate and print qualitative assessment
            qualitative_assessment = generate_qualitative_assessment(sentiment_data)
            if qualitative_assessment:
                logging.info("\n--- Qualitative Assessment ---")
                logging.info(qualitative_assessment)
        else:
            logging.error("Sentiment analysis failed.")

    except FileNotFoundError:
        logging.error("Error: transcript.txt not found. Please run the parser first.")
