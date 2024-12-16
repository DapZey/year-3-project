from PIL import Image
import torch


def analyze_images(model, processor, id):
    image1 = Image.open(f"client{id}.png")
    image2 = Image.open("test.jpg")
    inputs = processor(text=[""], images=[image1, image2], return_tensors="pt", padding=True)
    outputs = model(**inputs)

    embedding1 = outputs.image_embeds[0]
    embedding2 = outputs.image_embeds[1]
    embedding1 = embedding1.unsqueeze(0)
    embedding2 = embedding2.unsqueeze(0)
    similarity_score = torch.cosine_similarity(embedding1, embedding2)
    print(f"Similarity score between images: {similarity_score.item()}")
    return similarity_score.item()
