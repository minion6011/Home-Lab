# 🍓 How to install
To use the HomeLab on Raspbian you need to follow these steps:

1. Install all files inside the `code/HomeLab` folder.
  
2. Create a [virtual environment in Python](http://rptl.io/venv) in the folder where you placed the files.

3. Then install all the requirements using the command:
   ```console
   pip install -r requirements.txt
   ```

4. Run the code with the command:
   ```console
   python3 main.py
   ```

5. Setup the `app_config.json` file in the `code/HomeLab` folder:

   - streamingcommunity_url (The current Streaming Community link)
   - discord_webhook (The Discord Webhook to which the site's local IP will be sent)
   - ESP32_integration (Set as `"True"` if you are using the ESP32 integration otherwise set as `"False"`)

6. Set the `user.json` file in the `code/HomeLab` folder following the example in the file

7. Install Node.js from [here](https://nodejs.org/en/download)
<hr>

[Go back](README.md)
