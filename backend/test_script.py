from app.schemas import UserCreate, NoteCreate, NoteUpdate
from pydantic import ValidationError

print("--- Test 1: valid user ---")
u = UserCreate(email="alice@example.com", password="supersecret")
print(u.model_dump())

print("\n--- Test 2: invalid email ---")
try:
    UserCreate(email="not-an-email", password="supersecret")
except ValidationError as e:
    print("REJECTED (good):", e.errors()[0]["msg"])

print("\n--- Test 3: password too short ---")
try:
    UserCreate(email="alice@example.com", password="abc")
except ValidationError as e:
    print("REJECTED (good):", e.errors()[0]["msg"])

print("\n--- Test 4: valid note with tags ---")
n = NoteCreate(title="Buy groceries", content="milk, eggs", tag_names=["personal", "todo"])
print(n.model_dump())

print("\n--- Test 5: note with empty title (should fail) ---")
try:
    NoteCreate(title="", content="x")
except ValidationError as e:
    print("REJECTED (good):", e.errors()[0]["msg"])

print("\n--- Test 6: partial update (PATCH semantics) ---")
patch = NoteUpdate(title="New title")
print("only-title patch:", patch.model_dump(exclude_unset=True))

print("\n--- Test 7: empty update ---")
patch2 = NoteUpdate()
print("empty patch:", patch2.model_dump(exclude_unset=True))

exit()
