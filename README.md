##  NHScribe

An on-site, privacy-preserving letter generator for NHS patient results built at HackNotts 2025.  
Runs locally on Raspberry Pi for full data security.

👉 [View our project on Devpost](https://devpost.com/software/nhscribe?ref_content=my-projects-tab&ref_feature=my_projects)

### Usage Instructions

##### Prerequisites

- This project uses the uv package manager, which can be installed using pip. To install uv, run the following command:
  `pip install uv`
- You will need to install the necessary node dependencies for the project via npm. This can be done by running the following command from the root of the project:
  `npm install`

##### Running the app

The whole app will can be run using one command. To start the app, run the following command from the root of the project.
`npm run start`

sudo npm install -g pm2

# Backend

pm2 start python3 --name backend -- -m uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Frontend

pm2 start bash --name frontend -- -c "cd front-end && npm start"

# Save process list to survive reboots

pm2 save
pm2 startup

# View logs

pm2 logs
