# InvitePal
 A Python + MySQL Based Telegram Referral Bot

**InvitePal** is a Telegram bot designed to manage referral-based rewards, user balances, and seamless integration with Telegram groups or channels. It leverages the **Telegram Bot API**, a MySQL database for user data management, and Python for robust backend logic.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Commands Overview](#commands-overview)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- 🏆 **Reward System**: Earn points for each successful referral and redeem rewards.
- 🔗 **Personalized Referral Links**: Share your unique referral link.
- 📊 **Track Referrals and Balance**: Check your referral history and current point balance.
- 🎉 **Reward Redemption**: Redeem points for exciting rewards.
- 🔒 **Secure Database Integration**: Store and retrieve user and reward information in MySQL.
- 🎛️ **Admin Panel**: Easily configurable options and commands.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/esyhacks/InvitePal.git
   cd InvitePal
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database**:
   - Create a MySQL database and import the required schema.

5. **Configure Environment Variables**:
   Create a `.env` file in the project root and include:
   ```env
   BOT_TOKEN=<Your_Telegram_Bot_Token>
   BOT_USERNAME=<Your_Bot_Username>
   TARGET_CHANNEL=<@YourTargetChannel>
   DB_HOST=<YourDatabaseHost>
   DB_USER=<YourDatabaseUser>
   DB_PASSWORD=<YourDatabasePassword>
   DB_PORT=<YourDatabasePort>
   DB_NAME=<YourDatabaseName>
   STICKER_ID=<StickerID1>
   STICKER_ID_2=<StickerID2>
   STICKER_ID_3=<StickerID3>
   STICKER_ID_4=<StickerID4>
   STICKER_ID_5=<StickerID5>
   ```

6. **Run the Bot**:
   ```bash
   python refbot.py
   ```

---

## Configuration

Ensure that your bot is an admin in the target Telegram channel to verify memberships.

- **Database Schema**:
  - Table `Users`: Manages user details like `telegram_id`, `points_available`, and referral status.
  - Table `Rewards`: Tracks reward items, their availability, and redemption points.

---

## Usage

1. **Start the Bot**:
   - Users can type `/start` to begin interacting with the bot.

2. **Earn Points**:
   - Share your referral link with friends. Earn points when they join the target channel.

3. **Check Rewards**:
   - Use the menu or commands to view available rewards and your balance.

4. **Redeem Rewards**:
   - Redeem points for rewards using the `/redeem <item-id>` command.

---

## Commands Overview

| Command           | Description                                                |
|-------------------|------------------------------------------------------------|
| `/start`          | Begin interaction with the bot and check channel membership. |
| `/rewards`        | View available rewards.                                    |
| `/get_link`       | Retrieve your referral link.                               |
| `/referrals`      | View a list of your referred users.                        |
| `/balance`        | Check your current point balance.                          |
| `/redeem <id>`    | Redeem a reward by item ID.                                |
| `/help`           | Get detailed instructions on bot usage.                   |

---

## Contributing

We welcome contributions! Please fork the repository and submit a pull request with your proposed changes.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

Start sharing and earning rewards today with **InvitePal**! 🎉
