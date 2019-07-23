from slim import Slim

app = Slim()


@app.get("/")
def home_page():
    return "home page"


@app.route("/hello", methods=["get", "post"])
def hello():
    return "hello!"


if __name__ == '__main__':
    app.run()
