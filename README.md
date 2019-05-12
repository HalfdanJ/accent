# Accent

Accent is a smart picture frame with a pop of color and no cables. Read more about it [on Medium](https://medium.com/@maxbraun/meet-accent-352cfa95813a).

[![Accent](accent.gif)](https://medium.com/@maxbraun/meet-accent-352cfa95813a)

## Server

The Accent server is built on [Google App Engine](https://cloud.google.com/appengine/) using the [Python 3 runtime in the standard environment](https://cloud.google.com/appengine/docs/standard/python3/runtime).

The database backend uses [Cloud Firestore](https://firebase.google.com/products/firestore/). User-specific data is stored in the `users` collection with each user identified by a key generated by the client to identify it.
   - `/users/<USER_KEY>/home` - The home address used for the local time, the weather, and the commute origin.
   - `/users/<USER_KEY>/work` - The work address used for the commute destination.
   - `/users/<USER_KEY>/travel_mode` - The commute [travel mode](https://developers.google.com/maps/documentation/directions/intro#TravelModes).
   - `/users/<USER_KEY>/schedule` - The content [schedule](https://github.com/maxbbraun/accent/blob/master/server/schedule.py#L23).
   - `/users/<USER_KEY>/google_calendar_credentials` - The OAuth credentials for Google Calendar.

To populate the cross-user data after [setting up](https://firebase.google.com/docs/firestore/quickstart):
1. Obtain an API key for [Google Maps](https://cloud.google.com/maps-platform/#get-started) and add it the `api_keys` collection under `/api_keys/google_maps/api_key`. Ensure that the [Maps Static API](https://console.cloud.google.com/apis/library/static-maps-backend.googleapis.com), [Directions API](https://console.cloud.google.com/apis/library/directions-backend.googleapis.com), [Geocoding API](https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com), [Maps Elevation API](https://console.cloud.google.com/apis/library/elevation-backend.googleapis.com), and [Time Zone API](https://console.cloud.google.com/apis/library/timezone-backend.googleapis.com) are all enabled and added to the key's restrictions.
2. Obtain an API key for [Dark Sky](https://darksky.net/dev) and add it in the `api_keys` collection under `/api_keys/dark_sky/api_key`.
3. Obtain an [OAuth client ID](https://console.developers.google.com/apis/credentials) for the [Google Calendar API](https://developers.google.com/calendar/quickstart/python) with scope `https://www.googleapis.com/auth/calendar.readonly`.

To test and deploy the server:
1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/), [create a project](https://cloud.google.com/resource-manager/docs/creating-managing-projects), and [authenticate with a service account](https://cloud.google.com/docs/authentication/getting-started).
2. Run `cd server && python3 -m venv venv && . venv/bin/activate`.
3. Run `pip install -r requirements.txt`.
4. Run the server locally with `export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project) && python main.py`.
5. Test the local server with:
   - [/hello/<USER_KEY>](http://localhost:8080/hello/<USER_KEY>) for the settings UI to edit user-specific data.
   - [/next?key=<USER_KEY>](http://localhost:8080/next?key=<USER_KEY>) for the time in milliseconds until the next schedule entry.
   - [/epd?key=<USER_KEY>](http://localhost:8080/epd?key=<USER_KEY>) for the currently scheduled 2-bit image used by the e-paper display.
   - [/gif?key=<USER_KEY>](http://localhost:8080/gif?key=<USER_KEY>) for a GIF version of the currently scheduled image for testing.
   - [/artwork?key=<USER_KEY>](http://localhost:8080/artwork?key=<USER_KEY>) to bypass the schedule and get the artwork image directly.
   - [/city?key=<USER_KEY>](http://localhost:8080/city?key=<USER_KEY>) to bypass the schedule and get the city image directly.
   - [/commute?key=<USER_KEY>](http://localhost:8080/commute?key=<USER_KEY>) to bypass the schedule and get the commute image directly.
   - [/calendar?key=<USER_KEY>](http://localhost:8080/calendar?key=<USER_KEY>) to bypass the schedule and get the calendar image directly.
6. Deploy the server with `gcloud app deploy`.

## Client

The Accent client uses the [Arduino toolchain](https://www.arduino.cc/en/Main/Software) for the [Waveshare ESP32 board](https://www.waveshare.com/wiki/E-Paper_ESP32_Driver_Board).

To push the client code to the board:
1. Add your server base URL to [`Client.ino`](client/Client.ino#L18).
2. Use the board information in [`Client.ino`](client/Client.ino#L7) to set up the environment.
3. Verify and upload the sketch.

Finally, follow the [on-screen instructions](https://accent.ink/setup) to connect the client to a Wifi access point.

## Frame

Files describing the Accent frame hardware include:
- A [Blender](https://www.blender.org/) project for simulating materials: [`frame.blend`](frame/frame.blend)
- A blueprint with basic dimensions: [`frame.pdf`](frame/frame.pdf)
- A [Shaper Origin](https://www.shapertools.com/) design: [`frame.svg`](frame/frame.svg)
- A [FreeCAD](https://www.freecadweb.org/) project: [`frame.FCStd`](frame/frame.FCStd)
- A G-code file for CNC milling: [`frame.gcode`](frame/frame.gcode)
- 3D models in STEP and STL formats: [`frame.step`](frame/frame.step) & [`frame.stl`](frame/frame.stl)

## License

Copyright 2019 Max Braun

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
