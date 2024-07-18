import json
from datasets import load_dataset
from datasets import load_dataset, Features, Value
from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from transformers import pipeline
from deep_translator import GoogleTranslator
from celery import shared_task
# Load tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
# Set padding token to the EOS token
tokenizer.pad_token = tokenizer.eos_token

def define_question(data):
    """function to define question to fine tune model on this data"""
    list_question = [
        {
            "question": f"What is the total number of environmental labels {data['campany_name']} received in {data['year']}?",
            "answer": f"{data['campany_name']} received a total of {data['total_env_label']} environmental labels in {data['year']}."
        },
        {
            "question": f"What is the total number of social labels {data['campany_name']} received in {data['year']}?",
            "answer": f"{data['campany_name']} received a total of {data['total_soc_label']} environmental labels in {data['year']}."
        },
         {
            "question": f"What is the total number of governance labels {data['campany_name']} received in {data['year']}?",
            "answer": f"{data['campany_name']} received a total of {data['total_gov_label']} environmental labels in {data['year']}."
        },
        {
            "question": f"How many labels indicate opportunities for improvement in environmental performance for {data['campany_name']} in {data['year']}?",
            "answer": f"{data['total_env_opportunity']} of the environmental labels indicate opportunities for improvement."
        },
         {
            "question": f"How many labels indicate opportunities for improvement in social performance for {data['campany_name']} in {data['year']}?",
            "answer": f"{data['total_soc_opportunity']} of the social labels indicate opportunities for improvement."
        },
          {
            "question": f"How many labels indicate opportunities for improvement in governance performance for {data['campany_name']} in {data['year']}?",
            "answer": f"{data['total_gov_opportunity']} of the governance labels indicate opportunities for improvement."
        },
        {
            "question": f"Can you provide the breakdown of environmental risks identified for {data['campany_name']} in {data['year']}?",
            "answer": f"{data['campany_name']} faced {data['total_env_risk']} environmental risks in {data['year']}."
        },
        {
            "question": f"What is {data['campany_name']}'s total environmental score for {data['year']}?",
            "answer": f"{data['campany_name']}'s total environmental score for {data['year']} is {data['total_e_score']}."
        },
        {
            "question": f"In what areas could {data['campany_name']} potentially improve its environmental performance based on the provided data in {data['year']}?",
            "answer": f"{data['campany_name']} could potentially improve in areas related to reducing environmental risks and capitalizing on more opportunities for improvement."
        },
        {
            "question": f"How many social labels did {data['campany_name']} receive in {data['year']}?",
            "answer": f"{data['campany_name']} received a total of 69 social labels in {data['year']}."
        },
        {
            "question": f"What is {data['campany_name']}'s total governance score for {data['year']}?",
            "answer": f"{data['campany_name']}'s total governance score for {data['year']} is {data['total_g_score']}"
        },
        {
            "question": f"What is {data['campany_name']}'s total social score for {data['year']}?",
            "answer": f"{data['campany_name']}'s total social score for {data['year']} is {data['total_s_score']}"
        },
        {
            "question": f"What is {data['campany_name']}'s total environmental score for {data['year']}?",
            "answer": f"{data['campany_name']}'s total environmental score for {data['year']} is {data['total_e_score']}"
        },
        {
            "question": f"What is {data['campany_name']}'s total ESG score for {data['year']}?",
            "answer": f"{data['campany_name']}'s total ESG score for {data['year']} is {data['total_esg_score']}"
        },
       
    ]
    return list_question

def save_file_json(path_file, list_question):
    """add new data and save it to file"""
    try:
        with open(path_file, "r") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []
    print(existing_data)
    existing_data.extend(list_question)
    print(existing_data)
    with open(path_file, "w") as file:
        json.dump(existing_data, file, indent=4)

def split_data(file_path) :
    """split data into train data and test data"""
    features = Features({
    "question": Value("string"),
    "answer": Value("string")
    })

    # Load the dataset with specified features
    dataset = load_dataset('json', data_files=file_path, features=features)

    # Split dataset into train and validation sets
    split_datasets = dataset['train'].train_test_split(test_size=0.1)
    train_dataset = split_datasets['train']
    eval_dataset = split_datasets['test']
    return train_dataset,eval_dataset


