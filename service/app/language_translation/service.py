import logging
from typing import Dict, Optional, List
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from IndicTransToolkit import IndicProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndicTransOnlyTranslator:
    """
    Translation service using IndicTrans2 AI4Bharat model + IndicProcessor
    """

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._initialize_model()

    def _initialize_model(self):
        """Initialize IndicTrans2 AI4Bharat model + processor"""
        try:
            model_name = "ai4bharat/indictrans2-indic-en-1B"
            logger.info(f"Loading IndicTrans2 model: {model_name} on {self.device}")

            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)

            # Use IndicProcessor for preprocessing + postprocessing
            self.processor = IndicProcessor(inference=True)

            logger.info("IndicTrans2 model + processor loaded successfully")
        except Exception as e:
            logger.error(f"Error loading IndicTrans2: {e}")
            self.model, self.tokenizer, self.processor = None, None, None

    def translate(self, sentences: List[str], src_lang: str = "mar_Deva", tgt_lang: str = "eng_Latn") -> List[str]:
        """
        Translate a batch of sentences from Marathi (Devanagari) to English (Latin script).
        Args:
            sentences (list of str): Input Marathi sentences.
            src_lang (str): Source language code.
            tgt_lang (str): Target language code.
        Returns:
            list of str: Translated English sentences.
        """
        if not self.model or not self.tokenizer or not self.processor:
            logger.error("Model or tokenizer not available")
            return []

        try:
            # Step 1: Preprocess input batch
            batch = self.processor.preprocess_batch(sentences, src_lang=src_lang, tgt_lang=tgt_lang)

            # Step 2: Tokenize
            inputs = self.tokenizer(
                batch,
                truncation=True,
                padding="longest",
                return_tensors="pt",
                return_attention_mask=True,
            ).to(self.device)

            # Step 3: Generate translations
            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    use_cache=False,
                    min_length=0,
                    max_length=256,
                    num_beams=5,
                    num_return_sequences=1,
                )

            # Step 4: Decode
            generated_texts = self.tokenizer.batch_decode(
                generated_tokens.detach().cpu().tolist(),
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )

            # Step 5: Postprocess
            translations = self.processor.postprocess_batch(generated_texts, lang=tgt_lang)

            return translations

        except Exception as e:
            logger.error(f"Translation error: {e}")
            return []

if __name__ == "__main__":
    translator = IndicTransOnlyTranslator()
    sentences = ["नमस्कार", "माझं नाव अभिषेक आहे.", "मराठी भाषा सुंदर आहे", "कृषी विकासासाठी नवीन योजना आखण्यात आली आहे.", "पर्यावरण संरक्षणासाठी नवे उपाय योजित आहेत."]
    translations = translator.translate(sentences, src_lang="mar_Deva", tgt_lang="eng_Latn")
    for s, t in zip(sentences, translations):
        print(f"Marathi: {s}")
        print(f"English: {t}")
