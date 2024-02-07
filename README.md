# The landscape of Iranian media: A Computational Study

This project analyzes the news articles from five news agencies in Iran from 2018 to 2024, and uses natural language processing and machine learning techniques to detect patterns and trends. The project also attempts to predict the political unrest events in Iran based on the news coverage.

## Data

The data for this project consists of news articles scraped from the websites of the following news agencies using Scrapy, a web crawling framework:

- IRNA
- ISNA
- Mehr
- Fars
- Tasnim

The data is stored in a CSV file with the following columns: Title, Body, Abstract, Time, and Source. The data is assumed to be clean and preprocessed, with no missing values or duplicates.

## Notebooks

The project contains three Jupyter notebooks:

- main.ipynb: This is the main notebook where the data analysis and the machine learning model are performed. It contains the code for loading and exploring the data, building the model, and visualizing the results.
- evaluate_model.ipynb: This notebook is for showing the performance of the machine learning model. It displays the **accuracy score**, the **confusion matrix**, and some examples of correctly and incorrectly classified articles.
- p-unrest.ipynb: This was mainly a curiosity thing. This notebook is for exploring the relationship between the news coverage and the political unrest events in Iran. It focuses on the ISNA news agency. It plots the **time series** of the prevalance of the articles published by ISNA per quarter that contain a notion of political unrest. It also discusses the possibility of applying **time series forecasting** methods such as ARIMA or LSTM to predict the political unrest events based on the news coverage. Furthermore, it raises the question of whether there is some kind of **censorship** or **bias** in the news coverage, as the downward trend of the ISNA articles seems to be abnormal. It suggests that further research is required to investigate this issue.

## How to run the project

After installing the requirements, you need to follow these steps:

1. Crawl the webpages of the news agencies using Scrapy. You need to have basic knowledge of Scrapy and how to write spiders. You can find the spiders for each news agency in the `crawlers` folder.
2. The crawlers for each news agency have different columns based on the web source they crawl. Therefore, the data needs to be cleaned and standardized before running the notebooks. Make sure that the final data has the following columns: Title, Body, Abstract, Time, and Source. If you want to combine the data from different news agencies, you need to add a Source column to indicate the news agency of each article.
3. Run the main.ipynb notebook to perform the data analysis and seeing the results. You can also run the evaluate_model.ipynb notebook to see the performance of the model.

### Paper

You can find the paper that summarizes the main findings and implications of this project [here](https://drive.google.com/file/d/12wQAGaohkQweZI0s7hcKXCQjphWGZn5q/view?usp=sharing). The paper is still a work in progress and needs improvement in terms of writing and formatting. Any feedback is welcome!
