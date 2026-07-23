import razorpay

client = razorpay.Client(
    auth=("YOUR_RZP_TEST_KEY", "YOUR_RZP_TEST_SECRET")
)

try:
    order = client.order.create({
        "amount": 100,
        "currency": "INR",
        "payment_capture": 1,
    })
    print(order)
except Exception as e:
    print(type(e))
    print(e)