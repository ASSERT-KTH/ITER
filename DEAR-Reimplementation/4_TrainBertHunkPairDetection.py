import numpy as np
import pandas as pd
import torch,sys
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, RandomSampler, SequentialSampler
import warnings
from torch import cuda
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from transformers import DataCollatorWithPadding
import torch.autograd as autograd
import csv
import os
from datasets import load_dataset
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer
import evaluate


def preprocess_function(examples):
    return tokenizer(examples["text"], truncation=True)       


def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return accuracy.compute(predictions=predictions, references=labels)
    
if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    SEED=42
    TRAIN_EPOCHS = 5
    MAX_LEN = 128
    device = 'cuda' if cuda.is_available() else 'cpu'
    TRAIN_PATH='TrainingPairs.csv'
    imdb = load_dataset("csv", data_files=TRAIN_PATH,on_bad_lines='skip',sep='\t')
    print(imdb['train'][1])
    print(imdb['train'][2])  
    
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")   
    tokenized_imdb = imdb.map(preprocess_function, batched=True)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    
    id2label = {0: "NEGATIVE", 1: "POSITIVE"}
    label2id = {"NEGATIVE": 0, "POSITIVE": 1}
    
    accuracy = evaluate.load("accuracy")
    
    model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2, id2label=id2label, label2id=label2id)
    
    training_args = TrainingArguments(
    output_dir="DEAR_BERT_Hunk_Detection_Modle",
    learning_rate=1e-5,
    per_device_train_batch_size=64,
    per_device_eval_batch_size=64,
    num_train_epochs=5,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    push_to_hub=False,)
    
    trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_imdb["train"],
    eval_dataset=tokenized_imdb["train"],
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)
    
    trainer.train()
    
