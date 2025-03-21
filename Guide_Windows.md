# 🪟 How to install
To use the HomeLab on Windows you need to follow these steps:

1. Install all files inside the `code/HomeLab` folder.
  
2. Install Python (I suggest `Python 3.11`)

3. Install all the requirements using the command:
   ```console
   pip install -r requirements.txt
   ```

4. Run the code with the command:
   ```console
   py main.py
   ```
   
5. Setup the `app_config.json` file in the `code/HomeLab` folder:

   - streamingcommunity_url (The current Streaming Community link)
   - discord_webhook (The Discord Webhook to which the site's local IP will be sent)
   - ESP32_integration (Set as `"True"` if you are using the ESP32 integration otherwise set as `"False"`)

6.  Set the `user.json` file in the `code/HomeLab` folder following the example in the file
   
<hr>

[Go back](README.md)
