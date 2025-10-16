from assistant import Assistant

def main():
    assistant = Assistant()
    # You can select the device by name or by an interactive prompt
    # assistant.set_input_device_by_name("your_mic_name")
    # assistant.select_input_device()
    assistant.listen_continuously()

if __name__ == "__main__":
    main()