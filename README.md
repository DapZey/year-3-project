# Paint-Draw Game with AI Image Comparison

## Use Case:
The use case is a head-to-head game. Two players (maybe more) need to draw a copy of a random image in an MS paint style application in a set amount of time. When time runs out, an AI model will determine which player's image more closely resembles the original. The more accurate image wins.

## Technologies (subject to change):
- **CPP front end / Python server**
- **Boost.asio** (for networking in CPP)
- **Python socket.io** (networking in Python)
- **Lorem Picsum API** (for generating random images)
- **CLIP AI model** (for analyzing image similarity)
- **RayLib** (graphics library for the painting app)
- **Python multithreading** (server side, for analyzing images, and for separating clients)
- **CPP threads** (client side, to dedicate a separate thread for network-related functions)

## TODO:
- **Create MS paint style application** that contains:
  - RGB selector
  - Brush thickness selector
  - Reset/go back commands to fix mistakes
  - Game timer
  - Image to draw
  - Current drawing score
  - Opponent's current score
- **Create client/server side functionality** to save what is currently drawn (so it can be sent)
- **Create concurrent networking functions on client side** (for sending/receiving)
- **Create connectivity protocol between client/server**
  - Safely sending/resending an image (JPEG) from client to server
  - Server tells client it finished analyzing image, gives a score, and is ready for a new version to analyze
  - Client sends new image and so on
- **Create concurrent networking and image processing functionality on server side** (to handle two players/two image sets)
- **Code game logic on server side**
  - Start of game
  - Handling receiving/sending images
  - Global countdown timer
  - End of game
- **Generation of new image for players to draw**
  - Connect server to Lorem Picsum API for handing out a reference image at the start of each game
  - Generate random image
  - Send image to both clients under the pretext that it is their reference to draw
  - Use same random image as comparison mediator between the AI and what clients send
- **Additional networking logic on both client and server**
  - Connect to server (localhost for now, possible domain or IP selection later)
  - Start a game
  - Restart a game
  - Game over/connect pages on client
  - More than two players per game?
  - More than one game per server?
- **Host on AWS EC2 or Lightsail for true online play** (I already own a deployed real-time Python server)
