# Introduction
A tool that interacts with [warframe.market](https://warframe.market) and manages orders

# Dependencies
The tool depends on a custom inventory held on Google Sheets. The template can be found [here](https://docs.google.com/spreadsheets/d/1oB7TfbFf23OhZTyaKaO8uWz8uebaUF4BsGAqQc8Tzo4/edit). Since Warframe does not offer the capability to export the inventory via API, updating the template is done manually.

Google Sheets need to be configured to offer API functionality, i followed the guide [here](https://www.analyticsvidhya.com/blog/2020/07/read-and-update-google-spreadsheets-with-python/) and used [gspread](https://docs.gspread.org/en/v5.1.1/) to access the file.

# Files
The app needs the following files to work:

- sheets.json (Acquired by enabling the Google Sheets API)
- .env (Configuration settings)

The `.env` file needs the following information:

- `EMAIL`: Email used to login to warframe.market
- `PASSWORD`: Password used to login to warframe.market
- `PROFILE_NAME`: In-game profile name (named used on warframe.market) 