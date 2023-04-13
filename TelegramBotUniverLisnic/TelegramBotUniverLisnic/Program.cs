using Newtonsoft.Json;
using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using Telegram.Bot;
using Telegram.Bot.Types;

using Telegram.Bot.Types.ReplyMarkups;


namespace TelegramBotUniverLisnic
{
    class MainWeather
    {
        [JsonProperty("temp")]
        public double temp { get; set; }

        [JsonProperty("feels_like")]
        public double feels_like { get; set; }
    }


    class WeatherData
    {
        [JsonProperty("name")]
        public string Name { get; set; }
        [JsonProperty("main")]
        public MainWeather mainWeather { get; set; }
    }

    internal class Program
    {
        public const String WEATHER = "WEATHER";

        private static readonly HttpClient httpClient = new HttpClient();
        static void Main(string[] args)
        {
            var client = new TelegramBotClient("5963067989:AAHLfs3o9_APGlCD8DfVvSeX7BaUT1X4bys");
            client.StartReceiving(Update, Error);
            Console.ReadLine();
        }

        private static Task Error(ITelegramBotClient ex, Exception arg2, CancellationToken arg3)
        {
            Console.WriteLine($"Ошибка: {arg2.Message}");
            return null;
        }


        static async Task<WeatherData> handleWeatherReq(ITelegramBotClient botClient, long chatId)
        {

            var cityName = "Кишинев";

            var response = await httpClient.GetAsync($"https://api.openweathermap.org/data/2.5/weather?q={cityName}&units=metric&appid=a3993f31ef3974d66a2454e5c9bd9590"); // замените 'your-api-key' на ваш API ключ

            Debug.WriteLine(response + "response");

            if (response.IsSuccessStatusCode)
            {
                var json = await response.Content.ReadAsStringAsync();
                var pojo = JsonConvert.DeserializeObject<WeatherData>(json);
                var mainTemp = pojo.mainWeather.temp;
                var feels_like = pojo.mainWeather.feels_like;

                var clothes = "";

                if (mainTemp > 10)
                {
                    clothes = "Куртка Кофта и джинсы";
                }
                else if (mainTemp > 20)
                {
                    clothes = "ШОрты и футболка";
                }
                else
                {
                    clothes = "Шуба и сапоги";
                }

                var message = @"
                   Город: " + cityName + "\n" +
                   "Температура: " + mainTemp + " С" + "\n" +
                   "Ощущается как: " + feels_like + " С" + "\n" +
                   "Совет по одежде: " + clothes + "\n";


                await botClient.SendTextMessageAsync(
                chatId: chatId,
                text: message
                );

            }

            return null;

        }

        async static Task Update(ITelegramBotClient botClient, Update update, CancellationToken token)
        {

            var message = update.Message;

            InlineKeyboardMarkup inlineKeyboard = new InlineKeyboardMarkup(new[] {
                        new []
                        {
                            InlineKeyboardButton.WithCallbackData(text: "Узнать погоду", callbackData: WEATHER),

                        },

                    });


            Debug.WriteLine(message);

            if (update.CallbackQuery != null && update.CallbackQuery.Data == WEATHER)
            {
                Debug.WriteLine("IN WEATHER CONDITION");
                await Program.handleWeatherReq(botClient, update.CallbackQuery.Message.Chat.Id);
            }

            if (message != null && message.Text != null)
            {


                Message sentMessage = await botClient.SendTextMessageAsync(
                    chatId: message.Chat.Id,
                    text: "Выберите функцию",
                    replyMarkup: inlineKeyboard
                    );

                Debug.WriteLine(message + "message");




            }

            /*


            InlineKeyboardMarkup inlineKeyboard = new InlineKeyboardMarkup(new[]
{
// first row
new []
{
InlineKeyboardButton.WithCallbackData(text: "1.1", callbackData: "11"),
InlineKeyboardButton.WithCallbackData(text: "1.2", callbackData: "12"),
},
// second row
new []
{
InlineKeyboardButton.WithCallbackData(text: "2.1", callbackData: "21"),
InlineKeyboardButton.WithCallbackData(text: "2.2", callbackData: "22"),
},
});

            if (message != null && message.Text != null)
            {
                botClient.SendTextMessageAsync(
    chatId: message.Chat.Id,
    text: "A message with an inline keyboard markup",
    replyMarkup: inlineKeyboard);

                Console.WriteLine($"{message.Chat.FirstName} | {message.Text}");
                if (message.Text.ToLower().Contains("привет"))
                {
                    await botClient.SendTextMessageAsync(message.Chat.Id, "Рад приветствовать тебя!");
                    return;
                }
            }
            Debug.WriteLine(message + "ERROR");
            if (message.Photo != null)
            {
                {
                    await botClient.SendTextMessageAsync(message.Chat.Id, "Хорошая фотография, но лучше отправь документом, чтобы сохранить качество.");
                    return;
                }
            }



            if (message.Document != null)
            {
                {
                    await botClient.SendTextMessageAsync(message.Chat.Id, "Сейчас изменю формат файла на PDF");
                    var fileId = update.Message.Photo.Last().FileId;
                    var fileInfo = await botClient.GetFileAsync(fileId);
                    var filePath = fileInfo.FilePath;

                    string desinationFilePath = $@"{Environment.GetFolderPath(Environment.SpecialFolder.Desktop)}\{message.Document.FileName}";
                    await using FileStream fileStream = System.IO.File.OpenWrite(desinationFilePath);
                    await botClient.DownloadFileAsync(filePath, fileStream);
                    fileStream.Close();

                    Process.Start(@"C:\Users\lisan\Desktop\MovieStar.exe", $@"""{desinationFilePath} """);
                    await Task.Delay(1500);

                    await using Stream stream = System.IO.File.OpenRead(desinationFilePath);
                    await botClient.SendDocumentAsync(message.Chat.Id, new InputOnlineFile(stream, message.Document.FileName.Replace(".jpg", "edited")));
                    return;

                
            }
        }*/
        }

    }

}
