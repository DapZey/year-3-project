import network
from multiprocessing import freeze_support
from transformers import CLIPProcessor, CLIPModel
if __name__ == '__main__':
    try:
        print("starting server...")
        freeze_support()
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        print("start finished")
        network.main(model, processor)

    except OSError as e:
        print("Error loading model. Make sure you have an internet connection and try running:")
        print("pip install --upgrade transformers")
        print("pip install torch")
        print(f"Error details: {e}")
