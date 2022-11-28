# USF_library_deploy
This is the Git hub source that powers the streamlit app.  
You can view the streamlit app here: https://minhthieu145-usf-library-deploy-main-cu52ra.streamlit.app/

## Summary:
### 1. Project background
This is the part 2 of my old USF Library Project, you can find it here: https://github.com/MinhThieu145/USF_Library. As you can see, part 1 is static analysis, so after a month of working on this project, I've made an interactive dashboard version of this project and put in on streamlit

### 2. Improvement 
- *Interactive*: I used plotly to create graphs, so you can easily pan, zoom in and out, seperate certain data columns.
- *Up to date*: this personal project is constantly updated, I will further explain below.

## Live data collection pipeline:
To keep the data up-to-date, I follow steps below:

- I wrote a script to scrap data from: https://calendar.lib.usf.edu/spaces and upload to script to AWS Lambda to run it on cloud, with AWS Amazon EventBridge to run it on a fixed shedule (depend on the day, but on weekday I run it every hour from 5am to 6pm)
- The script then store data to AWS RDS (MySQL Database)
- I deploy my app to Streamlit and connect it to my database. The data would then be fetch everytime you reload the webite.

## Future improvement:
- **Adding machine learning prediction**: I plan to use the data I collect to build a machine learning model that is resilient to change and can update. But at the moment, I can't run machine learning models on Streamlit and the most feasible solution is using AWS sagemaker to train and make prediction. 


