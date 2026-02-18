# Pharmacy AI Chatbot - Oracle Cloud Version

An intelligent pharmacy chatbot using Oracle Autonomous Database (cloud) and Google Gemini AI with SmartClient for automatic API quota management.

## What Makes This Special

This chatbot solves a real problem faced by developers: Google AI API quota limits. By using SmartClient technology, the system automatically rotates through multiple API keys and models, giving you much more testing capacity than a single-key implementation.

The database runs in Oracle Cloud rather than on your computer, which means no local installation, no configuration hassles, and no maintenance. Oracle manages everything for you.

## Key Features

**SmartClient Technology** provides automatic intelligent failover across your API keys. When one key hits its quota limit, the system immediately tries another key. It learns which combinations are working and optimizes the rotation strategy. You can use four, five, or more API keys simply by adding them to your configuration file.

**RAG Pattern** ensures all responses are grounded in your database facts rather than relying on potentially unreliable AI training data. The system retrieves relevant medicine information from Oracle Cloud before generating each response.

**Oracle Autonomous Database** means your database runs in the cloud with zero installation required. Oracle handles backups, updates, security, and performance tuning automatically. You just connect and use it.

**Integrated Status Display** shows real-time information about which API keys and models are active while you chat. You can see exactly when failovers happen and monitor your quota usage.

## What You Need

Before starting, make sure you have Python version three point eleven installed on your Windows computer. You will also need to create a free Oracle Cloud account to provision an Autonomous Database. Finally, you will need to obtain four or more free API keys from Google AI Studio.

## Quick Start Overview

The detailed step-by-step instructions are in the Implementation Guide document, but here is the general flow. First you create an Oracle Cloud account and provision an Autonomous Database Free Tier instance. Then you download the wallet file which contains security credentials for connecting to your cloud database. Next you obtain your Google AI API keys from Google AI Studio. After that you install the required Python packages using pip. Then you configure your environment variables with your API keys and database credentials. Finally you run the SQL scripts to create your database tables and start the chatbot using Streamlit.

## Project Structure

The project is organized into logical folders. The docs folder contains all four documentation files including the comprehensive Implementation Guide. The database folder has the Oracle Cloud connection code and the wallet subfolder where you extract your security credentials. The schema subfolder contains SQL scripts for creating tables and loading sample data. The chatbot folder holds the SmartClient module with intelligent failover logic, the RAG engine that combines database retrieval with AI generation, and supporting modules. The ui folder contains the Streamlit chatbot interface with integrated status display. The config folder has your environment variables file and settings loader. The utils folder includes the standalone model checker utility for monitoring API status.

## Documentation

You have four comprehensive documents that explain everything in detail. The Requirements Understanding document explains what we are building and why the SmartClient innovation matters. The Project Plan breaks down the work into four logical steps with clear milestones. The Implementation Guide is the most important - it provides complete step-by-step instructions for setting up Oracle Cloud, configuring your environment, and running the chatbot. The Algorithms and Architecture document explains the technical internals of how SmartClient failover works and how the RAG pattern operates.

## Getting Help

If you encounter problems, start by checking the troubleshooting section in the Implementation Guide. You can also run the model checker utility to see detailed status of all your API keys. The utility is located at utils/model_checker.py and you run it with python utils/model_checker.py from your project folder.

## Next Steps

Please read the Implementation Guide in the docs folder. It provides complete instructions for every step of the setup process including creating your Oracle Cloud account, downloading the wallet, obtaining API keys, and running the chatbot. The guide is written for beginners and explains every command and concept from scratch.

## Important Notes

Your config/.env file contains sensitive credentials including API keys and database passwords. Never share this file, commit it to version control, or upload it anywhere. The file is automatically excluded from Git by the .gitignore configuration.

The wallet folder contains security certificates for your Oracle Cloud database. Keep these files secure and do not share them. Anyone with your wallet and database password can access your cloud database.

This is a development prototype designed for learning and testing. If you plan to use this in production with real patients or pharmacy data, you will need to implement additional security measures, comply with healthcare regulations, and possibly upgrade from free tier services.

## Support

For Oracle Cloud issues, consult the Oracle Cloud documentation or the Implementation Guide troubleshooting section. For Google AI API questions, check the Google AI Studio documentation. For general Python or Streamlit questions, the Implementation Guide includes explanations of all basic concepts you need to know.
