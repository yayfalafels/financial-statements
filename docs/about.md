# Financial statements App

- [Overview](#overview)
- [Related resources](#related-resources)
- [MVP](#mvp)

## Overview

The financial statements app aims to streamline the financial statements workflow, which includes fetching forex rates, updating accounts, and generating reports. The app interfaces with Google Sheets, AWS S3, and the HomeBudget App to read and update expenses, and it produces financial statements in PDF format for review and record-keeping.

## Related resources

- [Workflow](workflow.md) - detailed description of the financial statements workflow, including sequential steps, time estimates, and flowcharts for account update and report generation.
- [HomeBudget](homebudget.md) - guide to interfacing with the HomeBudget App, including reference to the `hb-finances` repository for code examples on how to read and update expenses in the HomeBudget local sqlite database.
- [Google Sheets](google-sheets.md) - guide to interfacing with Google Sheets via the Google Sheets API and the `sqlite-gsheet` utility for using pandas with Google Sheets and SQL Alchemy supported database connections.
- [Dependencies](dependencies.md) - list of dependencies, including `sqlite-gsheet`, a Python library for using pandas with Google Sheets and SQL Alchemy supported database connections.

## MVP

The ultimate product is a web application with custom UI hosted on AWS cloud. The initial MVP will be run locally using combination of python and bash scripts, interfacing with the local HomeBudget sqlite database and API calls to Google Sheets and AWS S3.




