if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()

    from Website import createApp  # Import your createApp function

    app = createApp()  # Create the Flask app instance
    app.run(host='0.0.0.0', port=5000 , debug=True)
