import network

if __name__ == '__main__':
    try:
        network.main()
    except OSError as e:
        print("Error loading model. Make sure you have an internet connection and try running:")
        print("pip install --upgrade transformers")
        print("pip install torch")
        print(f"Error details: {e}")
