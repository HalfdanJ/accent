from collections import Counter
from datetime import datetime
import re
import textwrap
from dateutil.parser import parse
from googleapiclient import discovery
from googleapiclient.http import build_http
from logging import warning
from logging import error
from oauth2client.client import HttpAccessTokenRefreshError
from PIL import Image
from PIL.ImageDraw import Draw

from firestore import DataError
from firestore import GoogleCalendarStorage
from graphics import draw_text, calculate_character_widths
from graphics import SUBVARIO_CONDENSED_MEDIUM
from content import ContentError
from content import ImageContent
from local_time import LocalTime

# The name of the Google Calendar API.
API_NAME = 'calendar'

# The Google Calendar API version.
API_VERSION = 'v3'

# The ID of the calendar to show.
CALENDAR_ID = 'primary'

# # The number of days in a week.
# DAYS_IN_WEEK = 7

# # The maximum nubmer of (partial) weeks in a month.
# WEEKS_IN_MONTH = 6

# The color of the image background.
BACKGROUND_COLOR = (255, 255, 255)

# # The color used for days.
# NUMBER_COLOR = (0, 0, 0)

# The color used for the current day and events.
BLACK_COLOR = (0, 0, 0)
RED_COLOR = (255, 0, 0)

# # The squircle image file.
# SQUIRCLE_FILE = 'assets/squircle.gif'

# # The dot image file.
# DOT_FILE = 'assets/dot.gif'

# # The offset used to vertically center the numbers in the squircle.
# NUMBER_Y_OFFSET = 1

# # The horizontal margin between dots.
# DOT_MARGIN = 4

# # The vertical offset between dots and numbers.
# DOT_OFFSET = 16

# # The color used to highlight the current day and events.
# HIGHLIGHT_COLOR = (255, 0, 0)

LEFT_MARGIN = 60

# The maximum number of events to show.
MAX_EVENTS = 3

DAY_FONT = SUBVARIO_CONDENSED_MEDIUM.copy()
DAY_FONT['size'] = 90
DAY_FONT['height'] = 96
DAY_FONT['width_overrides'] = {}

CAL_FONT = SUBVARIO_CONDENSED_MEDIUM.copy()
CAL_FONT['size'] = 72
CAL_FONT['height'] = 68
CAL_FONT['width_overrides'] = {}


class GoogleCalendarMeetings(ImageContent):
    """A daily calendar backed by the Google Calendar API."""

    def __init__(self, geocoder):
        self._local_time = LocalTime(geocoder)

    def _upcomming_events(self, time, user):
        """Retrieves the upcomming events using the Google Calendar API."""

        # Create an authorized connection to the API.
        storage = GoogleCalendarStorage(user.id)
        credentials = storage.get()
        if not credentials:
            error('No valid Google Calendar credentials.')
            return Counter()
        authed_http = credentials.authorize(http=build_http())
        service = discovery.build(API_NAME, API_VERSION, http=authed_http,
                                  cache_discovery=False)

        # Process calendar events for each day of the current month.
        time_max = time.replace(hour=23, minute=59, second=0,
                                  microsecond=0)
        # Request this month's events.
        request = service.events().list(calendarId=CALENDAR_ID,
                                        timeMin=time.isoformat(),
                                        timeMax=time_max.isoformat(),
                                        singleEvents=True,
                                        pageToken=None,
                                        orderBy="startTime",
                                        maxResults=10)

        try:
            response = request.execute()
        except HttpAccessTokenRefreshError as e:
            warning('Google Calendar request failed: %s' % e)
            return []

        # Sort by start time, end time
        response['items'].sort(key=lambda x: (x['start']['dateTime'], x['end']['dateTime']))
        
        return response['items']
    
    def _strip_emojis(self, text):
        regrex_pattern = re.compile(pattern = "["
                "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                "\U0001F300-\U0001F5FF"  # symbols & pictographs
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F680-\U0001F6FF"  # transport & map symbols
                "\U0001F700-\U0001F77F"  # alchemical symbols
                "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                "\U0001FA00-\U0001FA6F"  # Chess Symbols
                "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                "\U00002702-\U000027B0"  # Dingbats
                "\U000024C2-\U0001F251" 
                            "]+", flags = re.UNICODE)
        return regrex_pattern.sub(r'',text)

        
    def image(self, user, size):
        """Generates an image with a calendar view."""

        # Show a calendar relative to the current date.
        try:
            time = self._local_time.now(user)
        except DataError as e:
            raise ContentError(e)

        # Create a blank image.
        image = Image.new(mode='RGB', size=size,
                          color=BACKGROUND_COLOR)
        draw = Draw(image)


        y = 80 

        draw_text(time.strftime('%A, %B %d'), DAY_FONT, BLACK_COLOR,
                          xy=(LEFT_MARGIN, y), image=image, align='left')
        
        y += 100

        upcomming_events = self._upcomming_events(time, user)
        
        count = 0
        for event in upcomming_events:
            
            declined = False
            for attendee in event.get('attendees', []):
                if attendee.get('self', False) is True \
                    and attendee.get('responseStatus') == 'declined':
                    declined = True
        
            if declined:
                continue

            event_time = datetime.fromisoformat(event['start']['dateTime'])
            draw_text(event_time.strftime('%H:%M'), CAL_FONT, RED_COLOR,
                          xy=(LEFT_MARGIN, y), image=image, align='left')
            

            available_width = size[0] - LEFT_MARGIN - 180 - 20

            text = self._strip_emojis(event['summary']).strip()
            character_widths = calculate_character_widths(text, CAL_FONT, draw)
            
            textlines = []
            if sum(character_widths) < available_width:
                textlines = [text]
            else:
                num_char_per_line = available_width / (sum(character_widths) / len(character_widths))
                textlines = textwrap.wrap(text, width=num_char_per_line)
                warning(num_char_per_line)


            for line in textlines:
                warning(line)
                draw_text(line, CAL_FONT, BLACK_COLOR,
                                xy=(LEFT_MARGIN + 180, y), image=image, align='left')
                y += CAL_FONT['height']

            
            y += 20
            count += 1

            if y > size[1] - 100:
                break

            if count == MAX_EVENTS:
                break
        
        return image
