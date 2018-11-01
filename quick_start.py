from slim.app import Slim, SlimModule

slim = Slim()


@slim.route("/")
def hello():
    return "hello"


@slim.route("/method_test", methods=["post"])
def method_test_post():
    return "method_test_post"


@slim.route("/method_test", methods=["delete"])
def method_test_delete():
    return "method_test_delete"


@slim.route("/argument_test")
def argument_test(name, age):
    return "name: {name}, age: {age}".format(name=name, age=age)


case = SlimModule(slim, module_url="case")


@case.module_route("/module_test")
def module_test():
    return "module_test"


sub_case = SlimModule(case, module_url="sub_case")


@sub_case.module_route("/sub_case_test")
def sub_case_test():
    return "sub_case_test"


if __name__ == '__main__':
    slim.run()
