#  Development and research of methods for predicting the popularity of video content.
This repository contains implementations of a number of models that are designed to solve the problem of predicting video popularity.
# Data set.
To run the method, it is both possible to download existing data with the wget utility from the google drive and to create a new dataset. To collect new data, a parser ('parser' folder) in Python 3 has been created.
## Using parser to collect videos from YouTube channels:
- Download Python 3.6.8.
- Run the install.bat file to install all the required libraries.
- Create Youtube Data API keys  and save them in the api.txt file (each key on a new line).
- Add YouTube channel links to the Urls.txt file (one link per line).
- Launch start.bat.
- Start start_new_view_count.bat to collect the views of every video.
## Using a parser to collect data about popular videos in a certain region:
- Download Python 3.6.8.
- Run the install.bat file to install all of the required libraries.
- Create Youtube Data API keys  and save them in api.txt file (one key per line).
- Set the limit on the number of videos downloaded and select the region in the config file.
- Start the start_new.bat file.
- Launch the start_new_view_count.bat file to collect views for each video.
# Implemented methods.
### 1. Prediction Method using visual characterisitics of a video using LRCN architecture.
Using a pretrained Convolutional Network Resnet-152, visual cues are extracted from video frames. The attributes of each frame are sequentially fed into an LSTM cell. Next, a two-layer MLP network is applied for classification.

### 2. Prediction Method, which uses Bidirectional Long Term Memory architecture to predict popularity of a YouTube video using the title.
Video titles are rendered using pretrained GLOVE embeddings. To analyze a title, the obtained representations are given to the BiLSTM network as input. The outputs of the BiLSTM network are then fed to the fully connected network for classification.

### 3. Popularity prediction method based on convolutional network and BiLSTM cell. (Multimod_simple)
This method is a combination of the two previous methods. Text is processed using the GLOVE + BILSTM method, and frames are analyzed using the RESNET + LSTM method. The obtained representations are concatenated and a two-layer fully connected network is constructed for classification.


### 4. Method for predicting the popularity of video content based on statistics of the video and the according YouTube video channel using a neural network. (Statistics)
The method uses quantitative data to predict the popularity of a video. The model consists of fully connected layers and activation functions.

### 5. Method for predicting the popularity of video content based on statistics of video content and the according YouTube video channel using an ensemble of trees Gradientboosting.(Gradient_boosting)
Gradientboosting is used to predict popularity, which is applied only to quantitative and categorical features(represented using OneHot).

### 6. Method for predicting the popularity of video content based on statistics of video content and YouTube video channel using an ensemble of trees XGBClassifier. (Xgb_classifier)
The XGBClassifier is used to predict popularity. The number of views of previous video, channel statistics, the title of the video and the "attractiveness" of the video preview are used as variables to predict the number of views.

### 7. Method for predicting the popularity of video content based on statistics of video content and the YouTube video channel using the RandomForestClassifier tree ensemble. (Random_forest_classifier)
RandomForestClassifier is used to predict popularity. The statistics of views of the previous video and channel, the title of the video and the "attractiveness" of the video preview are used as indicators to predict the number of views.

# Launching the project.
In order to run the methods, you must run the .ipynb cells sequentially. files.

# Required libraries.
- Python 3.6.8
- Pytorch 1.5.0
- Numpy 1.18.0
- Pandas 1.0.3
- Open-CV 3.4.2











