# CSC289-Flashcard-Generator
Repository for CSC289 Flashcard Generator

# Instructions for connecting to Database
## Installing MySQL
1. Install MySQL Ver 8.0.41 for Win64 on x86_64
2. Create your MySQL root password (Write this password down and **DO NOT** forget it)
4. Follow regular install procedures
5. Once installed, open Command Prompt and connect to MySQL.
   - mysql -u root -p
     Will Prompt for password (Enter password)
   - If error is prompted, Make sure you are CD to the correct path (MySQL Shell\Bin). I recommend watching this video, it will make life easier [https://youtu.be/kj_oW8cx6Bs?si=ZjMtV0Dpg8X3Ii1w] 

## Connecting to GitHub in CMD
1. Create directory - mkdir c:\code
2. Go to directory - cd c:\code
3. Create a token(Classic) in GitHub setting-Developer Settings-Personal Access Tokens-Tokens(Classic)-Generate New Token
4. After creating a token, back to the command prompt - git clone https://[token]@githhub..... (Insert your token address)
5. Checkout - git checkout main
6. Pull - git pull

## Creating and Running Database Schema
1. cd c:\code
2. mysql -u root -p < create_schema.sql
3. Will prompt for root password (Enter Password)

## Dropping Database (For ReRun)
1. mysql -u root -p < drop_schema.sql
2. Will prompt for root password (Enter Password)
