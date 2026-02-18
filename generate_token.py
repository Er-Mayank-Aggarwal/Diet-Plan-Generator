import jwt

token = jwt.encode(
    {"email": "tesst@example.com"},
    "supersecretkey123",
    algorithm="HS256"
)

print(token)
