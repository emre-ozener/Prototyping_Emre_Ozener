# Assignment 1: Streamlit App
- **Streamlit App** that helps landlords to estimate the nightly price, view the statitstics of other listings, calculate the revenue, and download the report and graphs. 


## Which Model?
I have chosen the machine learning model used in the Artificial Intelligence 1 course hackathon, where the task was to train a model to predict the pricing of an Airbnb listing. I selected this model due to the variety of features and the extensive amount of data available.

## Description of the Prototype
My prototype is designed as a tool for landlords to determine the price of their listing on the platform, analyze trends, calculate revenue, and download relevant files. The initial tab allows users to estimate the price of a listing based on its features. In the second tab, they can calculate their potential revenue. The third tab provides overall statistics on the dataset, allowing users to select and view different graphs, which can also be downloaded. Lastly, the final tab allows users to download a comprehensive report.

## Difficulties Faced
The main challenge in this assignment was incorporating practical utility beyond simple price prediction. To address this, I implemented additional features such as revenue calculation, interactive data visualization, and download functions to enhance usability. Initially, I intended to allow users to download files as PDFs, but integrating the necessary libraries proved challenging. As an alternative, I opted for text file downloads, though this is somewhat less convenient for the end user.

## Contents of the Folder: 
1. airbnb_price_model.pkl & preprocessing_pipeline.pkl : docs that were used in the app to load the model.
2. assignment_app.py : streamlit app

## Extra Notes:
- Make sure the file paths are adapted after the download.

