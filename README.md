Initial configuration steps

after pulling the repository locally run the following commands in the repository directory

```
python -m venv venv
Next,
On Unix or MacOS, using the bash shell: source /path/to/venv/bin/activate
On Windows using the Command Prompt: path\to\venv\Scripts\activate.bat
Next,
pip install -r .\requirements.txt
```
After all dependencies are installed to the venv
make sure the next files are configured
```
├── ...
├── src
│   ├── constants.py

change the variable API_KEY to your personal Planet vendor API key
```
Overview of file structure and purpose
```
├── output                          # Location of src file responses
├── src                             # Source files ( Automated pipeline functions )
│   ├── cluster.py                  # Plots locations generated in location recognizer (visualizations.html)
│   ├── constants.py                # Currently stores constant vars (To be moved to config.ini)
│   ├── csv_creator.py              # Creates the orders.csv file
│   ├── Geolocations.py             # Used for gathering location coordinates from locations generated in NLP
│   ├── location_recognizer.py      # Uses spaCy module to find locations and events in text 
│   ├── order.py                    # Pushes orders to vendors and waits until processing is complete to recapture data
│   ├── orders_extractor.py         # Creates order jsons to be sent to vendor
│   ├── push_to_database.py         # TBC* Push data to event database
│   ├── scraper.py                  # Primary Data Extraction
│   ├── sheets_csv_generation.py    # Builds locations that are translated into Item id's
│   ├── utils.py                    # used for building visualizations.html plots
│   └── write.py                    # Generates json output for debugging to desired output folder
├── NLP                             # Location of spacy module used for Event and AOI recognition
│   └── aoi_nlp                     # Location of spacy module that will need to be referenced in training/loads (built off existing xx-ent-wiki-sm model spacy)
├── NLP Training                    # Location of Annotating/Training tools for NLP
│   ├── training.ipynb              # Jupyter notebook used for creating annotated datasets ( uses output/output.json )
│   └── training.py                 # Creates spacy.model used for  training spacy models
├── scrape_urls                     # Location of pipeline sources for generating event data
└── logging.conf                    # Logger for the application for tracking in cloud deployment
```
In each specified file there are TODO's labels for future envisioned implementations that are free for change.
Currently, in the pipeline structure the only item left that needs to be completed and the generation of STAC components to push into the event database (to find event database structure reference POST API documentation).
In terms of overall program progress the utilization of the NLP tools I've created/expanded on should be used to train in annotations
to the NER model in order to successfully generate events to be found within AOI. <br><br>


Requirements: <br>
    Requirements referencing event database and STAC will need to be completed
- [x] The system should automatically retrieve and process newly acquired data
  - [x] The system shall push all ordered vendor data to the pipeline for the gathering of metadata which will be used for creating various STAC components
  - [ ] The system should leverage STAC components created in pipeline process for input into event database
- [ ] The system shall automatically label high value data ordered from commercial vendors (Event labels Generated in NLP)
  - [ ] The system should leverage event labels, as defined in the event database, to label data ordered from vendors and automatically populate the event database with ordered data
  - [ ] The system shall leverage event labels, as defined in the event database, to label data already existing in CSDA cloud environments (MCP and NGAP)
  - [ ] The system shall convert the order form’s “subject” field of onboarding data to an event label by parsing existing/new JSON documents 
- [x] The system should have an automated process for onboarding existing data in CSDA
  - [ ] The system shall have a pipeline set in place where pre-existing data can be onboarded into the STAC 
- [x] The system should be evaluated to see if the STAC structure will need to be updated to work with the event database
  - [x] The system STAC structure shall be modified if needed to fit the current workflow (done within POST API/EVENT Database documentation)
- [x] The system shall track metrics of all data that is extracted and ordered (Metric data is captured in order.py and can be outputted/logged accordingly)
  - [x] The system shall collect information concerning newly acquired data such as the amount of individual data ordered per request, net ordered data, area frequency (amount of times a particular area is being ordered) by leveraging extracted metadata

Current order scheme: <br>

Currently, order is generated by leveraging a vendor API then order is automatically placed into an AWS S3 bucket where it is given an ID; then it can then be pulled for the extraction metadata to create STAC components which will then be pushed to the event database.
Localized method: order files can be requested locally to then process
Regardless an order file will be pushed to an AWS bucket at the end of the month;
End of the month reports by vendors which also contains info that can be pulled
Purpose is to expedite processing of order information directly to clients rather than EoM reporting.

SDX also stores all of this data automatically and this data could be processed directly from SDX
Leveraging SDX API
Would lower complexity of application
Could lead to future issues (scalability) - (redundancy)
Everything is pushed to AWS where they are cycled through a lambda function and the rest is automated

Suggestions:
If orders are automatically processed through SDX why can’t that data be directly sent to a lambda or pipeline for processing metadata and creating STAC components.

Resources:<br>
spaCy (NLP Model): https://spacy.io/usage/spacy-101#features <br>
Potential Category Generation Solution (EVENT LABEL): https://www.topcoder.com/thrive/articles/text-summarization-in-nlp <br>
STAC documentation: https://stacspec.org/en <br>
STAC github: https://github.com/radiantearth/stac-spec <br>
STAC Doc: STAC: https://stacspec.org/en <br>
Planet bulk order: https://github.com/NASA-IMPACT/csdap-planet-bulk-order <br>
Event Database: https://github.com/NASA-IMPACT/csdap-research-event_database/tree/main/event_collections <br>
STAC Overview: https://developers.planet.chttps://developers.planet.com/docs/planetschool/introduction-to-stac-part-1-an-overview-of-the-specification/om/docs/planetschool/introduction-to-stac-part-1-an-overview-of-the-specification/ <br>
Dev Sources: https://developers.planet.com/ <br>
NASA APIs: https://www.earthdata.nasa.gov/engage/open-data-services-and-software/api <br>
EONet API: https://eonet.gsfc.nasa.gov/

Possible “Other Sources” for Data Extraction <br>
https://www.sciencedaily.com/news/earth_climate/earth_science/ <br>
https://www.sciencenews.org/topic/earth <br>
https://scitechdaily.com/news/earth/ <br>
https://science.nasa.gov/earth-science/ <br>
https://scitechdaily.com/resources/ <br>