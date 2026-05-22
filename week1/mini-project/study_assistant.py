import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


def init_model():
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    return model, tokenizer, device


def generate_text(model, tokenizer, device, prompt, max_new_tokens=100):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    output = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        num_beams=4,
        early_stopping=True,
    )

    return tokenizer.decode(output[0], skip_special_tokens=True).strip()


def summarize_text(model, tokenizer, device, text):
    prompt = f"summarize: {text.strip()}"
    return generate_text(model, tokenizer, device, prompt)


def answer_question(model, tokenizer, device, context, question):
    prompt = f"question: {question.strip()} context: {context.strip()}"
    return generate_text(model, tokenizer, device, prompt)


if __name__ == "__main__":
    print("Loading model...")
    model, tokenizer, device = init_model()
    print("AI Study Assistant Ready!\n")

    while True:
        print("1. Summarize Text")
        print("2. Ask Question")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "3":
            print("Goodbye!")
            break

        if choice == "1":
            text = input("\nEnter text to summarize:\n")
            summary = summarize_text(model, tokenizer, device, text)
            print("\nSummary:")
            print(summary)
            print()

        elif choice == "2":
            context = input("\nEnter context/study material:\n")
            question = input("Enter question:\n")
            answer = answer_question(model, tokenizer, device, context, question)
            print("\nAnswer:")
            print(answer)
            print()

        else:
            print("Invalid choice\n")