def tokenize_function(examples):
    """Tokenize the dataset"""
    combined_texts = ["Question: " + q + "\nAnswer: " + a for q, a in zip(examples['question'], examples['answer'])]
    tokenized_output = tokenizer(combined_texts, truncation=True, padding='max_length', max_length=512)
    tokenized_output['labels'] = tokenized_output['input_ids'].copy()
    return tokenized_output

def fine_tune_model(train_dataset,eval_dataset,model_fine_tune):
    """function modeling to fine tune models with the training  and evaluation  data"""
 
    tokenized_train_dataset = train_dataset.map(tokenize_function, batched=True, remove_columns=["question", "answer"])
    tokenized_eval_dataset = eval_dataset.map(tokenize_function, batched=True, remove_columns=["question", "answer"])
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    training_args = TrainingArguments(
        output_dir='./results',
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=4,
        num_train_epochs=3,
        weight_decay=0.01,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train_dataset,
        eval_dataset=tokenized_eval_dataset,
        data_collator=data_collator,
    )

    trainer.train()
    model.save_pretrained(model_fine_tune)
    tokenizer.save_pretrained(model_fine_tune)
    
   
def translate_text(text, language):
    """Function to translate text to be compatible with models"""
    translated = GoogleTranslator(source='auto', target=language).translate(text)
    print(translated)
    return translated   
    
    
def get_response(model_fine_tune,question) :
        # Load the fine-tuned model
    model = GPT2LMHeadModel.from_pretrained(model_fine_tune)
    tokenizer = GPT2Tokenizer.from_pretrained(model_fine_tune)
    qa_pipeline = pipeline('text-generation', model=model, tokenizer=tokenizer)
    input_text = "question: " + question + " \n Answer:"
    # input_text=question +"\n"

    # Set `max_new_tokens` to avoid exceeding max length
    return qa_pipeline(input_text, max_new_tokens=50, max_length=512)
    
data = {
    "campany_name": "Orange",
    "year": 2022,
    "total_env_label": 16,
    "total_soc_label": 69,
    "total_gov_label": 0,
    "total_env_neutral": 11,
    "total_env_opportunity": 2,
    "total_env_risk": 3,
    "total_soc_neutral": 0,
    "total_soc_opportunity": 57,
    "total_soc_risk": 12,
    "total_gov_neutral": 0,
    "total_gov_opportunity": 0,
    "total_gov_risk": 0,
    "total_e_score": 14.28,
    "total_s_score": 67.77,
    "total_g_score": 0,
    "total_esg_score": 24.62
}  
# @shared_task(ignore_result=True)
# def fine_tune_model_task(data):
#     print("hello world finee tuneee !!")
#     file_path="data.json"
#     model_fine_tune="fine-tuned-gpt2"
#     list_question=define_question(data)
#     save_file_json(file_path,list_question) 
#     train_dataset,eval_dataset=split_data(file_path)
#     fine_tune_model(train_dataset,eval_dataset,model_fine_tune)  
@shared_task(ignore_result=True)
def fine_tune_model_task(data):
    try:
        # Example implementation of the task function
        # Ensure 'data' is properly processed here
        file_path = "data.json"
        model_fine_tune = "fine-tuned-gpt2"
        
        list_question = define_question(data)
        save_file_json(file_path, list_question)
        train_dataset, eval_dataset = split_data(file_path)
        fine_tune_model(train_dataset, eval_dataset, model_fine_tune)
        
    except Exception as e:
        # Handle exceptions properly based on your application's needs
        print(f"Error in fine_tune_model_task: {e}")



# list_question=define_question(data)
# print(list_question)
# save_file_json("data.json",list_question)        
# train_dataset,eval_dataset=split_data("data.json")
# model_fine_tune="fine-tuned-gpt2"
# fine_tune_model(train_dataset,eval_dataset,model_fine_tune)
# msg="Quel est ESG score pour  orange en 2022?"
# msg=translate_text(msg,"en")

# response=get_response(model_fine_tune,msg)
# print({"response":response})