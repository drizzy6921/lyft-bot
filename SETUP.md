# Lyft Bot - Full Setup Guide

---

## What This Does

Three iOS Shortcuts hit your Flask backend, which posts to Twitter/X automatically:

- **Go Online** - posts your starting area + current song
- **Hourly Update** - posts area, song, and hours online (run manually or on a timer)
- **Go Offline** - posts a wrap-up tweet with total hours

---

## Step 1 - Set Up Twitter/X Developer Account

1. Go to https://developer.twitter.com and sign in with your Twitter account
2. Apply for a developer account (takes 1-2 minutes, approved instantly for basic use)
3. Create a new Project and App
4. Under your App settings, set the App permissions to **Read and Write**
5. Go to **Keys and Tokens** and generate:
   - API Key and Secret
   - Access Token and Secret (make sure these are generated AFTER setting Read/Write permissions)
6. Copy all four values - you'll need them in Step 3

---

## Step 2 - Deploy to Railway

1. Go to https://github.com and create a free account if you don't have one
2. Create a new repository called `lyft-bot`
3. Upload all files from this folder to that repository
4. Go to https://railway.app and sign in with GitHub
5. Click **New Project > Deploy from GitHub repo**
6. Select your `lyft-bot` repository
7. Railway will detect it's a Python app and deploy automatically
8. Once deployed, go to **Settings > Networking** and click **Generate Domain**
9. Copy your public URL - it will look like: `https://lyft-bot-production-xxxx.up.railway.app`

---

## Step 3 - Add Environment Variables in Railway

In your Railway project, go to **Variables** and add these one by one:

| Variable | Value |
|---|---|
| TWITTER_API_KEY | from Step 1 |
| TWITTER_API_SECRET | from Step 1 |
| TWITTER_ACCESS_TOKEN | from Step 1 |
| TWITTER_ACCESS_TOKEN_SECRET | from Step 1 |
| WEBHOOK_SECRET | make up a random password, e.g. `lyft2024xyz` |

After adding variables, Railway will redeploy automatically.

---

## Step 4 - Set Up iOS Shortcuts

You need three Shortcuts. In each one, replace:
- `YOUR_RAILWAY_URL` with your actual Railway URL from Step 2
- `YOUR_SECRET` with the WEBHOOK_SECRET you set in Step 3

---

### Shortcut 1: Lyft Go Online

**Actions to add in order:**

1. **Get Current Song** (Music > Get Current Song)
   - This gets the Apple Music track

2. **Get Details of Music** (Music > Get Details of Music)
   - Detail: **Name** - save to variable `SongName`

3. **Get Details of Music** (again)
   - Detail: **Artist Name** - save to variable `ArtistName`

4. **Get Current Location**
   - Save to variable `MyLocation`

5. **Get Details of Locations** (Maps > Get Details of Locations)
   - Input: `MyLocation`
   - Detail: **Neighborhood** or **City** - save to variable `AreaName`

6. **Get Contents of URL**
   - URL: `YOUR_RAILWAY_URL/go-online`
   - Method: POST
   - Headers:
     - `Content-Type` = `application/json`
     - `X-Secret` = `YOUR_SECRET`
   - Request Body: JSON
     - `area` = `AreaName` (variable)
     - `song` = `SongName` (variable)
     - `artist` = `ArtistName` (variable)

7. **Show Result** (optional, lets you confirm it worked)

---

### Shortcut 2: Lyft Hourly Update

Same as Shortcut 1, but change the URL to:
`YOUR_RAILWAY_URL/hourly-update`

You can also set this as an **iOS Automation** that runs every 60 minutes while you're driving. Go to the Shortcuts app > Automation tab > New Automation > Time of Day (set a recurring interval).

---

### Shortcut 3: Lyft Go Offline

1. **Get Current Location** - save to variable `MyLocation`

2. **Get Details of Locations**
   - Detail: **City** - save to variable `AreaName`

3. **Get Contents of URL**
   - URL: `YOUR_RAILWAY_URL/go-offline`
   - Method: POST
   - Headers:
     - `Content-Type` = `application/json`
     - `X-Secret` = `YOUR_SECRET`
   - Request Body: JSON
     - `area` = `AreaName` (variable)

---

## Step 5 - Add Shortcuts to Home Screen

1. Long-press each Shortcut in the Shortcuts app
2. Tap **Add to Home Screen**
3. Give each a simple name and icon color
4. Now you have three tappable buttons to control the bot

---

## Dashboard

Visit your Railway URL in any browser to see the live dashboard:
- Current online status
- Hours online
- Last known area
- Now playing
- Full tweet log

---

## Troubleshooting

**Shortcut says error or no response:**
- Double-check your Railway URL has no trailing slash
- Make sure WEBHOOK_SECRET matches exactly in Railway and the Shortcut

**Tweet not posting:**
- Check that your Twitter App has Read and Write permissions
- Make sure Access Token was generated AFTER enabling Write permissions (you may need to regenerate it)

**Location shows wrong area:**
- The "Neighborhood" detail from Get Details of Locations sometimes returns empty
- Use "City" as a fallback in the Shortcut

---

## Tweet Examples

**Go Online:**
> 🚗 Just went online on Lyft!
> 📍 Starting in Downtown Atlanta
> 🎵 Playing: Knife Talk - Drake

**Hourly Update:**
> ⏱️ 2.5h online | Still rolling on Lyft
> 📍 Currently in Midtown
> 🎵 Nonstop - Drake

**Go Offline:**
> 🔴 Wrapped up for the day!
> ⏱️ 4.5h on the road
> 📍 Last area: Buckhead
> Thanks to everyone who rode with me 🙏
