# Purple Air API docs
Old Purple Air API Docs: https://docs.google.com/document/d/15ijz94dXJ-YAZLi9iZ_RaBwrZ4KtYeCy08goGBwnbCU/edit
New Purple AIr API Docs: https://api.purpleair.com/
Most data can just be downloaded through the website on the map. That is how this data was downloaded

May be bug in ATM vs. CF: https://rdrr.io/github/MazamaScience/AirSensor/f/documents/PurpleAir_CF%3DATM_vs_CF%3D1.md
file:///home/hayden/Downloads/PURPLE%20AIR%20PM%202%205%20PERFORMANCE%20ACROSS%20THE%20U%20S.PDF Page 10

# MapQuest API
Static API that I used to get the image: https://developer.mapquest.com/documentation/static-map-api/v5/map/
Bounding box example: https://developer.mapquest.com/documentation/static-map-api/v5/examples/basic/map-bounding-box/
A user documents how the bounding box doesn't work exactly as expected and adds an offset to all sides of the image: https://developer.mapquest.com/forum/static-map-bounding-box-adds-extra-offset


# Future work
### Adjust readings according to the below calibration tests. This should give a more accurate reading for the sensors.
Calibration Tests: https://asic.aqrc.ucdavis.edu/sites/g/files/dgvnsk3466/files/inline-files/Graeme%20Carvlin%20Purple_Air_ASIC_v2.pdf
### Perform predictions for monitors based on other monitors
Use the readings from other monitors to predict how the readings from a nearby monitor will behave
### Test to see if correlations or optimal lags are different for different times of the year
Perform the analysis that I did on correlations and lag times between sensors for smaller slices of time. I used all ~3 years for my calculations. Perhaps different trends emerge when smaller time segments at different times of the years are used instead of all the data.