import spacy
from google.cloud import translate_v3 as translate
import re
from typing import List, Dict, Tuple
import os

# --- Configuration ---
filename: str = "VerneVoyage_short.txt"
# Assuming target language is English (en) for the translation
target_language: str = "en"
# Assuming French (fr) based on your original code and novel choice
source_language: str = "fr" 

# Set up spaCy
# You might need to run: python -m spacy download fr_core_news_sm
try:
    nlp = spacy.load("fr_core_news_sm")
except OSError:
    print("Downloading spaCy model 'fr_core_news_sm'...")
    # This block is for illustration; in a production script, you'd run the command directly
    # or handle the download within the script if preferred.
    raise Exception("Please run: python -m spacy download fr_core_news_sm")


# --- File I/O ---
def load_text(file_path: str) -> str:
    """Loads the text file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return ""

# --- Text Processing (spaCy & Cleaning) ---
def extract_unique_lemmas(text: str) -> List[Tuple[str, str]]:
    """
    Uses spaCy for tokenization, lemmatization, filtering, and POS tagging.
    Returns a list of unique (lemma, pos) tuples.
    """
    doc = nlp(text)
    
    # Define a set of undesirable POS tags and token types
    # This is more robust than simple stop word removal
    undesirable_pos: set = {"SPACE", "PUNCT", "SYM", "NUM", "X", "DET", "ADP", "SCONJ", "CCONJ", "AUX"}
    
    unique_lemmas: Dict[str, str] = {} # Key is lemma, Value is its first observed POS
    
    for token in doc:
        # 1. Basic Cleaning & Filtering
        if (token.is_alpha and # Only include alphabetic tokens
            not token.is_stop and # Exclude standard French stop words (handled by spaCy's model)
            token.pos_ not in undesirable_pos):
            
            # Convert the lemma to lowercase and strip leading/trailing non-alpha chars (just in case)
            lemma = token.lemma_.lower().strip()
            
            # 2. Filtering for common edge cases (e.g., single letters that aren't stop words)
            if len(lemma) > 1 or (len(lemma) == 1 and lemma not in ('y', 'a', 'à', 'ô', 'ç')):
                
                # We store the most common/first observed POS, but the final output
                # will rely on the translation service for POS-specific translations.
                if lemma not in unique_lemmas:
                    unique_lemmas[lemma] = token.pos_

    # Return the sorted list of unique lemmas (base forms)
    return sorted(list(unique_lemmas.keys()))


# --- Translation (Google Cloud Translation API) ---

def translate_word_list(words: List[str], target_lang: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Uses the Google Cloud Translation API to translate a batch of words 
    and returns structured data. Requires API credentials to be set up.
    
    Returns: {lemma: [{'pos': str, 'translation': str}, ...], ...}
    """
    # NOTE: This part requires you to have authenticated your environment
    # (e.g., via 'gcloud auth application-default login') and enabled
    # the Cloud Translation API for your project.
    
    # Initialize the client (automatically uses credentials)
    translate_client = translate.TranslationServiceClient()
    
    # Replace 'YOUR_PROJECT_ID' with your actual Google Cloud Project ID
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "translateverne")

    if project_id == "YOUR_PROJECT_ID":
        print("\n*** WARNING: Please set the GOOGLE_CLOUD_PROJECT environment variable or replace 'YOUR_PROJECT_ID' in the code. ***\n")
        
    location = "global"  # Or another region, e.g., "us-central1"
    parent = f"projects/{project_id}/locations/{location}"

    print(f"Requesting translation for {len(words)} unique words...")

    # The translate_text method is the single request for all words
    response = translate_client.translate_text(
        parent=parent,
        contents=words,
        target_language_code=target_lang,
        source_language_code=source_language,
        model="base", # Use 'nmt' for Neural Machine Translation if needed, 'base' is often fine.
    )

    lexicon_data: Dict[str, List[Dict[str, str]]] = {}

    for i, translation in enumerate(response.translations):
        source_word = words[i]
        
        # The V3 API response format is more direct than the old googletrans library.
        # It gives you the translated text, but does not inherently return a list 
        # of POS-specific translations (like the 'extra_data' you were using).
        # To get structured, POS-specific translations, we would need to use a more
        # sophisticated NMT model or a dedicated dictionary API. 
        #
        # For simplicity and to match the single-line output format, we will combine 
        # the **spaCy POS** with the **primary translation**.
        
        # If the goal is strictly a single request (as per your plan), the V3 API is the way to go.
        # If the goal is to get multiple POS translations, you might need to revert to 
        # the multiple-request pattern, or use a tool like a dedicated dictionary API.
        
        # Sticking to the single-request structure and focusing on the lemma/primary translation:
        
        # NOTE: Since we lack the 'all-translations' feature from googletrans, we'll
        # just record the primary translation and mark the POS as the one identified by spaCy.
        
        lexicon_data[source_word] = [
            {
                "pos": "?", # Placeholder: Cannot get multiple POS from a single V3 API request
                "translation": translation.translated_text
            }
        ]

    return lexicon_data


# --- Output Formatting ---
def format_lexicon_output(data: Dict[str, List[Dict[str, str]]], spacy_lemmas: List[str]) -> str:
    """
    Formats the final lexicon data into the desired plain text output.
    Format: base form - translation; translation
    (Simplifying the format since the V3 API gives only one primary translation)
    """
    output_lines: List[str] = []
    
    # Iterate through the *sorted* list of lemmas from spaCy for clean output
    for word in spacy_lemmas:
        if word in data and data[word]:
            # The data currently holds only one entry (the primary translation)
            translation_text = data[word][0]['translation']
            
            # Final output format: base form - part of speech, translation; part of speech, translation
            # Since we only have the primary translation, we simplify it.
            # If you were able to run your original code on a small list, you could 
            # use that structure, but for the batch API, this is the most reliable format.
            
            # Using a simplified format: Lemma - Primary Translation
            # NOTE: If you integrate the spaCy POS back, you'd do: f"{word} - {spacy_pos}, {translation_text}"
            output_lines.append(f"{word} - {translation_text}")
    
    return "\n".join(output_lines)

def save_output(content: str, output_file: str = "lexicon_output.txt"):
    """Saves the final formatted content to a text file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\nSUCCESS: Lexicon saved to '{output_file}' with {len(content.splitlines())} entries.")

# --- Main Execution ---

if __name__ == "__main__":
    # 1. Load Text
    text_content = load_text(filename)
    if not text_content:
        exit()

    # 2. Extract & Clean (using spaCy)
    # This list will be the unique, sorted words (lemmas) for translation
    unique_lemmas = extract_unique_lemmas(text_content)
    print(f"Found {len(unique_lemmas)} unique base words (lemmas) after filtering.")
    
    # Optional: Save the list of unique lemmas to a file (as per your original plan)
    save_output("\n".join(unique_lemmas), "unique_lemmas.txt")

    # 3. Batch Translate
    # NOTE: Comment this out if you cannot configure Google Cloud credentials.
    # You would need to temporarily revert to the single-request loop with googletrans 
    # for testing without the full Google Cloud setup.
    translated_data = translate_word_list(unique_lemmas, target_language)

    # 4. Format and Save Final Lexicon
    final_output = format_lexicon_output(translated_data, unique_lemmas)
    save_output(final_output)
