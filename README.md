# EmotionPhotoBooth
A photo booth game that can detect if you're happy or sad then answer relevant questions<br>

## What it is
This is photobooth that can detect (using your webcamera) emotions. It allows users to play different emotion based games using a graphical interface made in Tkinter. At the end of the game the user is able to take a snapshot, print and place text on their image.<br>

## Install
Clone and change directory to the repository<br>


	git clone https://github.com/smerkousdavid/EmotionPhotoBooth ~/EmotionPhotoBooth
	cd ~/EmotionPhotoBooth

Install the dependencies<br>

	
	sudo pip install -r requirements.txt

**If you want to build your own facial recognition dataset**<br>
Make sure to read these instructions<br><br>

Create the required directories


	cd ~/EmotionPhotoBooth
	mkdir sorted_set source_emotion source_images dataset
	

Download the CK+ and Emotion Labels datasets from Cohn-Kanade<br>
Once completed unzip the folder(s) near the EmotionPhotoBooth folder<br>
**You must register via a valid email**


	http://www.consortium.ri.cmu.edu/ckagree/

Organizing the datasets<br>
1. Move all of the folders containing *.txt into the source_emotion folder
2. Move all of the folders containing the images into the source_images folder<br>

Run the premade cascade training (Modify the main file or import emotionset.py)<br>

	from config import Config
	from emotionset import Emotions
	
	config = Config()
	emotions = Emotions(config)
	
	emotions.calibrateCascades() # Crop the current datasets and just get the sorted cascade images (This will open a new window for every image)
	emotions.createDataset() # Create the organized image data set with the cropped images
	emotions.train() # Train and write the image datasets to the trainer.txt
	emotions.run_test() # Test the trainer (It will print the success rate, the emotion labels must be present)

You're done!

## License
MIT License<br><br>

Copyright (c) 2017 David Smerkous<br><br>

Permission is hereby granted, free of charge, to any person obtaining a copy<br>
of this software and associated documentation files (the "Software"), to deal<br>
in the Software without restriction, including without limitation the rights<br>
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell<br>
copies of the Software, and to permit persons to whom the Software is<br>
furnished to do so, subject to the following conditions:<br><br>

The above copyright notice and this permission notice shall be included in all<br>
copies or substantial portions of the Software.<br><br>

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR<br>
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,<br>
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE<br>
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER<br>
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,<br>
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE<br>
SOFTWARE.<br><br>


## Citations
Paul van Gent, 2016<br>
van Gent, P. (2016). Emotion Recognition With Python, OpenCV and a Face Dataset.<br>
A tech blog about fun things with Python and embedded electronics. Retrieved from:<br>
http://www.paulvangent.com/2016/04/01/emotion-recognition-with-python-opencv-and-a-face-dataset/<br><br>

Cohn, &Tian and Lucey, 2000<br>
Cohn, T., & L. (n.d.). Cohn-Kanade (CK and CK ) database Download Site. Retrieved March 02, 2017, from http://www.consortium.ri.cmu.edu/ckagree/


