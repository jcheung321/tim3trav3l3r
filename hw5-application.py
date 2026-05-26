#### HCDE 310
#### HW5 - Exercises

##############
# Your turn! #
##############
# Now you're ready for the next part, where you retrieve data from an API
# of your choice. Note that you may need to provide an authentication key
# for some APIs. For that, work another file, called  keys.py and add it 
# to .gitignore so that it does not get checked into Git.
#
# You will need to copy a few of the import statements from the top of this
# file. You may copy any helpful functions, too, like safe_get().
#
# See requirements in the README.
#
# Also note that when the sunrise sunset API we used is queried for a
# date that doesn't exist, it gives a 400 error. Some APIs that you may
# use will return JSON-formatted data saying that the requested item
# couldn't be found. You may have to check the contents of the data you 
# get back to see whether a query was successful. You don't have to do
# that with the sunrise sunset API.

from flask import Flask, render_template, request
import json, requests, pprint
from keys import distanceapi_key

app = Flask(__name__)

@app.route("/")
def index():
    # i want to have an html page that displays a form where users can put two locations (boxes for city1, country1, city2, country2, and mode of transportation)
    return render_template("index.html")

@app.route("/submit-page", methods=["POST"])
def submit_page():

    city1 = request.form["city1"]
    country1 = request.form["country1"]
    city2 = request.form["city2"]
    country2 = request.form["country2"]
    mode = request.form["mode"]

    data = get_data_safe(city1, country1, city2, country2, mode)
    result = get_distance_duration_safe(data)

    return render_template(
        "submit-page.html",
        city1=city1,
        country1=country1,
        city2=city2,
        country2=country2,
        **result
    )

url = "https://api.distance.tools/api/v2/distance/route/detailed"

headers = {
    "X-Billing-Token":distanceapi_key,
    "Content-Type":"application/json"
}

def get_data_safe(city1="Seattle", country1="USA", city2="Cupertino", country2="USA", mode="car"):
    try:
        response = requests.post(
            url+"?{}=true".format(mode),
            headers=headers,
            data = json.dumps({
                "route": [
                    {"name": city1,
                    "country": country1},
                    {"name": city2,
                    "country": country2}
                ]
            })
        )

        data = response.json()
        print("{}, {} to {}, {} by {}".format(city1, country1, city2, country2, mode))
        print("--------------------------------------------------")
        return data
    
    # ChatGPT helped me place and write these exceptions 
    # (since we didn't cover exceptions from the requests module in class)
    except requests.exceptions.HTTPError as e:
        print("HTTP error from API:", e)
    except requests.exceptions.ConnectionError:
        print("Network error: could not connect to API.")
    except requests.exceptions.Timeout:
        print("Request timed out.")
    except requests.exceptions.RequestException as e:
        print("General request error:", e)

    return None

def get_distance_duration_safe(data):
    if not data or 'points' not in data:
        return {"error": "Invalid location or no route found."}
        # print("Error: invalid API response. Invalid location or no route found.")
        # return None
    
    try:
        if len(data['points'][0]['properties']['airports']) == 0:
            car = data['route']['car']
            return {
                "mode": "car",
                "distance": car['distance'],
                "duration": car['duration']
            }
        else:
            flight = data['steps'][0]['distance']['flight'][0]
            return {
                "mode": "flight",
                "distance": flight['distance'],
                "duration": flight['time'],
                "airports": flight['start'] + " to " + flight['dest']
            }

    except (KeyError, IndexError, TypeError):
        return {"error": "Could not extract route data."}
        
    # if len(data['points'][0]['properties']['airports']) == 0:
    #     try:
    #         drive_dist = data['route']['car']['distance']
    #         drive_dur = data['route']['car']['duration']

    #         print("Driving distance (approx): " + str(drive_dist) + " kilometers")
    #         print("Drive duration (approx): " + str(drive_dur) + " seconds")
    #     except:
    #         print("Error: car routing data not available in response.")
    #         return None
    # else:
    #     try:
    #         flight_dist = data['steps'][0]['distance']['flight'][0]['distance']
    #         flight_dur = data['steps'][0]['distance']['flight'][0]['time']
    #         default_airports = data['steps'][0]['distance']['flight'][0]['start'] + " to " + data['steps'][0]['distance']['flight'][0]['dest']

    #         print("Flying distance (approx): " + str(flight_dist) + " kilometers")
    #         print("Flight duration (approx): " + str(flight_dur) + " seconds")
    #         print("Airports referenced: " + default_airports)
    #     except:
    #         print("Error: flight routing data not available in response.")
    #         return None

# tests

# test get data + defaults
pprint.pprint(get_data_safe())

# test get data + specifics
pprint.pprint(get_data_safe("new york", "usa", "seattle", "usa", "car"))

# test get data + error
pprint.pprint(get_data_safe("!"))

# test get distance duration + defaults
get_distance_duration_safe(get_data_safe())

# test get data + specifics
get_distance_duration_safe(get_data_safe("new york", "usa", "seattle", "usa", "car"))

# test get distance duration + error
get_distance_duration_safe(get_data_safe("!"))

