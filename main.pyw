import wx
import openai
import requests
import emoji

api_key = 'Your API'

blacklisted_countries = ['RU', 'BY']
class ChatFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="OpenAI Chat", size=(400, 500))
        
        self.panel = wx.Panel(self, style=wx.BORDER_THEME)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.ip_label = wx.StaticText(self.panel, label="Your IP Address: ")
        self.country_label = wx.StaticText(self.panel, label="Country: ")
        self.chat_history = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(380, 200))
        self.user_input = wx.TextCtrl(self.panel, size=(300, -1))
        self.generate_button = wx.Button(self.panel, label="Send")
        self.clear_button = wx.Button(self.panel, label="Clear Chat")

        self.generate_button.Bind(wx.EVT_BUTTON, self.on_generate)
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear)

        self.sizer.Add(self.ip_label, 0, wx.ALL | wx.EXPAND, 10)
        self.sizer.Add(self.country_label, 0, wx.ALL | wx.EXPAND, 10)
        self.sizer.Add(self.chat_history, 1, wx.ALL | wx.EXPAND, 10)
        self.sizer.Add(self.user_input, 0, wx.ALL | wx.EXPAND, 10)
        self.sizer.Add(self.generate_button, 0, wx.ALL | wx.CENTER, 10)
        self.sizer.Add(self.clear_button, 0, wx.ALL | wx.CENTER, 10)

        self.panel.SetSizer(self.sizer)
        self.statusbar = self.CreateStatusBar()
        self.messages = []

    def get_client_info(self):
        try:
            response = requests.get("https://ipinfo.io/json")
            data = response.json()
            ip = data.get("ip")
            country = data.get("country")
            return ip, country
        except Exception as e:
            return None, None

    def generate_response(self, user_input):
        user_ip, user_country = self.get_client_info()
        self.ip_label.SetLabel(f"Your IP Address: {user_ip}")
        self.country_label.SetLabel(f"Country: {user_country}")
      
        if user_country in blacklisted_countries:
            error_message = "Country not allowed."
            wx.MessageBox("Fatal request from OpenAI model: " + error_message, "API Error", wx.OK | wx.ICON_INFORMATION)
        else:
            user_message = {"role": "user", "content": user_input}
            self.messages.append(user_message)

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
                api_key=api_key,
            )
            bot_response = response["choices"][0]["message"]["content"]

            bot_message = {"role": "assistant", "content": bot_response}
            self.messages.append(bot_message)

            self.update_chat_history()

    def update_chat_history(self):
        self.chat_history.Clear()
        for message in self.messages:
            if message["role"] == "user":
                self.chat_history.AppendText(f"\n👱‍♂ You: {message['content']}\n")
            elif message["role"] == "assistant":
                self.chat_history.AppendText(f"\n🤖 Chatbot: {message['content']}\n")

    def on_generate(self, event):
        user_input = self.user_input.GetValue()
        if user_input:
            self.generate_response(user_input)
            self.user_input.Clear()

    def on_clear(self, event):
        self.messages = []
        self.chat_history.Clear()
        self.update_chat_history()

if __name__ == "__main__":
    app = wx.App(False)
    frame = ChatFrame()
    frame.Show()
    app.MainLoop()
