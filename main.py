from assistant import Assistant

def main():
    assistant = Assistant()
    # You can select the device by name or by an interactive prompt
    # mic_name = assistant.select_input_device()
    # assistant.set_input_device_by_name(mic_name)
    assistant.listen_continuously()

if __name__ == "__main__":
    main()