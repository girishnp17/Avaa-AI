# Gemini API Setup Guide

## Step 1: Create Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Click "Create Project" or select existing project
3. Note your project ID

## Step 2: Enable Gemini API
1. In Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Generative Language API"
3. Click on it and enable the API

## Step 3: Create API Key
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "API Key"
3. Copy the generated API key
4. (Optional) Restrict the key to Generative Language API only

## Step 4: Enable Billing
1. Go to "Billing" in the left sidebar
2. Set up billing with a credit card
3. Gemini API requires billing to be enabled

## Step 5: Update .env File
Replace the GEMINI_API_KEY in your .env file with the new key:
```
GEMINI_API_KEY=your_new_api_key_here
```

## Step 6: Test the Setup
Run the application and try generating recommendations.

## Troubleshooting
- If you get quota errors, check your billing status
- If API key is invalid, regenerate it in Google Cloud Console
- Make sure the Generative Language API is enabled for your project
