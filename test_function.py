"""
python 3.8
test lambda function
John Armitage 19/11/2019
"""


def my_handler(event, context):
    hello = "Hello World"

    return {
        'message': hello
    }