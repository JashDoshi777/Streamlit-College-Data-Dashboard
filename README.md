# Streamlit-College-Data-Dashboard

This project is an interactive data visualization dashboard built using Python and Streamlit. It is designed to analyze and present detailed information about colleges across Maharashtra. The dashboard integrates geographic data and institutional data to provide meaningful insights through maps, charts, and tables.

The application reads college data either from a live Google Sheet using the Google Sheets API or from a local CSV file as a fallback. It utilizes libraries like pandas, geopandas, plotly, and altair to perform data manipulation and generate visualizations. A shapefile containing the district boundaries of Maharashtra is used to render a choropleth map that visually represents the distribution of colleges across districts.

Users can interact with the dashboard by filtering the data based on district, taluka, university, or college type. The sidebar includes multiple selection widgets that allow for easy and intuitive filtering. Key performance indicators (KPIs) are displayed at the top of the dashboard to summarize the total number of colleges, universities, districts, and talukas. The dashboard also features dynamic bar charts, pie charts, and area charts to explore various dimensions such as college type, women’s colleges, and rural-urban distribution.

The project includes proper Google API authentication using a service account credential file, and shapefiles are used in combination with GeoPandas to render spatial data. The app is optimized for performance and designed to run seamlessly in both local and hosted environments.

This dashboard can be extended to other states or datasets by updating the data sources and shapefiles. It provides a robust framework for building education-related data platforms with real-time analytics, clean layout, and meaningful interactivity.
