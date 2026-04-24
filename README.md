# Devina Hermawan Recipe Dictionary from Youtube

## Scraping videos from Devina Hermawan youtube channel (no-scroll)
at `fetch_yt.py` I scraped the page that are intially loaded when first time enter Devina Hermawan's videos without scrolling. I perform this task using wreq from python. Later I know that because of "endless-scroll" system on youtube channel's videos, I can't using this way and I have to find another way.

## Manually scrolling and scraping using js script
I manually scrolling through all Devina Hermawan's videos and scraping using js script run in browser console, the js script I use to perform this task is in `js_fetch_all_videos.txt`. With that script I am able to produce file like `parsed_videos_with_thumbnails.txt`.

## Scraping the recipe in Videos's Description
The last task I had to perform to got all the data I need, is asynchronously scraping the description of all the youtube-url videos I already got using wreq in python. Both Indonesian and English version and store it in different file `dataset_resep_indonesia.txt` and `dataset_resep_inggris.txt`.

## Web app to search what to cook with certain ingredients
After I got all the data I need. I am able to make a streamlit web app `app.py` to search with certain ingredients I have/want to cook. I even able to search multiple ingredients, and the search result is giving me the title of the video, the thumbnails, and the link to the youtube videos and LET ME COOK!!! ^_^
