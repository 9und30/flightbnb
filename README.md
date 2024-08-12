# 🛫 Airbnb & Flight Search API (Early Version)

This is an early version of an API that combines Airbnb listings and flight searches, similar to Booking.com.

⚠️ **Note**: Still under development. It requires optimization to reduce waiting times. Also the code is all unorganized and spaghetti as of right now. If the API does not work, the `refs.py` file might need updating—this hasn't been done yet.

## 🚀 Features
- Search for Airbnb listings and flights with a single API call.
- Customize your search with multiple parameters.

## 📋 API Parameters

- ```your_url/search/...```
- `start`: **Start location**
- `ziel`: **End location**
- `jahr`: **Year of travel**
- `monat`: **Month of travel**
- `dauer`: **Duration** (for now `weekend_trip` or `one_week`)
- `anzahl_gaeste`: **Number of guests**
- `max_preis_bnb`: **Maximum Airbnb price in total**
- `seiten` *(optional)*: **Number of Airbnb pages to scrape**
  - Good for wait time reduction

## 🛠 Requirements

- **Python Version**: definitely works for `3.12.2`
- **Python Libraries**:
  - `fastapi`
  - `selenium`
- **Google Chrome**
  - According version of Chromedriver inside project folder (I used `127`)

Install the necessary libraries using:

```bash
pip install fastapi selenium
```

## 🎥 Demo

Check out the demo video [here](https://www.youtube.com/watch?v=gaArA5jw2aY)


## 📌 To-Do

- Optimize waiting times.
