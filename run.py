from server import create_app
# imports flask server and runs it
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)