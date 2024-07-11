import os
from django.core.management.base import BaseCommand
from transformers import AutoModel, AutoTokenizer

class Command(BaseCommand):
    help = 'Save a pre-trained model and tokenizer'

    def handle(self, *args, **options):
        model_name = 'gpt2'
        new_model_name = 'fine-tuned-gpt2'

        # Load the model and tokenizer
        self.stdout.write(self.style.NOTICE(f'Loading model and tokenizer from {model_name}...'))
        model = AutoModel.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Save the model and tokenizer with the new name
        self.stdout.write(self.style.NOTICE(f'Saving model and tokenizer to {new_model_name}...'))
        os.makedirs(new_model_name, exist_ok=True)
        model.save_pretrained(new_model_name)
        tokenizer.save_pretrained(new_model_name)

        self.stdout.write(self.style.SUCCESS(f"Model and tokenizer saved to {new_model_name}/"))
