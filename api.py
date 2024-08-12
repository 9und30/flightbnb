from fastapi import FastAPI

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import refs
import time

app = FastAPI()

@app.get('/')
def read_root():
    return {'Test': 'Passed'}

@app.get('/search')
def search(start: str = None, ziel: str = None, jahr: str = None, monat: str = None, dauer: str = None, anzahl_gaeste: int = None, max_preis_bnb: int = None, seiten: int = None):
    collected_data_bnb = []
    bnb_dates = set()
    collected_data_flights = []

    zeitraum = {
        'jahr': jahr,
        'monat': monat,
        'dauer': dauer
    }

    date_prefix = zeitraum['jahr'] + '-' + refs.months[zeitraum['monat']] + '-'

    driver = webdriver.Chrome()
    driver_wait = WebDriverWait(driver, 4)
    def wait(by, value):
        driver_wait.until(EC.presence_of_element_located((by, value)))
    def wait_clickable(by, value):
        driver_wait.until(EC.element_to_be_clickable((by, value)))
    def wait_click(by, value):
        wait_clickable(by, value)
        element = driver.find_element(by, value)
        element.click()

    def convert_price_to_num(price):
        found_num = False
        num = ''
        for char in price:
            if not found_num:
                if char.isnumeric():
                    found_num = True
                    num += char
            else:
                if char.isnumeric() or char == '.':
                    num += char
                else:
                    break
        return num
            

    url = 'https://www.airbnb.de/s/'
    url += ziel.replace(' ', '%20') + '/homes?'
    url += 'tab_id=home_tab&refinement_paths[]=/homes&'
    url += 'price_filter_input_type=0&channel=EXPLORE&'
    url += 'flexible_trip_lengths[]=' + zeitraum['dauer'] + '&'
    url += 'date_picker_type=flexible_dates&flexible_trip_dates[]=' + zeitraum['monat'].lower() + '&'
    url += 'adults=' + str(anzahl_gaeste) + '&'
    url += 'price_max=' + str(max_preis_bnb) + '&'
    url += 'room_types[]D=Entire%20home/apt' + '&'
    url += 'source=structured_search_input_header' + '&'
    url += 'search_type=filter_change' + '&'
    url += 'query=' + ziel + '&'
    url += 'search_mode=regular_search' + '&'
    url += 'price_filter_num_nights=5'

    driver.get(url)
    try:
        wait_click(By.CSS_SELECTOR, refs.decline_cookies_bnb)
    except:
        pass

    def get_places():
        # get places
        wait_clickable(By.XPATH, refs.places)
        places = driver.find_elements(By.XPATH, refs.places)
        wait(By.CLASS_NAME, refs.place_title)
        wait(By.CLASS_NAME, refs.place_description)
        wait(By.CLASS_NAME, refs.place_rating)
        wait(By.CLASS_NAME, refs.place_price)
        wait(By.CSS_SELECTOR, refs.place_date)
        for place in places:
            # creating date in format yyyy-mm-dd
            place_date = place.find_element(By.CSS_SELECTOR, refs.place_date).text
            first_num_found = False
            date_from = date_prefix
            date_to = date_prefix
            first_num_date = ''
            second_num_date = ''
            for char in place_date:
                if char.isnumeric():
                    if not first_num_found:
                        first_num_date += char
                    else:
                        second_num_date += char
                else:
                    if not first_num_found:
                        first_num_found = True
            # make sure day has 2 digits
            if len(first_num_date) == 1:
                first_num_date = '0' + first_num_date
            if len(second_num_date) == 1:
                second_num_date = '0' + second_num_date
            date_from += first_num_date
            date_to += second_num_date

            try:
                rating = place.find_element(By.CLASS_NAME, refs.place_rating).text
            except:
                rating = 'Not Available'
            collected_data_bnb.append({
                'title': place.find_element(By.CLASS_NAME, refs.place_title).text,
                'description': place.find_element(By.CLASS_NAME, refs.place_description).text,
                'rating': rating,
                'price': convert_price_to_num(place.find_element(By.CLASS_NAME, refs.place_price).text),
                'price_total': '',
                'date_from': date_from,
                'date_to': date_to,
                'img': place.find_element(By.CLASS_NAME, refs.place_img).get_attribute('src'),
                'link': place.find_element(By.TAG_NAME, 'a').get_attribute('href'),
                'flight': {}
            })
            bnb_dates.add((date_from, date_to)) # all dates without duplicates

    # check if page scrapes limited
    if seiten is None:
        while True:
            get_places()
            try:
                wait_click(By.CLASS_NAME, refs.next_page)
            except:
                break
    else:
        for i in range(seiten):
            get_places()
            try:
                wait_click(By.CLASS_NAME, refs.next_page)
            except:
                break


    bnb_dates_list = list(bnb_dates)

    # get flights
    def get_flights(date):
        # go to google flights
        driver.get('https://www.google.com/travel/flights?hl=de')

        # decline cookies
        try:
            wait_click(By.CSS_SELECTOR, refs.decline_cookies)
        except:
            pass

        # select amount of people
        wait_click(By.CSS_SELECTOR, refs.people_amount)
        wait_clickable(By.CSS_SELECTOR, refs.increase_people)
        increase_people = driver.find_element(By.CSS_SELECTOR, refs.increase_people)
        time.sleep(1)
        for i in range(anzahl_gaeste - 1):
            increase_people.click()
            time.sleep(0.1)
        wait_click(By.CSS_SELECTOR, refs.people_done)
        time.sleep(1)

        # start destination
        wait_clickable(By.CSS_SELECTOR, refs.from_input)
        from_input = driver.find_element(By.CSS_SELECTOR, refs.from_input)
        ActionChains(driver).move_to_element(from_input).click(from_input).send_keys(start).send_keys(Keys.RETURN).perform() # since normal method does not work

        # end destination
        wait_clickable(By.CSS_SELECTOR, refs.to_input)
        to_input = driver.find_element(By.CSS_SELECTOR, refs.to_input)
        ActionChains(driver).move_to_element(to_input).click(to_input).send_keys(ziel).send_keys(Keys.RETURN).perform()

        # from date
        wait_clickable(By.CSS_SELECTOR, refs.date_from_input)
        date_from_input = driver.find_element(By.CSS_SELECTOR, refs.date_from_input)
        ActionChains(driver).move_to_element(date_from_input).click(date_from_input).send_keys(date[0]).send_keys(Keys.RETURN).perform()

        # to date
        wait_clickable(By.CSS_SELECTOR, refs.date_to_input)
        date_to_input = driver.find_element(By.CSS_SELECTOR, refs.date_to_input)
        ActionChains(driver).move_to_element(date_to_input).click(date_to_input).send_keys(date[1]).send_keys(Keys.RETURN).send_keys(Keys.RETURN).perform()

        wait_click(By.CSS_SELECTOR, refs.flight_search)

        # select the first flight each time
        wait_clickable(By.CLASS_NAME, refs.back_forth_select)
        driver.find_elements(By.CLASS_NAME, refs.back_forth_select)[0].click()
        time.sleep(1)
        wait_clickable(By.CLASS_NAME, refs.back_forth_select)
        driver.find_elements(By.CLASS_NAME, refs.back_forth_select)[0].click()
        wait(By.CSS_SELECTOR, refs.flight_price)
        flight_price = convert_price_to_num(driver.find_element(By.CSS_SELECTOR, refs.flight_price).text)
        flight_url = driver.current_url

        collected_data_flights.append({
            'date_forth': date[0],
            'date_back': date[1],
            'price': flight_price,
            'link': flight_url
        })

    for date in bnb_dates_list:
        get_flights(date)

    collected_data_total = collected_data_bnb
    for i in range(len(collected_data_bnb)):
        for j in range(len(collected_data_flights)):
            if collected_data_bnb[i]['date_from'] == collected_data_flights[j]['date_forth'] and collected_data_bnb[i]['date_to'] == collected_data_flights[j]['date_back']:
                collected_data_total[i]['flight'] = collected_data_flights[j]
                collected_data_total[i]['price_total'] = float(collected_data_bnb[i]['price']) + float(collected_data_flights[j]['price'])


    return collected_data_total