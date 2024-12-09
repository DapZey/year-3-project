from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
from multiprocessing import freeze_support


def analyze_images(model, processor, id):
    image1 = Image.open(f"client{id}.png")
    image2 = Image.open("client1.png")

    # Process the images
    inputs = processor(text=[""], images=[image1, image2], return_tensors="pt", padding=True)

    # Perform the inference
    outputs = model(**inputs)

    embedding1 = outputs.image_embeds[0]
    embedding2 = outputs.image_embeds[1]

    # Add an extra batch dimension to each embedding
    embedding1 = embedding1.unsqueeze(0)
    embedding2 = embedding2.unsqueeze(0)

    # Compute cosine similarity between the two embeddings
    similarity_score = torch.cosine_similarity(embedding1, embedding2)

    print(f"Similarity score between images: {similarity_score.item()}")
