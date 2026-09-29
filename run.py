from app import create_app

app = create_app()

if __name__ == "__main__":
    # Debug/reloader are OFF by default even locally — flip via FLASK_ENV=development
    # in your .env if you want auto-reload while developing.
    app.run(host="127.0.0.1", port=5000)
