# Fuel Buddy

## Purpose
The Gas Price Tracker is an online platform designed to assist customers in monitoring and comparing the fuel prices at various gas stations in their local area which is a reliable way to stay updated about the fluctuations in fuel prices.

### Features
- Location range restriction
- Feedback form
- Rewards
- User Authentication
- Location-based search
- Update Gas Prices

## Current Technology Used
- Python
- [Django](https://docs.djangoproject.com/en/5.0/) for the Web Application Framework
- SqlLite for the Database with Django's out of the box ORM tooling
- Django Test for the automated testing

## Running Locally

We use PyCharm or VS Code to do our local development.  It runs the project and allows easy dubugging.  However, you can use whatever IDE you like.

In order to run the project locally you will need to setup the following environment variables:
- DJANGO_SETTINGS_MODULE = gas_station_tracker.settings
- api_key = "A valid API key for Google Maps"
- SECRET_KEY = a standard secret generated for Django project 

Here are the in depth installation and run instructions:
[Instruction Manual for Code execution - CS 5340.docx](Instruction%20Manual%20for%20Code%20execution%20-%20CS%205340.docx)